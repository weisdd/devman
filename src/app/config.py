import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "oNJ7QzZjwmenrBYh")
    CACTI_MYSQL_HOST = os.environ.get("CACTI_MYSQL_HOST", "127.0.0.1")
    CACTI_MYSQL_UNIX_SOCKET = os.environ.get("CACTI_MYSQL_UNIX_SOCKET", "")
    CACTI_MYSQL_DB = os.environ.get("CACTI_MYSQL_DB", "cacti")
    CACTI_MYSQL_USER = os.environ.get("CACTI_MYSQL_USER", "root")
    CACTI_MYSQL_PASSWORD = os.environ.get("CACTI_MYSQL_PASSWORD", "")
    CACTI_URL = os.environ.get("CACTI_URL", "http://127.0.0.1:8002")
    NETBOX_URL = os.environ.get("NETBOX_URL", "http://127.0.0.1:8000")
    NETBOX_TOKEN = os.environ.get(
        "NETBOX_TOKEN", "0123456789abcdef0123456789abcdef01234567"
    )
    VERSION = os.environ.get("VERSION", "")
    ZABBIX_URL = os.environ.get("ZABBIX_URL", "http://127.0.0.1:8081")
    ZABBIX_USER = os.environ.get("ZABBIX_USER", "Admin")
    ZABBIX_PASSWORD = os.environ.get("ZABBIX_PASSWORD", "zabbix")


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
