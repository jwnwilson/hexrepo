FROM public.ecr.aws/lambda/python:3.12

# Install Poetry
ENV PATH="/root/.local/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python - && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* ${LAMBDA_TASK_ROOT}/
COPY ./libs /libs

# Allow installing dev dependencies to run tests
RUN poetry lock && poetry install --no-root

COPY ./projects/example/src ./src
COPY ./projects/example/alembic.ini ./

ENV PYTHONPATH ${LAMBDA_TASK_ROOT}/app
CMD ["src.app.interactor.api,fastapi.lambda.handler"]
