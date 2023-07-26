from fastapi import FastAPI, Body, HTTPException, status, Query
from api.routers import operations

API_VERSION = '1.0.0'

app = FastAPI(
    title='Stable Protocol v0 API',
    version=API_VERSION,
    description='Stable Protocol v0 API',
    openapi_url="/openapi.json",
    docs_url="/",
)
app.include_router(operations.router)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
