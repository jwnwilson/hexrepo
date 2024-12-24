FROM python:3.12-slim

ARG PROJECT
WORKDIR /code
ENV PYTHONPATH=/code/src

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh
# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

COPY ./projects/${PROJECT}/pyproject.toml ./projects/${PROJECT}/poetry.lock ./
COPY ./libs /libs

# RUN poetry self add keyrings.google-artifactregistry-auth
RUN uv sync --frozen --no-group dev

COPY ./projects/${PROJECT}/src ./src
COPY ./projects/${PROJECT}/alembic.ini ./
CMD ["uvicorn", "app.interactor.api.fastapi.main:app", "--host", "0.0.0.0", "--port", "8000"]

# TODO: Use poetry to build project into wheel so that final build image can be seperated from the preauth image