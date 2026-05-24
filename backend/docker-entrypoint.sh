#!/bin/sh
set -e

DB_PATH="${DATABASE_PATH:-database/pycefr.db}"
DB_DIR=$(dirname "$DB_PATH")

mkdir -p "$DB_DIR"

if [ ! -f "$DB_PATH" ]; then
  echo "Initializing database at $DB_PATH ..."
  sqlite3 "$DB_PATH" ".read backend/db/schema.sql"
  sqlite3 "$DB_PATH" ".read backend/db/initialize_db.sql"
  echo "Database initialized."
fi

exec "$@"
