ARG PYTHON_VERSION=python3.8-slim-2021-10-02

FROM tiangolo/uvicorn-gunicorn-fastapi:${PYTHON_VERSION}

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        libjson-perl \
        libsnmp-info-perl \
        libsmi2-common \
        snmp \
        procps \
        iproute2 \
        curl \
        && \
    rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*.list && \
    chmod g+w /etc/snmp/snmp.conf

COPY mibs/ /app/mibs

COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip --no-cache-dir && \
    pip install --no-cache-dir --upgrade -r /app/requirements.txt

RUN umask 002 && \
    mkdir -p /etc/snmp/ /app/snmp/ && \
    echo > /app/snmp/snmp.conf && \
    chmod g=u /app/snmp/snmp.conf && \
    ln -sf /app/snmp/snmp.conf /etc/snmp/snmp.conf

COPY ./app /app

# TODO: add user (group root)
# TODO: move these instructions?
ENV PORT=8000
STOPSIGNAL SIGTERM
EXPOSE 8000
HEALTHCHECK CMD ["curl", "-f", "http://127.0.0.1:8000/healthz"]
