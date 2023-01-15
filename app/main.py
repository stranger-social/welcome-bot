import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, admin, post, bot
import logging

description = """
This is an API controller for the Mastodon welcome-bot.
"""

app = FastAPI(
    title="welcome-bot",
    description=description,
    version="0.1.0",
    contact={
        "email": "azcoigreach@gmail.com",
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
app.include_router(admin.router)
app.include_router(auth.router)


logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

@app.on_event("startup")
def setup_logging():
    # Configure the logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))
    logger.addHandler(handler)

@app.get("/")
async def root():
    return {"message": "welcome-bot-app"}

