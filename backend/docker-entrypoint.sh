#!/usr/bin/env bash
set -euo pipefail

# Extract PostgreSQL connection details from POSTGRES_DSN or use defaults
# DSN format: postgresql+asyncpg://user:password@host:port/database
if [[ -n "${POSTGRES_DSN:-}" ]]; then
  PG_HOST=$(echo "$POSTGRES_DSN" | sed -n 's/.*@\([^:/]*\).*/\1/p')
  PG_USER=$(echo "$POSTGRES_DSN" | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
  PG_PORT=$(echo "$POSTGRES_DSN" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
else
  PG_HOST="${POSTGRES_HOST:-postgres}"
  PG_USER="${POSTGRES_USER:-schemaintern}"
  PG_PORT="${POSTGRES_PORT:-5432}"
fi

echo "Waiting for PostgreSQL at $PG_HOST:$PG_PORT..."
until pg_isready -h "$PG_HOST" -p "${PG_PORT:-5432}" -U "$PG_USER" 2>/dev/null; do
  sleep 1
done
echo "PostgreSQL is ready."

echo "Running database migrations..."
alembic upgrade head
echo "Migrations complete."

exec "$@"
