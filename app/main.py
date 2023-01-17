from .config import settings

import sys
from fastapi import FastAPI, File
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, admin, post, bot, account

import logging

description = """
The welcome-bot is a Mastodon bot that welcomes new users to a Mastodon instance.
Use the API interface to add welcome messages to the database and start the bot. The bot will then automatically welcome new users to the instance. Checking the instance every 30 seconds for new users. 
"""

app = FastAPI(
    title="welcome-bot",
    description=description,
    version="0.2.1",
    contact={
        "name": "azcoigreach",
        "url": "https://strangerproduction.com",
        "email": "azcoigreach@strangerproduction.com",
    },
    docs_url="/docs", redoc_url=None,
)

origins = ["*"] # Configured for public API

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(bot.router)
app.include_router(post.router)
app.include_router(account.router)
app.include_router(admin.router)
app.include_router(auth.router)

# Set logging level to variable settings.logging_level
logging.basicConfig(level=settings.logging_level)
logger = logging.getLogger(__name__)

# Configure the logger
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))
logger.addHandler(handler)


@app.on_event("startup")
def setup_logging():
    pass

# Favicon
@app.get("/favicon.ico")
async def favicon():
    return File("/app/static/hoodie-small.png")

@app.get("/")
async def root():
    return {"message": "welcome-bot-app"}

