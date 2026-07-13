# Troubleshooting Guide

## Port Already in Use

**Error**: `Address already in use` or `port is already allocated`

**Solution**:
```bash
# Find the process using the port (replace <PORT> with 8100, 3000, etc.)
netstat -ano | grep :<PORT>
# Windows (PowerShell)
netstat -ano | findstr :<PORT>

# Kill the process (replace <PID>)
kill -9 <PID>
# Windows
taskkill /F /PID <PID>
```

Ports used by this project:
| Port | Service |
|------|---------|
| 8100 | Backend API |
| 8200 | Knowledge Engine API (internal) |
| 3000 | Frontend |
| 5432 | PostgreSQL |
| 6379 | Redis |
| 6333 | Qdrant HTTP |
| 6334 | Qdrant gRPC |
| 9090 | Prometheus |
| 3001 | Grafana |
| 4318 | OpenTelemetry Collector |

## Database Connection Refused

**Error**: `could not connect to server: Connection refused` or `sqlalchemy.exc.OperationalError`

**Solutions**:

1. **PostgreSQL not running**
   ```bash
   docker compose -f infra/docker/docker-compose.yml up -d postgres
   docker compose -f infra/docker/docker-compose.yml ps postgres
   ```

2. **Wrong credentials in `.env`**
   Ensure `POSTGRES_DSN` matches `docker-compose.yml`:
   ```
   POSTGRES_DSN=postgresql+asyncpg://schemaintern:schemaintern_dev@localhost:5432/schemaintern
   ```

3. **Database doesn't exist**
   ```bash
   docker exec -it schemaintern-postgres psql -U schemaintern -c "CREATE DATABASE schemaintern;"
   ```

4. **Connection pool exhausted**
   Restart the backend service. Increase pool size if persistent:
   ```
   POSTGRES_POOL_SIZE=20
   ```

## Redis Connection Refused

**Error**: `redis.exceptions.ConnectionError` or `Error 111 connecting to localhost:6379`

**Solutions**:

1. **Redis not running**
   ```bash
   docker compose -f infra/docker/docker-compose.yml up -d redis
   docker compose -f infra/docker/docker-compose.yml ps redis
   ```

2. **Wrong Redis URL in `.env`**
   ```
   REDIS_URL=redis://localhost:6379/0
   ```

3. **Redis container not healthy**
   ```bash
   docker logs schemaintern-redis
   ```

## Qdrant Connection Refused

**Error**: `qdrant_client.http.exceptions.UnexpectedResponse` or `Connection refused`

**Solutions**:

1. **Qdrant not running**
   ```bash
   docker compose -f infra/docker/docker-compose.yml up -d qdrant
   docker compose -f infra/docker/docker-compose.yml ps qdrant
   ```

2. **Wrong Qdrant configuration in `.env`**
   ```
   QDRANT_HOST=localhost
   QDRANT_PORT=6333
   ```

3. **Verify Qdrant is accessible**
   ```bash
   curl http://localhost:6333/collections
   ```

## Docker Issues

### Docker Daemon Not Running

**Error**: `Cannot connect to the Docker daemon`

**Solutions**:
- **Windows**: Start Docker Desktop from Start Menu
- **macOS**: Start Docker Desktop from Applications
- **Linux**: `sudo systemctl start docker`

### Docker Compose Version

**Error**: `unknown shorthand flag: 'f' in -f`

**Solution**: Use `docker compose` (v2) instead of `docker-compose` (v1):
```bash
docker compose -f infra/docker/docker-compose.yml up -d
```

### Container Exits Immediately

```bash
# Check logs
docker logs schemaintern-postgres

# Rebuild and restart
docker compose -f infra/docker/docker-compose.yml down
docker compose -f infra/docker/docker-compose.yml up -d
```

### Volume Permissions

**Error**: `Permission denied` on mounted volumes

**Solution**: Ensure volume directories exist and have correct permissions:
```bash
mkdir -p .docker/postgres .docker/redis .docker/qdrant
```

## uv / Python Issues

### uv Not Found

**Error**: `uv: command not found`

**Solution**: Install `uv`:
```bash
pip install uv
```

### Dependency Conflict

**Error**: `uv sync` fails with resolution error

**Solution**:
```bash
# Clear cache and retry
uv cache clean
uv sync --reinstall

# If still failing, update lockfile
uv lock --upgrade
uv sync
```

### Virtual Environment Issues

**Error**: Module not found despite `uv sync` succeeding

**Solution**:
```bash
# Ensure .venv is activated or use uv run
uv run python -c "import app"

# If .venv is corrupted, recreate
rm -rf backend/.venv
uv sync
```

## npm / pnpm Issues

### Package Not Found

**Error**: `npm ERR! 404 Not Found`

**Solution**:
```bash
# Clear npm cache
npm cache clean --force

# Reinstall
rm -rf frontend/node_modules frontend/package-lock.json
npm install
```

### Node Version Mismatch

**Error**: `You are running Node.js <version> but this project requires >=20`

**Solution**: Use `nvm` (Node Version Manager):
```bash
nvm install 20
nvm use 20
```

### ESLint / Prettier Configuration

**Error**: `ESLint: failed to load config` or `Prettier: No configuration found`

**Solution**:
```bash
# Regenerate node_modules
rm -rf frontend/node_modules
npm install
```

## Migration Issues

### Alembic Migration Fails

**Error**: `Target database is not up to date` or `Can't locate revision identified by`

**Solution**:
```bash
# Check current migration state
cd backend && uv run alembic current

# Check migration history
uv run alembic history

# Stamps to head
uv run alembic stamp head
uv run alembic upgrade head

# If all else fails, reset (DEVELOPMENT ONLY)
uv run alembic downgrade base
uv run alembic upgrade head
```

## CORS Issues

**Error**: `Access-Control-Allow-Origin` missing in browser

**Solution**: Ensure `CORS_ORIGINS` in `.env` includes your frontend URL:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:8100
```

## General

### Slow Backend Startup

Uvicorn with `--reload` watches many files. For faster startup:
```bash
cd backend && uv run uvicorn app.main:create_app --reload --reload-dir app --port 8100
```

### "Command not found" for make

- **Windows**: Install [GNU Make via Chocolatey](https://community.chocolatey.org/packages/make) or use Git Bash
- **macOS**: `xcode-select --install`
- **Linux**: `sudo apt install make` (Ubuntu/Debian) or `sudo dnf install make` (Fedora)

### Health Check Failing

```bash
# Direct check
curl http://localhost:8100/api/v1/health/live

# Check backend is running
docker ps | grep schemaintern-backend

# Check backend logs
cd backend && uv run -- logs/app.log
```

## Still Stuck?

1. Check the [Development Guide](development-guide.md) for setup instructions
2. Search existing GitHub issues
3. Ask in the team's communication channel
