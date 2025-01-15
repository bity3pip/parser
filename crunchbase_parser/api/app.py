from fastapi import FastAPI
from api.routers.parser import router as parser_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(router=parser_router, prefix="/parser")

MEDIA_ROOT = "/crunchbase_parser/shared_storage"
app.mount("/media", StaticFiles(directory=MEDIA_ROOT, html=False), name="media")