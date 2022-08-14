# Heavily inspired from Dockerfile, this one also install requirements_for_test.txt

FROM python:3.9-alpine

ENV PYTHONDONTWRITEBYTECODE 1

RUN apk add --no-cache bash docker build-base git gcc musl-dev postgresql-dev g++ make libffi-dev libmagic libcurl curl-dev && rm -rf /var/cache/apk/*

# update pip
RUN python -m pip install wheel

WORKDIR /app

COPY requirements.txt requirements_for_test.txt .

RUN pip3 install -r requirements_for_test.txt

COPY . /app

ENV PORT=6011

ARG GIT_SHA
ENV GIT_SHA ${GIT_SHA}

ENTRYPOINT ["./entrypoint.sh"]

CMD ["sh", "-c", "gunicorn -c gunicorn_config.py application"]
