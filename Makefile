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
	uv run ruff check .

ruff-format:
	uv run ruff format .

ruff-fix:
	uv run ruff check --fix .

ty-check:
	ty check src

lint: ruff-check ty-check

format: ruff-format

slim-build:
	@echo "Building dev image..."
	docker build -t url-shorter:dev --target dev .
	@echo "Minifying with DockerSlim..."
	docker run --rm \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(PWD):/workspace \
		dslim/slim build \
		--target url-shorter:dev \
		--expose 6749 \
		--http-probe=false \
		--continue-after=30 \
		--include-path '/opt/pysetup' \
		--include-path '/opt/app' \
		--include-exe 'python' \
		--include-exe 'uv' \
		--include-exe 'curl' \
		--include-exe 'vim' \
		--include-exe 'htop' \
		url-shorter:dev
	@echo "Tagging slim image..."
	-docker tag url-shorter.slim:latest url-shorter.slim:dev
	-docker tag url-shorter.slim:latest url-shorter:dev
	@echo "Done! Minified image: url-shorter.slim:dev (352MB vs 667MB original)"

slim-start: slim-build
	@echo "Starting with slim image..."
	$(DC) up -d

slim-script:
	@./scripts/slim-dev.sh
