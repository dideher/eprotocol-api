FROM python:3.11-slim-bullseye AS compile-image
ARG ENVIRONMENT=development
ARG DEBIAN_FRONTEND=noninteractive

RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
		build-essential \
		pkg-config \
		default-libmysqlclient-dev \
	; \
	rm -rf /var/lib/apt/lists/*

## virtualenv
ENV VIRTUAL_ENV=/opt/venv
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

## install requirements
RUN pip install --upgrade pip wheel pip-tools

COPY requirements.txt ./requirements.txt

## update requirements file with deployment requirement deps
RUN set -eux; \
    echo "" >> /requirements.txt ; \
    echo "gunicorn" >> /requirements.txt ; \
	echo "inotify" >> /requirements.txt ; \
    echo "mysqlclient" >> /requirements.txt

RUN pip install -r ./requirements.txt

FROM python:3.11-slim-bullseye AS runtime-image
ARG ENVIRONMENT=development

# partially inspired from https://github.com/tiangolo/meinheld-gunicorn-docker

## update alpine and install runtime deps
RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
        openssl \
        ca-certificates \
        default-mysql-client \
        nginx \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        vim \
	; \
	rm -rf /var/lib/apt/lists/*


## copy Python dependencies from build image
COPY --from=compile-image /opt/venv /opt/venv

## prepare nginx
# COPY nginx.conf /etc/nginx/sites-available/default
# RUN ln -sf /dev/stdout /var/log/nginx/access.log \
#     && ln -sf /dev/stderr /var/log/nginx/error.log

COPY ./dockerfiles/app/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./dockerfiles/app/start.sh /start.sh
RUN chmod +x /start.sh

COPY ./dockerfiles/app/gunicorn_conf.py /gunicorn_conf.py

COPY ./src /app
WORKDIR /app/


ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

# Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Meinheld
CMD ["/start.sh"]
