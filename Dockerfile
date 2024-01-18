ARG PYTHON_VERSION=3.6

FROM python:${PYTHON_VERSION} as base
ARG ENVIRONMENT=development
WORKDIR /app
COPY ./requirements/production.requirements.txt /app/production.requirements.txt
COPY ./requirements/${ENVIRONMENT}.requirements.txt /app/${ENVIRONMENT}.requirements.txt
COPY ./hyphen /app/hyphen
RUN pip install -r ${ENVIRONMENT}.requirements.txt
ENV PYTHONPATH=/app
