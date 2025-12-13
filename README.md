# URL Shortener

A link shortening service.

## What It Is

Key features:
- Redirects are fast (Redis cache, async processing)
- Click statistics (total clicks, last click time)
- Top 5 most popular links
- Codes are pre-generated, so creating a link takes microseconds

## How to Run

```bash
make start
```

The service will start at `http://localhost:9898`. API documentation will be available at `/docs` (standard FastAPI Swagger).

## What's Inside

- **FastAPI** — main framework
- **PostgreSQL** — stores links and statistics
- **Redis** — cache for fast redirects + pool of pre-generated codes
- **RabbitMQ** — queue for click processing (so redirects aren’t blocked)
- **TaskIQ** — background tasks (refilling code pool, batch processing clicks)

All details are in `/docs` after launch.

## How It Works

1. You create a link → get an 8-character code
2. Someone clicks → instant redirect (from cache), click is logged to queue
3. Background task collects clicks in batches and updates statistics
4. Codes are pre-generated in a pool, so you don’t wait during creation

## Useful Commands

- `make up` — start
- `make down` — stop
- `make logs` — view logs
- `make migrate` — run migrations
- `make shell` — open IPython shell

## Notes

- Code pool refills automatically (when less than 10% remains)
- Clicks are processed in batches every minute
- Link cache lives for 24 hours
- If the code pool is empty — codes are generated synchronously (but this is rare)

## Docker Image Optimization

This project uses [DockerSlim](https://github.com/slimtoolkit/slim) to minimize image size.

**Image sizes:**
- Original image: ~667 MB
- Minified image: ~391 MB (1.7x smaller)

**Automatic minification:**

1. **Auto on start (recommended):**
   ```bash
   make start-slim    # checks if minification is needed and runs it automatically
   ```

2. **Using an environment variable:**
   ```bash
   SLIM_BUILD=true make build    # automatically minifies during build
   ```

3. **Manually:**
   ```bash
   make slim-build    # minify the image
   make slim-start    # minify and run with slim image
   make auto-slim     # smart minification (only if needed)
   ```

**Note:** DockerSlim works only locally. In CI/CD, dev images are not minified.


**How it works:**
- `auto-slim` checks hash of `Dockerfile` and `pyproject.toml` — only minifies if they changed
- `start-slim` automatically minifies and starts with slim image
- Volumes (`./src:/opt/app`) still work for hot-reload

## TODO

- [ ] Delete expired URLs (cleanup task for expired links)
- [ ] Store clicks in ClickHouse with metadata (IP, user-agent, timestamp, etc.)
- [ ] Investigate RPS limits and optimize performance
- [x] Optimize Docker image size (DockerSlim)
- [ ] QR code generation for links
- [x] CI/CD pipeline setup (GitHub Actions)
- [ ] Add tests (unit + integration)
- [ ] User authentication, rate limits per user, personal links
