FROM python:3.14.7-slim-bookworm@sha256:998acd06f485adfd6890e3e15a4b542543e0cf22ff904310095da328a5e3e561

ENV PYTHONDONTWRITEBYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/sources/C/.venv \
    UV_CACHE_DIR=/validation/uv-cache
COPY sources /sources
COPY helpers /validation
COPY evidence /validation/evidence
COPY core.whl /validation/evidence/core.whl
COPY uv.tar.gz /validation/evidence/uv.tar.gz
RUN tar -xzf /validation/evidence/uv.tar.gz -C /opt
WORKDIR /sources/C
RUN /opt/uv-x86_64-unknown-linux-gnu/uv sync --locked --extra dev --no-python-downloads --python /usr/local/bin/python3.14
RUN /sources/C/.venv/bin/python -B /validation/remote.py qualify
