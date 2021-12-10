import pynetbox
from requests.exceptions import RequestException

import helpers  # noqa


def get_netbox_api(settings):
    nb = pynetbox.api(settings.netbox_url, token=settings.netbox_token, threading=True)
    return nb


def netbox_get_devices(settings, **kwargs):
    nb = get_netbox_api(settings)
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
    except (RequestException, pynetbox.core.query.RequestError) as e:
        error = helpers.wrap_exception(
            e,
            "Failed to retrieve data from netbox. Please, check logs for more details.",
        )
    return devices, error
