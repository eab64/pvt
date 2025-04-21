#!/bin/bash

set -e
set -u

function create_user_and_database() {
	local database=$1
	echo "  Checking if database '$database' exists..."
	
	# Проверяем, существует ли база данных
	if psql -tAc "SELECT 1 FROM pg_database WHERE datname='$database'" | grep -q 1; then
		echo "  Database '$database' already exists, skipping."
	else
		echo "  Creating database '$database'..."
		psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
		    CREATE DATABASE $database;
		    GRANT ALL PRIVILEGES ON DATABASE $database TO $POSTGRES_USER;
EOSQL
		echo "  Database '$database' created."
	fi
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
	echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
	for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
		create_user_and_database $db
	done
	echo "Multiple databases created"
fi 