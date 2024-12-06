format:
	poetry run ruff format .
	poetry run ruff check . --fix

clean:
	docker-compose down
	docker volume rm dosac_local_postgres_data
	docker-compose up -d

migrations:
	poetry run python manage.py makemigrations
	poetry run python manage.py migrate

run:
	poetry run daphne -p 8080 dosac.asgi:application


worker:
	poetry run python manage.py qcluster


test:
	poetry run pytest --cov=core tests