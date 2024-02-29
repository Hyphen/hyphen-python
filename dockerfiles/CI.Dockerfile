ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION} as base
ARG ENVIRONMENT=development
WORKDIR /app
ENV TEST_ENVIRONMENT=CI
COPY ./requirements/production.requirements.txt /app/production.requirements.txt
COPY ./requirements/${ENVIRONMENT}.requirements.txt /app/${ENVIRONMENT}.requirements.txt
COPY ./prospector.yml /app/prospector.yml
COPY ./pytest.ini /app/pytest.ini
COPY ./tests /app/tests
COPY ./hyphen /app/hyphen
RUN pip install -r ${ENVIRONMENT}.requirements.txt
ENV PYTHONPATH=/app
WORKDIR /app