#!/bin/bash
set -e

# Run migrations only on the primary backend instance
if [ "${RUN_MIGRATIONS}" != "false" ]; then
    echo "Running database migrations..."
    alembic upgrade head
    echo "Seeding database..."
    python -m seed.seed_data
    echo "Indexing products to Elasticsearch..."
    python -m app.utils.index_products
fi

# If a command is passed, run it instead of default
if [ $# -gt 0 ]; then
    exec "$@"
else
    # Default command: run the FastAPI server
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
fi
