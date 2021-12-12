#!/usr/bin/env python3
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from natsort import natsorted
from pydantic import BaseSettings

import ext_devices
import ext_go
import ext_netbox
import ext_zabbix


class Settings(BaseSettings):
    cacti_mysql_host: str = "127.0.0.1"
    cacti_mysql_unix_socket: str = ""
    cacti_mysql_db: str = "cacti"
    cacti_mysql_user: str = "root"
    cacti_mysql_password: str = ""
    cacti_url: str = "http://127.0.0.1:8002"
    debug: bool = False
    mock_snmp: bool = False
    netbox_url: str = "http://127.0.0.1:8001"
    netbox_token: str = "0123456789abcdef0123456789abcdef01234567"
    version: str = ""
    zabbix_url: str = "http://127.0.0.1:8081"
    zabbix_user: str = "Admin"
    zabbix_password: str = "zabbix"


settings = Settings()
app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def sort_interfaces(interfaces):
    return natsorted(interfaces)


templates.env.filters["natsort"] = sort_interfaces


@app.get("/")
async def index(request: Request):
    return RedirectResponse(request.url_for("devices"))


@app.get("/healthz")
async def healthz():
    # Just a trick to trigger NetBox caching
    ext_netbox.netbox_get_devices(settings)
    return {"status": "Healthy"}


@app.get("/devices", response_class=HTMLResponse)
async def devices(request: Request):
    devices_list, error = ext_netbox.netbox_get_devices(settings)
    return templates.TemplateResponse(
        "devices/index.html",
        {
            "request": request,
            "settings": settings,
            "error": error,
            "title": "Devices",
            "devices": devices_list,
        },
    )


@app.get("/devices/site/{site}")
async def devices_site(request: Request, site: str):
    devices_list, error = ext_netbox.netbox_get_devices(settings, site=site)

    return templates.TemplateResponse(
        "devices/index.html",
        {
            "request": request,
            "settings": settings,
            "error": error,
            "title": "Devices",
            "devices": devices_list,
        },
    )


@app.get("/devices/model/{model}")
async def devices_model(request: Request, model: str):
    devices_list, error = ext_netbox.netbox_get_devices(settings, model=model)

    return templates.TemplateResponse(
        "devices/index.html",
        {
            "request": request,
            "settings": settings,
            "error": error,
            "title": "Devices",
            "devices": devices_list,
        },
    )


@app.get("/devices/snmp/{ip}")
async def devices_ip(request: Request, ip: str):
    # Needed to distinguish an empty result and an invalid IP:
    # The empty result is fine
    if not ext_devices.check_ip(ip):
        raise HTTPException(status_code=404, detail="Page not found")
    snmp_data, error = await ext_devices.get_snmp_data(ip, settings)

    return templates.TemplateResponse(
        "devices/ip.html",
        {
            "request": request,
            "settings": settings,
            "error": error,
            "title": "{} - Devices".format(ip),
            "snmp": snmp_data,
        },
    )


@app.get("/go/cacti/{ip}", response_class=HTMLResponse)
async def go_cacti(request: Request, ip: str):
    url, error = ext_go.get_cacti_url(settings, ip)
    if error:
        return templates.TemplateResponse(
            "go/error.html",
            {
                "request": request,
                "settings": settings,
                "error": error,
                "title": "{} - Go - Cacti".format(ip),
            },
        )
    # IP is outside of the allowed range or MySQL errors occur
    if not url:
        raise HTTPException(status_code=404, detail="Page not found")

    return RedirectResponse(url)


@app.get("/go/zabbix/{ip}", response_class=HTMLResponse)
async def go_zabbix(request: Request, ip: str):
    url, error = ext_go.get_zabbix_url(settings, ip)
    if error:
        return templates.TemplateResponse(
            "go/error.html",
            {
                "request": request,
                "settings": settings,
                "error": error,
                "title": "{} - Go - Zabbix".format(ip),
            },
        )
    # IP is outside of the allowed range or can't retrieve data from zabbix
    if not url:
        raise HTTPException(status_code=404, detail="Page not found")

    return RedirectResponse(url)


@app.get("/scripts", response_class=HTMLResponse)
async def scripts(request: Request):
    items, error = ext_zabbix.dispatch_dict(names_only=True)
    return templates.TemplateResponse(
        "scripts/index.html",
        {
            "request": request,
            "settings": settings,
            "error": error,
            "title": "Scripts",
            "items": items,
        },
    )


@app.get("/scripts/{script}", response_class=HTMLResponse)
async def scripts_zabbix(request: Request, script: str):
    # In case the script is not known, result would be of type None
    if not (result := ext_zabbix.dispatch_dict(name=script, settings=settings)):
        raise HTTPException(status_code=404, detail="Page not found")

    (items, error) = result
    title = script.replace("_", " ").title()

    return templates.TemplateResponse(
        "scripts/zabbix/universal.html",
        {
            "request": request,
            "settings": settings,
            "error": error,
            "title": f"{title} - Scripts",
            "items": items,
        },
    )


if __name__ == "__main__":
    uvicorn.run("main:app")
