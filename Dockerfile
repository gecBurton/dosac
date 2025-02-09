
# poetry
FROM python:3.13-slim
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install --yes build-essential

RUN pip install poetry poetry-plugin-bundle

WORKDIR /src
COPY . .

RUN poetry install

ENV DJANGO_SETTINGS_MODULE='dosac.settings'
ENV PYTHONPATH "${PYTHONPATH}:/."

EXPOSE 8080

RUN chmod +x ./docker-entrypoint.sh

ENTRYPOINT [ "./docker-entrypoint.sh" ]
