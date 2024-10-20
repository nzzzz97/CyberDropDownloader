FROM python:3.12.7-bullseye as base

ARG DEV=false
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"


FROM base as builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

RUN pip install poetry==1.8.3

COPY pyproject.toml poetry.lock ./
RUN poetry add --group dev 'cyberdrop_dl'
RUN poetry install --with dev --no-root && rm -rf $POETRY_CACHE_DIR;

FROM python:3.12.7-bullseye as runtime

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY cyberdrop_dl /app


WORKDIR /app

#CMD ["/bin/cat", "/dev/null"]
#ENTRYPOINT ["python", "main.py"]
