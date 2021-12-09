import pynetbox
from requests.exceptions import RequestException

import helpers  # noqa


def get_netbox_api(config):
    nb = pynetbox.api(
        config["NETBOX_URL"], token=config["NETBOX_TOKEN"], threading=True
    )
    return nb


def netbox_get_devices(config, **kwargs):
    nb = get_netbox_api(config)
    error = {}

    # TODO: Filter name verification through **custom_filter

    try:
        devices = []
        for device in nb.dcim.devices.filter(
            role=["switch", "router"], has_primary_ip=True, **kwargs
        ):
            devices.append(
                {
                    "name": device.name,
                    "tenant_name": device.tenant.name,
                    "site_name": device.site.name,
                    "site_slug": device.site.slug,
                    "device_type": device.device_type.display_name,
                    "model_slug": device.device_type.slug,
                    "serial": device.serial,
                    "ip": str(device.primary_ip4).split("/")[0],
                    "id": device.id,
                }
            )
    # TODO: test authentication failures (might belong to another exception)
    except (RequestException, pynetbox.core.query.RequestError) as e:
        error = helpers.wrap_exception(
            e,
            "Failed to retrieve data from netbox. Please, check logs for more details.",
        )
    return devices, error
