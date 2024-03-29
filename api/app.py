from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from api.routers import operations
from api.routers import fastbtc
from api.routers import stats

from api.models.base import InfoApi
from api.logger import log
from api.db import connect_and_init_db, close_db_connect

from pymongo.errors import ServerSelectionTimeoutError as MongoTimeout
from fastapi import Request
from fastapi.responses import JSONResponse

from .common import get_env_var


API_VERSION = '1.0.8'
API_TITLE = 'Stable Protocol v0 API'
API_DESCRIPTION = """
This is a requirement for [stable-protocol-interface](https://github.com/money-on-chain/stable-protocol-interface)
___
"""

tags_metadata = [{
    "name": "Webapp",
    "description": "Mainly used from the webapp"}]

tags_metadata += stats.tags_metadata

tags_metadata += [{
    "name": "Diagnosis",
    "description":
    "Related to _information_ and _health measurements_ of this _API_"}]

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    openapi_url="/openapi.json",
    docs_url="/",
    openapi_tags=tags_metadata
)

app.add_event_handler("startup", connect_and_init_db)
app.add_event_handler("shutdown", close_db_connect)

app.include_router(operations.router)
app.include_router(fastbtc.router)
app.include_router(stats.router)

@app.exception_handler(MongoTimeout)
async def db_error_exception_handler(request: Request,
                                     exc: MongoTimeout):
    return JSONResponse(
        status_code=503,
        content={"detail": "Cannot get DB access"},
    )    

BACKEND_CORS_ORIGINS = get_env_var("BACKEND_CORS_ORIGINS", list)
ALLOWED_HOSTS = get_env_var("ALLOWED_HOSTS", list)

if BACKEND_CORS_ORIGINS is not None:

   # Sets all CORS enabled origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if ALLOWED_HOSTS is not None:

    # Guards against HTTP Host Header attacks
    app.add_middleware(TrustedHostMiddleware,
                       allowed_hosts=[str(host) for host in ALLOWED_HOSTS])


log.info("Starting webservice API version: {0}".format(API_VERSION))


@app.get("/infoapi",
         response_description="Returns information about this api",
         response_model=InfoApi,
         tags=["Diagnosis"])
async def info_api():
    return {
        "title": API_TITLE,
        "description": API_DESCRIPTION,
        "version": API_VERSION
    }


@app.get("/ping", tags=["Diagnosis"])
async def ping():
    return "webAppAPI OK"
