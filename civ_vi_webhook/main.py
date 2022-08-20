import json
from pathlib import Path

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from .api import action_endpoints, info_endpoints, turn_endpoints
from .models.db import mongo_setup
from .site import homepage

app = FastAPI(
    title="Eric's Civilization VI Play By Cloud and PYDT Webhook server",
    description="The server acts as an endpoint for PBC and PYDT JSON then sends it to the service you configure.",
    version="1.1.8"
)

BASE_DIR = Path(__file__).resolve().parent
static_files_directory = str(Path(BASE_DIR, 'static'))

app.mount('/static', StaticFiles(directory=static_files_directory), name='static')

app.include_router(turn_endpoints.router)
app.include_router(info_endpoints.router)
app.include_router(action_endpoints.router)
app.include_router(homepage.router)


@app.on_event("startup")
async def load_db():
    with open("creds.conf", "r") as creds:
        credentials = json.load(creds)
    await mongo_setup.init_db('civ_vi_webhook',
                              username=credentials.get("username"),
                              password=credentials.get("password"))
