FROM python:3.12-slim

ARG CONTEXT=GCP
ENV CONTEXT ${CONTEXT}
WORKDIR /code
ENV PYTHONPATH=/code/src

RUN pip install poetry && \
    poetry config virtualenvs.create false

COPY ./projects/example/pyproject.toml ./projects/example/poetry.lock ./
COPY ./libs /libs

# RUN poetry self add keyrings.google-artifactregistry-auth
RUN poetry lock && poetry install --no-root

COPY ./projects/example/src ./src
COPY ./projects/example/alembic.ini ./
CMD ["uvicorn", "src.app.interactor.api.fastapi.main:app", "--host", "0.0.0.0", "--port", "8000"]

# TODO: Use poetry to build project into wheel so that final build image can be seperated from the preauth image