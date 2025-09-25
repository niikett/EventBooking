import httpx
import asyncio

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# from app.core.limiter import limiter
from app.models import *
from app.schemas import *
from app.core import security
from app.core.config_db import get_db
from app.core.config import settings
from app.api.routes import auth, events, registrations, volunteers


app = FastAPI()



route_to_call = f"/" 
async def call_route():
    async with httpx.AsyncClient() as client:
        try:
            await client.get(route_to_call)
        except httpx.RequestError:
            pass
scheduler = BackgroundScheduler()
@app.on_event("startup")
async def startup_event():
    scheduler.add_job(
        func=lambda: asyncio.run(call_route()),
        trigger=IntervalTrigger(minutes=14),
        # id="call_route_job",
        # name="Call route every 15 minutes",
    )
    scheduler.start()
@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()


origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return "REMOVE ME LATER"


app.include_router(auth.router)
app.include_router(events.router)
app.include_router(registrations.router)
app.include_router(volunteers.router)
