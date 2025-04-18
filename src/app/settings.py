# REMOVE ME
import pydantic_settings
from granian.log import LogLevels
from sqlalchemy.engine.url import URL


class Settings(pydantic_settings.BaseSettings):
    service_name: str = "test-application"
    debug: bool = False
    log_level: LogLevels = LogLevels.info

    db_driver: str = "postgresql+asyncpg"
    db_host: str = "db"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "password"
    db_database: str = "postgres"

    app_port: int = 8000

    @property
    def db_dsn(self) -> URL:
        return URL.create(
            self.db_driver,
            self.db_user,
            self.db_password,
            self.db_host,
            self.db_port,
            self.db_database,
        )
# END REMOVE ME
