from app import oauth2
from .. import oauth2, welcome_bot
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks


import logging
logger = logging.getLogger(__name__)

# Bot controls for the welcome-bot
router = APIRouter(
    prefix="/bot",
    tags=['Bot Controls']
)

is_running = False

# Start the welcome-bot
@router.post("/start", status_code=status.HTTP_200_OK, description="Start the welcome-bot [bot does not run automatically on startup]")
async def start_welcome_bot(
    background_tasks: BackgroundTasks,
    current_user: int = Depends(oauth2.get_current_user)
    ):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User {str(current_user.username)} is not active.")
    else:
        global is_running
        if not is_running:
            background_tasks.add_task(welcome_bot.welcome_bot_main)
            logger.info("welcome-bot started")
            is_running = True
            return {"message": "welcome-bot started"}
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"welcome-bot is already running.")

