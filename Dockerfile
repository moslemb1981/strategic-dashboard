ARG PYTHON_VERSION=3.10-slim

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/
COPY . /code

ENV SECRET_KEY "CiVuCCp0QOLtQwXj0Ez2YJU2Szc27ZxG36L2h3EsfKsgG6LuhP"
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["python","manage.py","runserver","0.0.0.0:8000"]
