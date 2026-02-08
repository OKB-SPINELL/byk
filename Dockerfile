FROM python:3.14-alpine AS base
LABEL authors="andrija"

WORKDIR /app
COPY requirements.txt /app/requirements.txt

ENV PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"

RUN python -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

RUN addgroup -S app && adduser -S app -G app && \
    chown -R app:app /app

USER app:app

FROM base AS final

COPY byk-server /app

ENV DEBUG=false
ENV DJANGO_SETTINGS_MODULE=byk.settings_env

EXPOSE 8000
