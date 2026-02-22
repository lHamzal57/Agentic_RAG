from fastapi import FastAPI
from app.api.routers import files

app = FastAPI()

app.include_router(files.router)
