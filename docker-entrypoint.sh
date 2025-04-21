#!/bin/bash
set -e

# Устанавливаем права выполнения на скрипт инициализации
echo "Setting execute permissions for init scripts..."
chmod +x /docker-entrypoint-initdb.d/docker-postgresql-multiple-databases.sh
echo "Permissions set successfully"

# Запускаем стандартный entrypoint PostgreSQL с дополнительными аргументами
echo "Starting PostgreSQL with standard entrypoint..."
exec /usr/local/bin/docker-entrypoint.sh postgres "$@" 