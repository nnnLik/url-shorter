DC = docker compose -f compose.dev.yml

start: build up

up:
	$(DC) up -d

down:
	$(DC) down

build:
	$(DC) build

logs:
	$(DC) logs -f

bash:
	$(DC) exec -it url-shorter-backend bash

shell:
	$(DC) exec -it url-shorter-backend bash -c "cd /opt/app/src && ipython"

migrate:
	$(DC) exec url-shorter-backend bash -c "cd /opt/app/src && alembic upgrade head"

migration:
	$(DC) exec url-shorter-backend bash -c "cd /opt/app/src && alembic revision --autogenerate -m '$(msg)'"

ruff-check:
	ruff check src

ruff-format:
	ruff format src

ruff-fix:
	ruff check --fix src

ty-check:
	ty check src

lint: ruff-check ty-check

format: ruff-format
