#!/usr/bin/env python
import os
import sys
from glob import glob


def prepare_snmp_conf():
    base_path = os.path.abspath(os.path.dirname(__file__))
    mibs_path = f"{base_path}/mibs/*/"
    snmp_conf_path = "/etc/snmp/snmp.conf"

    with open(snmp_conf_path, "w", encoding="utf-8") as snmp_conf:
        print(f"Generating snmp.conf based on the content of {mibs_path}\n")
        snmp_conf.write("# This file was generated automatically\n")

        mibdirs = glob(mibs_path)
        if mibdirs:
            for count, path in enumerate(mibdirs, 1):
                line = f"mibdirs {path}\n" if count == 1 else f"mibdirs +{path}\n"
                snmp_conf.write(line)
        else:
            sys.exit(f"Could not find any nested directories in {mibs_path}\n")


def main():
    prepare_snmp_conf()


if __name__ == "__main__":
    main()
