import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import pymysql.cursors  # noqa

import ext_devices  # noqa
import ext_zabbix  # noqa
import helpers  # noqa


def get_zabbix_url(config, ip):
    url = ""
    error = {}

    if ext_devices.check_ip(ip):
        hostid, error = ext_zabbix.get_hostid_by_ip(config, ip)
        if hostid:
            url = (
                f"{config['ZABBIX_URL']}/zabbix.php?action=latest.view"
                f"&filter_hostids[]={hostid}&filter_show_without_data=1"
                "&filter_set=1"
            )
        else:
            # if no matching device found in Zabbix
            url = config["ZABBIX_URL"]

    return url, error


def get_cacti_url(config, ip):
    url = ""
    error = {}

    if ext_devices.check_ip(ip):
        try:
            connection = pymysql.connect(
                host=config["CACTI_MYSQL_HOST"],
                unix_socket=config["CACTI_MYSQL_UNIX_SOCKET"],
                user=config["CACTI_MYSQL_USER"],
                password=config["CACTI_MYSQL_PASSWORD"],
                db=config["CACTI_MYSQL_DB"],
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
                        config["CACTI_URL"], hostid
                    )

                    sql = "SELECT `id` FROM `graph_tree_items` WHERE `host_id`=%s LIMIT 1"  # noqa
                    cursor.execute(sql, (hostid,))
                    result_graph_tree_items = cursor.fetchone()

                    if result_graph_tree_items:
                        tbranchid = result_graph_tree_items["id"]
                        url = (
                            f"{config['CACTI_URL']}/graph_view.php?action=tree"
                            f"&node=tbranch-{tbranchid}&host_id={hostid}"
                            "&site_id=-1&host_template_id=-1&hgd=&hyper=true"
                        )
        except pymysql.Error as e:
            error = helpers.wrap_exception(
                e,
                "Failed to retrieve data from MySQL. Please, check logs for more "
                "details.",
            )
        finally:
            connection.close()

    return url, error
