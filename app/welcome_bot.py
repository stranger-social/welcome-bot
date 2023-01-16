from .config import settings
import os
import asyncio
from datetime import datetime
import json
from fastapi import Depends
import aiohttp
from .database import get_db, get_db_
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from sqlalchemy.sql import insert
from sqlalchemy.sql import update

from . import models, schemas
import logging

logger = logging.getLogger(__name__)

'''
Wait for new users to register on the Mastodon instance and add them to the database
send all the new users the welcome messages stored in the database
'''

# Check if Quiet mode is enabled
# Quiet mode prevents messages from being sent to the Mastodon instance
def quiet_mode():
    if settings.quiet == True:
        logger.warning("Quiet mode is enabled")
        return True
    else:
        return False

# Check if the mastodon acct is in the database and add it if it's not
async def add_mastodon_acct(acct: schemas.MastodonUserCreate):
    with get_db() as db:
        # Check if the acct is in the database
        new_acct=models.MastodonAccts(acct=acct)
        try:
            db.add(new_acct)
            db.commit()
            db.refresh(new_acct)
            logger.debug(f"Added {acct} to the database")
        except Exception as e:
            logger.error(f"add_mastodon_acct | Exception occured: {e}")
            pass

# Monitor server notifications for new users
async def stream_notifications():
    # Use the base URL and the endpoint: GET /api/v1/streaming/user/notification HTTP/1.1
    # https://docs.joinmastodon.org/methods/streaming/#notification
    # use aiohttp to make the request
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{settings.mastodon_base_url}/api/v1/notifications", headers={"Authorization": f"Bearer {settings.mastodon_access_token}"}) as response:
            if response.status == 200:
                logger.debug(f"Response status: {response.status}")
                # Read the response as JSON
                data = await response.json()
                # Check if the response is a list
                if isinstance(data, list):
                    # Interate over the list and find the type: admin.sign_up
                    for item in data:
                        if item["type"] == "admin.sign_up":
                            # Get the user's acct
                            acct = item["account"]["acct"]
                            logger.debug(f"New user: {acct}")
                            # Add the user's acct to the database
                            await add_mastodon_acct(acct)
                            # Clear the notifications
                            item_id = item["id"]
                            logger.debug(f"item_id:{item_id}")
                            async with session.post(f"{settings.mastodon_base_url}/api/v1/notifications/{item_id}/dismiss", headers={"Authorization": f"Bearer {settings.mastodon_access_token}"}) as response:
                                if response.status == 200:
                                    logger.debug(f"Response status: {response.status}")
                                    logger.debug(f"Notifications cleared")
                                else:
                                    logger.warning(f"Response status: {response.status}")
                                    logger.warning(f"Response content: {await response.text()}")
            else:
                # Log response status
                logger.warning(f"Response status: {response.status}")
                # Log response content
                logger.warning(f"Response content: {await response.text()}")
                return False


# Check post_id sent to mastodon_acct_id in the database
# Return True if the post_id is in the database
async def check_post_id_as_sent(post_id: int, mastodon_acct_id: int):
    with get_db() as db:
        # Check if the post_id has already been sent to the acct using models.PostSent
        try:
            # Check if the post_id has already been sent to the acct
            post_sent = db.query(models.PostSent).filter(models.PostSent.post_id == post_id, models.PostSent.mastodon_acct_id == mastodon_acct_id).first()
            if post_sent:
                logger.debug(f"Post {post_id} has already been sent to {mastodon_acct_id}")
                return True
            else:
                logger.debug(f"Post {post_id} has not been sent to {mastodon_acct_id}")
                return False
        except Exception as e:
            logger.error(f"check_post_id_as_sent | Exception occured: {e}")
            return False 
            
# Mark post_id sent to mastodon_acct_id to the database
# Return True if the post_id is in the database
async def mark_post_id_as_sent(post_id: int, mastodon_acct_id: int):
    with get_db() as db:
        # Check if the post_id has already been sent to the acct using models.PostSent
        try:
            # Check if the post_id has already been sent to the acct
            post_sent = db.query(models.PostSent).filter(models.PostSent.post_id == post_id, models.PostSent.mastodon_acct_id == mastodon_acct_id).first()
            if post_sent:
                logger.debug(f"Post {post_id} has already been sent to {mastodon_acct_id}")
                return True
            else:
                logger.debug(f"Post {post_id} has not been sent to {mastodon_acct_id}")
                # Add the post_id to the database
                new_post_sent=models.PostSent(post_id=post_id, mastodon_acct_id=mastodon_acct_id)
                db.add(new_post_sent)
                db.commit()
                db.refresh(new_post_sent)
                logger.debug(f"Marked post {post_id} to {mastodon_acct_id} as sent")
                return True
        except Exception as e:
            logger.error(f"mark_post_id_as_sent | Exception occured: {e}")
            return False 


# Check if the acct has already been welcomed
# If the acct has already been welcomed, don't send the welcome message
# If the acct has not been welcomed, send the welcome message
# Return True if the acct has been welcomed
async def check_welcomed(acct: schemas.MastodonUserCreate):
    with get_db() as db:
        # Check if the acct has already been welcomed
        try:
            # Check if the acct has already been welcomed
            acct_welcomed = db.query(models.MastodonAccts).filter(models.MastodonAccts.acct == acct).first()
            if acct_welcomed.welcomed:
                logger.debug(f"{acct.acct} has already been welcomed")
                return True
            else:
                logger.debug(f"{acct.acct} has not been welcomed")
                return False
        except Exception as e:
            logger.error(f"check_welcomed | Exception occured: {e}")
            return False

# mark acct as welcomed
async def mark_acct_as_welcomed(acct: schemas.MastodonUserCreate):
    with get_db() as db:
        # Check if the acct is in the database
        try:
            # Mark acct as welcomed and add the datetime to welcomed_at
            db.query(models.MastodonAccts).filter(models.MastodonAccts.acct == acct).update({models.MastodonAccts.welcomed: True, models.MastodonAccts.welcomed_at: datetime.now()})
            # db.query(models.MastodonAccts).filter(models.MastodonAccts.acct == acct).update({models.MastodonAccts.welcomed: True})
            db.commit()
            logger.info(f"Marked {acct} as welcomed")
        except Exception as e:
            logger.error(f"mark_acct_as_welcomed | Exception occured: {e}")
            pass

# Read the welcome messages from the database that are marked as published
async def read_welcome_messages():
    with get_db() as db:
        # Check if the acct is in the database
        try:
            # Read the welcome messages from the database
            welcome_messages = db.query(models.Post).filter(models.Post.published == True).all()
            logger.info(f"Read {len(welcome_messages)} welcome messages from the database")
            return welcome_messages
        except Exception as e:
            logger.error(f"read_welcome_messages | Exception occured: {e}")
            pass
# Create list of welcome messages that can be sent
# Use models.Post.published to determine if the post should be sent
# Check against models.PostSent to determine if the post has already been sent to the acct
# Return list of unsent welcome messages for acct
async def create_welcome_messages(acct: schemas.MastodonUserCreate):
    # Check if the can be sent any welcome messages
    logging.debug(f"create_welcome_messages: Checking if {acct.acct} can be sent any welcome messages")
    try:
        # Use read_welcome_messages to get the welcome messages
        welcome_messages = await read_welcome_messages()
        # Check if the welcome messages have already been sent to the acct        
        for post in welcome_messages:
            # Use check_post_id_as_sent to check if the post has already been sent to the acct and remove it from the list
            if await check_post_id_as_sent(post.id, acct.id):
                logger.debug(f"Post {post.id} has already been sent to {acct.acct}")
                welcome_messages.remove(post)
            else:
                logger.debug(f"Post {post.id} has not been sent to {acct.acct}")
        logger.debug(f"Created {len(welcome_messages)} welcome messages for {acct.acct}")
        return welcome_messages
    except Exception as e:
        logger.error(f"create_welcome_message | Exception occured: {e}")
        pass

# Send the welcome message to the new user
async def send_welcome_messages(acct: schemas.MastodonUserCreate):
    logging.debug(f"send_welcome_messages: Sending welcome messages to {acct.acct}")
    # Use the base URL and the endpoint: POST /api/v1/statuses HTTP/1.1
    # https://docs.joinmastodon.org/methods/statuses/#post-api-v1-statuses
    # use aiohttp to make the request
    # with get_db() as db:
    # Check if the acct is in the database
    available_welcome_messages = await create_welcome_messages(acct)
    try:
        # Send the welcome message to the new user
        for post in available_welcome_messages:
            logger.debug(f"Post id: {post.id} content: {post.content}")
            # Send the post to the acct                    
            payload = {"status": f"@{acct.acct} {post.content}",
                    "visibility": "direct"}
            # if quiet mode is enabled, don't send the post
            if quiet_mode() == True:
                logger.info(f"Not sending post to {acct.acct}.")
                logger.info(f"Payload content: {payload}")

            else:
                async with aiohttp.ClientSession() as session:
                    logger.debug(f"Sending welcome message to {acct.acct}")
                    
                    async with session.post(f"{settings.mastodon_base_url}/api/v1/statuses", 
                                            headers={"Authorization": f"Bearer {settings.mastodon_access_token}"},
                                            data=payload                        
                                            ) as response:
                        if response.status == 200:
                            logger.info(f"Response status: {response.status}")
                            logger.info(f"Welcome message sent to {acct.acct}")
                        else:
                            logger.warning(f"Response status: {response.status}")
                            logger.warning(f"Response content: {await response.text()}")
                # Mark the post as sent to the acct
                await mark_post_id_as_sent(post.id, acct.id)
            # sleep for 2 seconds
            await asyncio.sleep(2)
        
        # If there are no more posts to send, mark the acct as welcomed
        # If quiet mode is enabled, don't mark the acct as welcomed
        if quiet_mode() == True:
            logger.info(f"Not marking {acct.acct} as welcomed.")
        else:
            await mark_acct_as_welcomed(acct.acct)
            logger.info(f"Marked {acct.acct} as welcomed")
    except Exception as e:
        logger.error(f"send_welcome_messages | Exception occured: {e}")
        pass

'''
Main welcome_bot functions

- check_for_new_users() - Check stream_notifications for new users
- monitor_database() - Check the database for new users

These function contain the main loops and logic for the bot
'''

# Check Instance for new users
async def monitor_instance():
    # Check stream_notifications for new users every 120 seconds
    while True:
        logger.debug("Checking for new users")
        new_users = await stream_notifications()
        if new_users is not None:
            count = len(new_users)
        else:
            count = 0
        if new_users:
            logger.debug(f"New users: {count}")
        await asyncio.sleep(120)

# Monitor the database for new users
async def monitor_database():
    # Check the database for new users every 120 seconds
    # Debug only print to console
    while True:
        logger.debug("Checking the database for new users")
        with get_db() as db:
            # Check if the acct is in the database
            try:
                # Read the new users from the database
                new_accts = db.query(models.MastodonAccts).filter(models.MastodonAccts.welcomed == False).all()
                logger.debug(f"Read {len(new_accts)} new users from the database")
                for acct in new_accts:
                    await send_welcome_messages(acct)
            except Exception as e:
                logger.error(f"monitor_database | Exception occured: {e}")
                pass
        await asyncio.sleep(120)

# Main loop
async def welcome_bot_main():
    # Start the monitor_instance() and monitor_database() functions
    await asyncio.gather(monitor_instance(), monitor_database())
