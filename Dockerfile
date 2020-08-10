FROM python:slim
MAINTAINER Geppe Brillo
RUN mkdir -p /blablabla/logs /blablabla/bots
WORKDIR /blablabla
COPY . ./
RUN pip install -r dev-requirements.txt
RUN chown -R nobody: /blablabla
USER nobody
RUN echo '#!/bin/bash \nWORKDIR="/blablabla"\nexport BLABLABLA_LOGGING_CONF=${WORKDIR}/logging.dev.conf\nGUNICORN_CMD_ARGS="--bind=0.0.0.0:8000 --workers=1 --access-logfile ${WORKDIR}/logs/access.log --error-logfile ${WORKDIR}/logs/error.log" BLABLABLA_LOGGING_CONF="${WORKDIR}/logging.conf" gunicorn "api:from_config(\"config.toml\")"' > ./entrypoint.sh && chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
