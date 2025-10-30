FROM jupyter/minimal-notebook:python-3.11

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}
COPY python/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip uninstall -y torch torchvision torchaudio || true \
    && pip install --no-cache-dir --pre --extra-index-url https://download.pytorch.org/whl/nightly/cu124 torch torchvision torchaudio \
    && pip install --no-cache-dir -r /tmp/requirements.txt

ENV PYTHONPATH="/home/jovyan/work/python:${PYTHONPATH}"

WORKDIR /home/jovyan/work
