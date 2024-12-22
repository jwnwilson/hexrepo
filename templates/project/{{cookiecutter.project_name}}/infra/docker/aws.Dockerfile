FROM public.ecr.aws/lambda/python:3.12

# Install Poetry
ENV PATH="/root/.local/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python - && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./libs /libs
COPY ./projects/{{cookiecutter.project_slug}}/pyproject.toml ./projects/{{cookiecutter.project_slug}}/poetry.lock* ${LAMBDA_TASK_ROOT}/

# Allow installing dev dependencies to run tests
RUN poetry lock && poetry install --no-root --without dev

COPY ./projects/{{cookiecutter.project_slug}}/src ./src
COPY ./projects/{{cookiecutter.project_slug}}/alembic.ini ./

ENV PYTHONPATH ${LAMBDA_TASK_ROOT}/src
{% if cookiecutter.use_api == 'y' %}
CMD ["src.app.interactor.aws.lambda_api.handler"]
{% else %}
CMD ["src.app.interactor.event.aws.handler"]
{% endif %}
