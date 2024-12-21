FROM public.ecr.aws/lambda/python:3.12

# Install Poetry
ENV PATH="/root/.local/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python - && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./libs/src /libs/src
COPY ./projects/example/pyproject.toml ./projects/example/poetry.lock* ${LAMBDA_TASK_ROOT}/

# Allow installing dev dependencies to run tests
RUN poetry lock && poetry install --no-root

COPY ./projects/example/src ./src
COPY ./projects/example/alembic.ini ./

ENV PYTHONPATH ${LAMBDA_TASK_ROOT}/src
CMD ["src.app.interactor.event.aws.handler"]
