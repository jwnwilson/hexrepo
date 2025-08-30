FROM python:3.12-slim

ARG PROJECT
WORKDIR /code/project
ENV WORKERS=2
ENV PYTHONPATH=/code/project/src
EXPOSE 8000

# Download the latest installer
RUN apt update && apt install -y curl
ADD https://astral.sh/uv/install.sh /uv-installer.sh
# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

COPY ./projects/${PROJECT}/pyproject.toml ./projects/${PROJECT}/README.md ./projects/${PROJECT}/uv.lock ./
COPY ./libs /libs

RUN uv sync --frozen --no-group dev --compile-bytecode 
ENV PATH="/code/project/.venv/bin/:$PATH"

COPY ./projects/${PROJECT}/src ./src
COPY ./projects/${PROJECT}/env ./env

CMD ["sh", "-c", "gunicorn --forwarded-allow-ips=* --bind 0.0.0.0:8000 -w ${WORKERS} -k gevent main.wsgi:application"]

