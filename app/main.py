from fastapi import FastAPI
from app.core.config import settings
from app.api.routers import files, query

app = FastAPI(title=settings.APP_NAME, debug=settings.APP_DEBUG)

app.include_router(files.router)
app.include_router(query.router)