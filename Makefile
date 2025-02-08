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


web:
	poetry run daphne -p 8080 dosac.asgi:application


worker:
	poetry run python manage.py qcluster


test:
	poetry run pytest --cov=core --cov-report term-missing --cov-fail-under=85 tests

databases:
	docker-compose up -d postgres minio


build:
	docker login rg.fr-par.scw.cloud/account-registry -u nologin --password-stdin <<< "$SCW_SECRET_KEY"
	docker buildx create --use --name multi-arch-builder || true
	docker buildx use multi-arch-builder
	docker buildx inspect --bootstrap
	docker buildx build --platform linux/amd64,linux/arm64 -t django-app:latest --push .
	docker tag django-app:latest rg.fr-par.scw.cloud/account-registry/django-app:latest
	docker push rg.fr-par.scw.cloud/account-registry/django-app:latest

