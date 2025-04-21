import os
os.environ["DB_DATABASE"] = "test_db"

import logging
import sys

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
import subprocess

# from app import ioc
from app.application import AppBuilder
from app.settings import Settings


logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("tests")


class TestSettings(Settings):
    db_database: str = "test_db"


logger.info(f"В начале conftest.py, Settings().db_database = {Settings().db_database}")


class TestAppBuilder(AppBuilder):

    def __init__(self):
        self.settings = TestSettings()
        logger.info(f"TestAppBuilder создан с настройками базы данных: {self.settings.db_database}")
        super().__init__()


_app_builder = None


@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    logger.info("Инициализация тестовой базы данных...")

    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        logger.info("Миграции успешно применены.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при применении миграций: {e}")
        pytest.fail("Ошибка при применении миграций к тестовой базе данных.")


@pytest.fixture
async def client():
    builder = AppBuilder()

    await builder.init_async_resources()

    async with AsyncClient(
        transport=ASGITransport(app=builder.app),  # type: ignore[arg-type]
        base_url="http://test",
    ) as test_client:
        yield test_client

    logger.info("Очистка ресурсов после теста...")
    await builder.tear_down()


@pytest.fixture
async def db_session():
    engine = create_async_engine(Settings().db_dsn)
    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.fixture(autouse=True)
async def clean_database(db_session):
    await _truncate_tables(db_session)

    yield

    await _truncate_tables(db_session)


async def _truncate_tables(session):
    try:
        result = await session.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename != 'alembic_version'"
        ))
        tables = [row[0] for row in result]

        if tables:
            await session.execute(text("SET session_replication_role = 'replica'"))

            for table in tables:
                await session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))

            await session.execute(text("SET session_replication_role = 'origin'"))

            await session.commit()
    except Exception as e:
        logger.error(f"Ошибка при очистке таблиц: {e}")
        await session.rollback()


@pytest.fixture(scope="session", autouse=True)
async def cleanup_resources():
    yield
    global _app_builder
    if _app_builder is not None:
        logger.info("Завершение тестов, очистка ресурсов...")
        await _app_builder.tear_down()
        _app_builder = None


#
# @pytest.fixture(autouse=True)
# async def _prepare_ioc_container() -> typing.AsyncIterator[None]:
#     engine = await ioc.IOCContainer.database_engine()
#     connection = await engine.connect()
#     transaction = await connection.begin()
#     await connection.begin_nested()
#     session = AsyncSession(connection, expire_on_commit=False, autoflush=False)
#     ioc.IOCContainer.session.override(session)
#
#     try:
#         yield
#     finally:
#         if connection.in_transaction():
#             await transaction.rollback()
#         await connection.close()
#
#         ioc.IOCContainer.reset_override()
#         await ioc.IOCContainer.tear_down()
