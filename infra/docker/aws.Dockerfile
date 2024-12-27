FROM public.ecr.aws/lambda/python:3.12

ARG PROJECT

# Install UV
ENV PATH="/root/.local/bin:$PATH"
RUN pip install uv

# Copy uv.lock* in case it doesn't exist in the repo
COPY ./libs /libs
COPY ./projects/${PROJECT}/pyproject.toml ./projects/${PROJECT}/uv.lock* ./projects/${PROJECT}/README.md ${LAMBDA_TASK_ROOT}/

# Allow installing dev dependencies to run tests
RUN uv export --group aws > requirements.txt && uv pip install -r requirements.txt --system

COPY ./projects/${PROJECT}/src ./src
COPY ./projects/${PROJECT}/alembic.ini ./

ENV PYTHONPATH ${LAMBDA_TASK_ROOT}/src
CMD ["src.app.interactor.aws.lambda_api.handler"]
