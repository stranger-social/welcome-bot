from typing import List, Optional

from app import oauth2
from .. import models, schemas, utils, oauth2, welcome_bot
from fastapi import APIRouter, Body, FastAPI, HTTPException, Response, status, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db

import logging
logger = logging.getLogger(__name__)

# Bot controls for the welcome-bot
router = APIRouter(
    prefix="/bot",
    tags=['Bot Controls']
)
# Start the welcome-bot
@router.post("/start", status_code=status.HTTP_200_OK)
async def start_welcome_bot(
    background_tasks: BackgroundTasks,
    current_user: int = Depends(oauth2.get_current_user)
    ):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        background_tasks.add_task(welcome_bot.start_bot)
        logger.info("welcome-bot started")
        return {"message": "welcome-bot started"}
