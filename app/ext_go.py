import pymysql.cursors
from requests.exceptions import RequestException

import ext_devices
import ext_zabbix
import helpers


def get_zabbix_url(settings, ip):
    url = ""
    error = {}

    if ext_devices.valid_ip(ip):
        try:
            zapi = ext_zabbix.get_zapi(settings)
            call = {"filter": {"ip": ip}, "limit": "1"}

            result = zapi.hostinterface.get(**call)
            if result:
                hostid = result[0]["hostid"]
                url = (
                    f"{settings.zabbix_url}/zabbix.php?action=latest.view"
                    f"&filter_hostids[]={hostid}&filter_show_without_data=1"
                    "&filter_set=1"
                )
            else:
                # If an IP is correct and there's no error, then we should
                # at least return base URL
                url = settings.zabbix_url
        except RequestException as e:
            error = helpers.wrap_exception(
                e,
                "Failed to retrieve data from zabbix."
                " Please, check logs for more details.",
            )

    return url, error


def get_cacti_url(settings, ip):
    url = ""
    error = {}

    if ext_devices.valid_ip(ip):
        try:
            connection = pymysql.connect(
                host=settings.cacti_mysql_host,
                unix_socket=settings.cacti_mysql_unix_socket,
                user=settings.cacti_mysql_user,
                password=settings.cacti_mysql_password,
                db=settings.cacti_mysql_db,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
        except pymysql.Error as e:
            error = helpers.wrap_exception(
                e, "Failed to connect to MySQL. Please, check logs for more details."
            )
            return url, error

        # TODO: not clear yet, why the modules' documentation suggests to wrap it all
        # with try - __exit__ is implemented
        try:
            with connection.cursor() as cursor:
                # Find hostid by ip
                sql = "SELECT `id` FROM `host` WHERE `hostname`=%s LIMIT 1"
                cursor.execute(sql, (ip,))
                result_host = cursor.fetchone()
                if result_host:
                    hostid = result_host["id"]
                    # Just in case there's a host not added to the tree
                    url = "{}/graph_view.php?action=preview&host_id={}".format(
                        settings.cacti_url, hostid
                    )

                    sql = "SELECT `id` FROM `graph_tree_items` WHERE `host_id`=%s LIMIT 1"  # noqa
                    cursor.execute(sql, (hostid,))
                    result_graph_tree_items = cursor.fetchone()

                    if result_graph_tree_items:
                        tbranchid = result_graph_tree_items["id"]
                        url = (
                            f"{settings.cacti_url}/graph_view.php?action=tree"
                            f"&node=tbranch-{tbranchid}&host_id={hostid}"
                            "&site_id=-1&host_template_id=-1&hgd=&hyper=true"
                        )
                else:
                    # If an IP is correct and there's no error, then we should
                    # at least return base URL
                    url = settings.cacti_url
        except pymysql.Error as e:
            error = helpers.wrap_exception(
                e,
                "Failed to retrieve data from MySQL. Please, check logs for more "
                "details.",
            )
        finally:
            connection.close()

    return url, error
