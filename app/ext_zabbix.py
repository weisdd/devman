import re
from collections import OrderedDict

from pyzabbix import ZabbixAPI
from requests.exceptions import RequestException

import helpers


def get_zapi(settings):
    zapi = ZabbixAPI(settings.zabbix_url)
    zapi.login(settings.zabbix_user, settings.zabbix_password)
    return zapi


def get_maps_forgotten_elements(settings):
    error = {}
    result = {
        "description": (
            "It helps to find images that have a {HOST.IP} macros or an IP address "
            "in their map labels. - Those that someone had planned to convert to "
            "hosts, but forgot."
        ),
        "fields": OrderedDict(
            [("name", "Map Name"), ("number", "Number"), ("labels", "Labels")]
        ),
        "items": [],
    }

    try:
        zapi = get_zapi(settings)

        call = {"selectSelements": "extend", "sortfield": "name"}

        # Simplified regexp for IPv4 addresses
        ip_regexp = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")

        for sysmap in zapi.map.get(**call):
            # Retrieving only elementtype 4, which corresponds to images
            # on Zabbix maps
            images = [
                element
                for element in sysmap["selements"]
                if element["elementtype"] == "4"
            ]

            # We're looking for elements with a macros {HOST.IP}
            # (which will not be expanded for images)
            # and/or IP addresses in their labels
            forgotten_elements = [
                image["label"]
                for image in images
                if "{HOST.IP}" in image["label"] or ip_regexp.search(image["label"])
            ]

            result["items"].append(
                {
                    "name": sysmap["name"],
                    "number": len(forgotten_elements),
                    "labels": forgotten_elements,
                }
            )
    except RequestException as e:
        error = helpers.wrap_exception(
            e,
            "Failed to retrieve data from zabbix. Please, check logs for more details.",
        )

    return result, error


def get_maps_missing_hosts(settings):
    error = {}
    result = {
        "description": ("It helps to find hosts that haven't been added to any maps."),
        "fields": OrderedDict(
            [("name", "Name"), ("hostid", "HostID"), ("description", "Description")]
        ),
        "items": [],
    }

    try:
        zapi = get_zapi(settings)

        call = {
            "selectSelements": "extend",
        }

        # Here we'll store hosts that are added to at least one map.
        sysmap_hosts = []
        for sysmap in zapi.map.get(**call):
            # Retrieving only elementtype 0, which corresponds to hosts
            # on Zabbix maps.
            sysmap_hosts.extend(
                [
                    element
                    for element in sysmap["selements"]
                    if element["elementtype"] == "0"
                ]
            )

        # Here we'll store a unique set of sysmap hosts, might be useful
        # should we decide to play with sets.
        # As far as I'm concerned, it should always be one hostid per Zabbix host,
        # so it should be a safe assumption.
        sysmap_hosts_ids = {host["elements"][0]["hostid"] for host in sysmap_hosts}

        call = {"sortfield": "host"}

        # It's time to find out what we've missed. :)
        missing_hosts = [
            host
            for host in zapi.host.get(**call)
            if host["hostid"] not in sysmap_hosts_ids
        ]

        for host in missing_hosts:
            result["items"].append(
                {
                    "name": host["name"],
                    "hostid": host["hostid"],
                    "description": host["description"],
                }
            )
    except RequestException as e:
        error = helpers.wrap_exception(
            e,
            "Failed to retrieve data from zabbix. Please, check logs for more details.",
        )

    return result, error


def dispatch_dict(name="", settings="", names_only=False):
    error = {}
    routes = {
        "forgotten_elements": lambda: get_maps_forgotten_elements(settings),
        "missing_hosts": lambda: get_maps_missing_hosts(settings),
    }
    if names_only:
        return sorted(routes.keys()), error
    return routes.get(name, lambda: None)()
