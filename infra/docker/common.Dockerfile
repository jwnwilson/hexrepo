FROM python:3.12-alpine

ARG PROJECT
WORKDIR /code
ENV PYTHONPATH=/code/src

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh
# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

COPY ./projects/${PROJECT}/pyproject.toml ./projects/${PROJECT}/uv.lock ./
COPY ./libs /libs

RUN uv sync --frozen --no-group dev

COPY ./projects/${PROJECT}/src ./src
COPY ./projects/${PROJECT}/alembic.ini ./
CMD ["uvicorn", "app.interactor.api.fastapi.main:app", "--host", "0.0.0.0", "--port", "8000"]
