build:
	docker build -t service:latest .

virus_build:
	docker build -t virus:latest virus
up_tp:
	docker compose -f docker-compose.tp.yml up -d

up:
	docker compose up -d

down_tp:
	docker compose -f docker-compose.tp.yml down

down:
	docker compose down

client:
	docker run --env-file .env --rm -it service:latest python run_api_client.py

lint:
	black --check -l 120 app virus tests
	isort --check --line-length 120 .
	pylint --rcfile conf/.pylintrc app virus
	mypy --strict ${PWD}/app

fix:
	black -l 120 app virus tests
	isort --line-length 120 .
	pylint --rcfile conf/.pylintrc app virus
	mypy --strict ${PWD}/app

tdb:
	docker run -p "5431:5432" --rm -e POSTGRES_PASSWORD=postgres --name test_db postgres:16.3

test:
	pytest --cov=app