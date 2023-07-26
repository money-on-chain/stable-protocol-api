from pydantic import BaseModel


class InfoApi(BaseModel):
    title: str
    description: str
    version: str

    class Config:
        json_schema_extra = {
            "example": {
                  "title": "Stable Protocol v0 API",
                  "description": "Stable Protocol v0 API",
                  "version": "1.0.0"
            }

        }
