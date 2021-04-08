RUN apt-get update && apt-get -y install curl unzip wget libhdf5-dev

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

RUN touch ~/.bashrc

RUN echo 'export PATH=$HOME/.poetry/bin:$PATH' >> ~/.bashrc

CMD source /root/.bashrc && poetry self update
