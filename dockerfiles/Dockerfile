ARG PYTHON_VERSION=3.6

FROM python:${PYTHON_VERSION} as base
ARG ENVIRONMENT=development
WORKDIR /app
COPY ./requirements/production.requirements.txt /app/production.requirements.txt
COPY ./requirements/${ENVIRONMENT}.requirements.txt /app/${ENVIRONMENT}.requirements.txt
COPY ./hyphen /app/hyphen
RUN pip install -r ${ENVIRONMENT}.requirements.txt
ENV PYTHONPATH=/app

FROM ubuntu:20.04 as github
ARG PARENT=/app
ARG ROOT=$PARENT/app
COPY ./utils ${ROOT}/utils
COPY ./.env ${ROOT}/.env
RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
RUN chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
RUN apt update && apt install gh -y
WORKDIR ${ROOT}
ENTRYPOINT ["/bin/bash","./utils/set_env_for_github_actions.sh"]