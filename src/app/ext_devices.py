import asyncio
import json
import os
import subprocess
from ipaddress import ip_address

from decouple import config as dconfig

import helpers


class DevManSNMPError(Exception):
    pass


async def get_snmp_data(ip):
    snmp_data = {}
    error = {}
    test_mode = dconfig("DEVMAN_TEST_MODE", default=False, cast=bool)

    if check_ip(ip):
        path = os.path.abspath(os.path.dirname(__file__))
        if test_mode:
            with open(
                f"{path}/tests/ext_devices/test.json", "r", encoding="utf-8",
            ) as f:
                snmp_data = json.load(f)
        else:
            devman_path = f"{path}/devman.pl"
            proc = await asyncio.create_subprocess_exec(
                devman_path,
                ip,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                error = helpers.wrap_exception(
                    DevManSNMPError(stderr.decode()),
                    "Failed to retrieve data via SNMP. Please, "
                    "check logs for more details.",
                )
                return snmp_data, error

            snmp_data = json.loads(stdout.decode())

    return snmp_data, error


def check_ip(ip):
    try:
        return ip_address(ip).is_private
    except ValueError:
        return False
