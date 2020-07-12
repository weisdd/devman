import os
import sys
from flask import Flask, abort, redirect, render_template, url_for
from natsort import natsorted

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import ext_devices  # noqa
import ext_go  # noqa
import ext_netbox  # noqa
import ext_zabbix  # noqa

app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
print(os.environ["APP_SETTINGS"])


@app.template_filter("natsort")
def sort_interfaces(interfaces):
    return natsorted(interfaces)


@app.route("/")
def index():
    return redirect(url_for("devices"))


@app.route("/devices")
def devices():
    return render_template(
        "devices/index.html",
        title="Devices",
        devices=ext_netbox.netbox_get_devices(app.config),
    )


@app.route("/devices/site/<site>")
def devices_site(site):
    return render_template(
        "devices/index.html",
        title="Devices",
        devices=ext_netbox.netbox_get_devices(app.config, site=site),
    )


@app.route("/devices/model/<model>")
def devices_model(model):
    return render_template(
        "devices/index.html",
        title="Devices",
        devices=ext_netbox.netbox_get_devices(app.config, model=model),
    )


@app.route("/devices/snmp/<ip>")
def devices_ip(ip):
    # Needed to distinguish an empty result and an invalid IP:
    # The empty result is fine
    if not ext_devices.check_ip(ip):
        abort(404)
    snmp_data = ext_devices.get_snmp_data(ip)
    return render_template(
        "devices/ip.html", title="{} - Devices".format(ip), snmp=snmp_data
    )


@app.route("/go/cacti/<ip>")
def go_cacti(ip):
    url = ext_go.get_cacti_url(app.config, ip)
    if not url:
        abort(404)
    return redirect(url)


@app.route("/go/zabbix/<ip>")
def go_zabbix(ip):
    url = ext_go.get_zabbix_url(app.config, ip)
    if not url:
        abort(404)
    return redirect(url)


@app.route("/healthz")
def healthz():
    # Just a trick to trigger NetBox caching
    ext_netbox.netbox_get_devices(app.config)
    return "UP"


@app.route("/scripts")
def scripts():
    items = ext_zabbix.dispatch_dict(names_only=True)
    return render_template("scripts/index.html", title="Scripts", items=items)


@app.route("/scripts/<name>")
def scripts_zabbix(name):
    items = ext_zabbix.dispatch_dict(name=name, config=app.config)
    title = name.replace("_", " ").title()
    # non-existent functions
    if not items:
        abort(404)
    return render_template(
        "scripts/zabbix/universal.html", title=f"{title} - Scripts", items=items,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
