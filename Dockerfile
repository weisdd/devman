ARG PYTHON_VERSION=3.9.9-slim

FROM python:${PYTHON_VERSION}

RUN apt-get update && \
    apt-get install --no-install-recommends -y libjson-perl libsnmp-info-perl libsmi2-common snmp nano apt-transport-https \
                       curl gnupg2 procps iproute2 && \
    curl -sL https://nginx.org/keys/nginx_signing.key | apt-key add - && \
    echo 'deb https://packages.nginx.org/unit/debian/ bullseye unit' > /etc/apt/sources.list.d/unit.list && \
    apt-get update && \
    apt-get install -y unit-python3.9 && \
    rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*.list

# A set of Python modules changes less often than code, thus better to run it first to save some time
COPY src/app/requirements.txt /devman/requirements.txt
RUN pip3 install --upgrade pip --no-cache-dir && \
    pip3 install --no-cache-dir -r /devman/requirements.txt

COPY mibs/ /devman/mibs
COPY src/ /devman/

# Configure snmp and nginx unit; forward logs to docker log collector
RUN mkdir -p /etc/snmp/ && \
    echo > /devman/snmp.conf && \
    chmod g=u /devman/snmp.conf && \
    ln -sf /devman/snmp.conf /etc/snmp/snmp.conf && \
    mkdir /docker-entrypoint.d && \
    ln -f /devman/nginx-unit.json /docker-entrypoint.d/nginx-unit.json && \
    ln -sf /dev/stdout /var/log/unit.log

STOPSIGNAL SIGTERM

ENV LANG=C.UTF-8 \
    APP_SETTINGS="config.ProductionConfig" \
    CACTI_MYSQL_HOST=mysql \
    CACTI_MYSQL_DB=cacti \
    CACTI_MYSQL_USER=root \
    CACTI_MYSQL_PASSWORD="" \
    NETBOX_URL=http://netbox \
    NETBOX_TOKEN=0123456789abcdef0123456789abcdef01234567 \
    SNMP_COMMUNITY=public \
    ZABBIX_URL=http://zabbix \
    ZABBIX_USER=Admin \
    ZABBIX_PASSWORD=zabbix

EXPOSE 8000

HEALTHCHECK CMD ["curl", "-f", "http://127.0.0.1:8000/healthz"]

ENTRYPOINT ["/devman/docker-entrypoint.sh"]

CMD ["unitd", "--no-daemon", "--control", "unix:/var/run/control.unit.sock"]
