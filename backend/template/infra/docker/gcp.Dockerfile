FROM python:3.12 as pre_auth

ARG CONTEXT=GCP
ENV CONTEXT ${CONTEXT}
WORKDIR /code
ENV PYTHONPATH=/code/src

RUN pip install poetry && \
    poetry config virtualenvs.create false

    COPY ./pyproject.toml ./poetry.lock ./

# Copy poetry.lock so dependencies only get rebuilt if they are changed
# Creds file as wildcard to not fail if not present
# COPY ./pyproject.toml ./poetry.lock ./creds.json* ./

# # Downloading gcloud package
# RUN if [ "$CONTEXT" = "local" ]; then curl https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz > /tmp/google-cloud-sdk.tar.gz; fi

# # Installing the package
# RUN if [ "$CONTEXT" = "local" ]; then mkdir -p /usr/local/gcloud \
#   && tar -C /usr/local/gcloud -xvf /tmp/google-cloud-sdk.tar.gz \
#   && /usr/local/gcloud/google-cloud-sdk/install.sh; fi

# ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin
# RUN if [ "$CONTEXT" = "local" ]; then gcloud auth activate-service-account --key-file=creds.json && rm creds.json; fi

# RUN poetry self add keyrings.google-artifactregistry-auth
RUN poetry install --no-root

FROM pre_auth as build

COPY ./src ./src
COPY ./alembic.ini ./
CMD ["uvicorn", "src.app.interactor.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# TODO: Use poetry to build project into wheel so that final build image can be seperated from the preauth image