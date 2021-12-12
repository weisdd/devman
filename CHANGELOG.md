# CHANGELOG

## 0.2.0

- Added proper error handling for netbox, mysql, zabbix, devman.pl. It's also possible to print extended details while running in debug mode;
- Changed snmp.conf path;
- Deprecated Makefile;
- Moved from Flask to FastAPI;
- Moved from Nginx Unit to gunicorn;
- Moved to async call for devman.pl (so it doesn't block the app now);
- Moved to async handlers;
- Moved to non-root user;
- Moved to python 3.8;
- Updated all python depdendencies.

## 0.1.20

- Moved to `3.7.10-slim`.

## 0.1.19

- Bumped python base image (to `3.7.10`) and dependencies.

## 0.1.18

- Moved to python-decouple.

## 0.1.17

- Added Makefile;
- Updated dependencies:
  - python: 3.7.7 -> 3.7.9;
  - pymysql: 0.9.3 -> 0.10.1;
  - pynetbox: 5.0.3 -> 5.1.0.
