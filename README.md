# Cortex

## Local Docker setup (Postgres, Qdrant, Neo4j) ✅

This project can run all external dependencies locally via Docker Compose for development and testing.

Quick start:

1. Make sure Docker and Docker Compose are installed and running.
2. Verify `.env` is configured for local services (defaults point to `postgres`, `qdrant`, and `neo4j` services).
3. Start the stack:

   ```bash
   docker compose up -d
   ```

4. Check connectivity:
   - Postgres: `psql -h localhost -U postgres -d cortex_db` (password `postgres`)
   - Qdrant HTTP API: `http://localhost:6333` (no API key by default)
   - Neo4j Browser: `http://localhost:7474` (user `neo4j`, pass `neo4j`)
   - You can also run the repository health checks (scripts are now under `backend/scripts`):
     ```bash
     python backend/scripts/check_postgres.py
     python backend/scripts/check_qdrant.py
     python backend/scripts/check_neo4j.py
     ```

Notes:
- If you change any credentials, update both `.env` and the corresponding service environment variables in `docker-compose.yml`.
- Volumes `postgres_data`, `qdrant_data`, and `neo4j_data` persist local data between restarts.
