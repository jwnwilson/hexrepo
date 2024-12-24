FROM public.ecr.aws/lambda/python:3.12

ARG PROJECT

# Install UV
ENV PATH="/root/.local/bin:$PATH"
# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh
# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Copy uv.lock* in case it doesn't exist in the repo
COPY ./libs /libs
COPY ./projects/${PROJECT}/pyproject.toml ./projects/${PROJECT}/uv.lock* ${LAMBDA_TASK_ROOT}/

# Allow installing dev dependencies to run tests
RUN uv sync --all-extras --frozen --no-group dev

COPY ./projects/${PROJECT}/src ./src
COPY ./projects/${PROJECT}/alembic.ini ./

ENV PYTHONPATH ${LAMBDA_TASK_ROOT}/src
CMD ["src.app.interactor.aws.lambda_api.handler"]
