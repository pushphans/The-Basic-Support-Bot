from fastapi import FastAPI, APIRouter
from app.api.router import router

app = FastAPI()


app.include_router(router=router, prefix="/api/v1")
