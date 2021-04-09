# [Choice] Python version: 3, 3.9, 3.8, 3.7, 3.6
ARG VARIANT=3.8
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

# [Option] Install Node.js
ARG INSTALL_NODE="true"
ARG NODE_VERSION="lts/*"
RUN if [ "${INSTALL_NODE}" = "true" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

RUN apt-get update && apt-get -y install curl unzip wget libhdf5-dev

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

RUN touch ~/.bashrc

RUN echo 'export PATH=$HOME/.poetry/bin:$PATH' >> ~/.bashrc

CMD source /root/.bashrc && poetry self update
