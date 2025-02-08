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
	docker login rg.nl-ams.scw.cloud/docker-registry -u nologin --password-stdin <<< "$SCW_SECRET_KEY"
	docker tag local-image:tagname rg.nl-ams.scw.cloud/docker-registry/imagename:latest
	docker push rg.nl-ams.scw.cloud/docker-registry/imagename:latest