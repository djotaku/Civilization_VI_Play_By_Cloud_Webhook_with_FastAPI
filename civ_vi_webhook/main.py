from fastapi import FastAPI

from . import api_logger
from .api import turn_endpoints, info_endpoints, action_endpoints

app = FastAPI(
    title="Eric's Civilization VI Play By Cloud and PYDT Webhook server",
    description="The server acts as an endpoint for PBC and PYDT JSON then sends it to the service you configure.",
    version="0.3.1"
)

app.include_router(turn_endpoints.router)
app.include_router(info_endpoints.router)
app.include_router(action_endpoints.router)


