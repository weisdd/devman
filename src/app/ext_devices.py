import json
import os
import subprocess
from ipaddress import ip_address


def get_snmp_data(ip):
    snmp_data = {}
    test_mode = os.getenv("DEVMAN_TEST_MODE", False)

    if check_ip(ip):
        path = os.path.abspath(os.path.dirname(__file__))
        if test_mode:
            with open(
                f"{path}/tests/ext_devices/test.json", "r", encoding="utf-8",
            ) as f:
                snmp_data = json.load(f)
        else:
            devman_path = f"{path}/devman.pl"
            command_result = subprocess.run(
                [devman_path, ip],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                encoding="utf-8",
            )
            if not command_result.returncode:
                snmp_data = json.loads(command_result.stdout)

    return snmp_data


def check_ip(ip):
    try:
        return ip_address(ip).is_private
    except ValueError:
        return False
