ARG BASE_CONTAINER=ucsdets/datahub-base-notebook:2021.2-stable

FROM $BASE_CONTAINER

USER root

RUN echo 'jupyter notebook "$@"' > /run_jupyter.sh && chmod 755 /run_jupyter.sh

RUN apt-get update 

USER jovyan

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
