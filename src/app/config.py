import os
from decouple import config as dconfig

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = dconfig("SECRET_KEY", default="oNJ7QzZjwmenrBYh")
    CACTI_MYSQL_HOST = dconfig("CACTI_MYSQL_HOST", default="127.0.0.1")
    CACTI_MYSQL_UNIX_SOCKET = dconfig("CACTI_MYSQL_UNIX_SOCKET", default="")
    CACTI_MYSQL_DB = dconfig("CACTI_MYSQL_DB", default="cacti")
    CACTI_MYSQL_USER = dconfig("CACTI_MYSQL_USER", default="root")
    CACTI_MYSQL_PASSWORD = dconfig("CACTI_MYSQL_PASSWORD", default="")
    CACTI_URL = dconfig("CACTI_URL", default="http://127.0.0.1:8002")
    NETBOX_URL = dconfig("NETBOX_URL", default="http://127.0.0.1:8000")
    NETBOX_TOKEN = dconfig(
        "NETBOX_TOKEN", default="0123456789abcdef0123456789abcdef01234567"
    )
    VERSION = dconfig("VERSION", default="")
    ZABBIX_URL = dconfig("ZABBIX_URL", default="http://127.0.0.1:8081")
    ZABBIX_USER = dconfig("ZABBIX_USER", default="Admin")
    ZABBIX_PASSWORD = dconfig("ZABBIX_PASSWORD", default="zabbix")


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
