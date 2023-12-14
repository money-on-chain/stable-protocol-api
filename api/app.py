from os import getenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from api.routers import operations
from api.routers import fastbtc
from api.routers import stats
from api.models.base import InfoApi
from api.logger import log


API_VERSION = '1.0.3'
API_TITLE = 'Stable Protocol v0 API'
API_DESCRIPTION = 'Stable Protocol v0 API'

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    openapi_url="/openapi.json",
    docs_url="/",
)
app.include_router(operations.router)
app.include_router(fastbtc.router)
app.include_router(stats.router)

# # Sets all CORS enabled origins
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[str(origin) for origin in getenv("BACKEND_CORS_ORIGINS", default=["*"])],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Guards against HTTP Host Header attacks
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=getenv("ALLOWED_HOSTS", default=["*"]))

log.info("Starting webservice API version: {0}".format(API_VERSION))


@app.get("/infoapi",
         response_description="Returns information about this api",
         response_model=InfoApi)
async def info_api():
    return {
        "title": API_TITLE,
        "description": API_DESCRIPTION,
        "version": API_VERSION
    }


@app.get("/ping")
async def ping():
    return "webAppAPI OK"
