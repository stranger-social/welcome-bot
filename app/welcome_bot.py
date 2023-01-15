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
        logger.info("Quiet mode is enabled")
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
            logger.info(f"Added {new_acct} to the database")
        except:
            logger.info(f"{new_acct} already in the database")
            pass

# Monitor server notifications for new users
async def stream_notifications():
    # Use the base URL and the endpoint: GET /api/v1/streaming/user/notification HTTP/1.1
    # https://docs.joinmastodon.org/methods/streaming/#notification
    # use aiohttp to make the request
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{settings.mastodon_base_url}/api/v1/notifications", headers={"Authorization": f"Bearer {settings.mastodon_access_token}"}) as response:
            if response.status == 200:
                logger.info(f"Response status: {response.status}")
                # Read the response as JSON
                data = await response.json()
                # Check if the response is a list
                if isinstance(data, list):
                    # Interate over the list and find the type: admin.sign_up
                    for item in data:
                        if item["type"] == "admin.sign_up":
                            # Get the user's acct
                            acct = item["account"]["acct"]
                            logger.info(f"New user: {acct}")
                            # Add the user's acct to the database
                            await add_mastodon_acct(acct)
                            # Clear the notifications
                            item_id = item["id"]
                            logger.info(f"item_id:{item_id}")
                            async with session.post(f"{settings.mastodon_base_url}/api/v1/notifications/{item_id}/dismiss", headers={"Authorization": f"Bearer {settings.mastodon_access_token}"}) as response:
                                if response.status == 200:
                                    logger.info(f"Response status: {response.status}")
                                    logger.info(f"Notifications cleared")
                                else:
                                    logger.info(f"Response status: {response.status}")
                                    logger.info(f"Response content: {await response.text()}")
            else:
                # Log response status
                logger.info(f"Response status: {response.status}")
                # Log response content
                logger.info(f"Response content: {await response.text()}")
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
                logger.info(f"Post {post_id} has already been sent to {mastodon_acct_id}")
                return True
            else:
                logger.info(f"Post {post_id} has not been sent to {mastodon_acct_id}")
                return False
        except:
            logger.info(f"Error checking if post {post_id} has been sent to {mastodon_acct_id}")
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
                logger.info(f"Post {post_id} has already been sent to {mastodon_acct_id}")
                return True
            else:
                logger.info(f"Post {post_id} has not been sent to {mastodon_acct_id}")
                # Add the post_id to the database
                new_post_sent=models.PostSent(post_id=post_id, mastodon_acct_id=mastodon_acct_id)
                db.add(new_post_sent)
                db.commit()
                db.refresh(new_post_sent)
                logger.info(f"Added post {post_id} to the database")
                return False
        except:
            logger.info(f"Error checking if post {post_id} has been sent to {mastodon_acct_id}")
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
                logger.info(f"{acct} has already been welcomed")
                return True
            else:
                logger.info(f"{acct} has not been welcomed")
                return False
        except:
            logger.info(f"Error checking if {acct} has been welcomed")
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
        except:
            logger.info(f"Failed to mark {acct} as welcomed")
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
        except:
            logger.info(f"No welcome messages in the database")
            pass

# Send the welcome message to the new user
async def send_welcome_messages(acct: schemas.MastodonUserCreate):
    # Use the base URL and the endpoint: POST /api/v1/statuses HTTP/1.1
    # https://docs.joinmastodon.org/methods/statuses/#post-api-v1-statuses
    # use aiohttp to make the request
    with get_db() as db:
        # Check if the acct is in the database
        try:
            # Send the welcome message to the new user
            for post in await read_welcome_messages():
                # Check if the post has already been sent to the acct
                if await check_post_id_as_sent(post.id, acct.id):
                    logger.info(f"Post {post.id} has already been sent to {acct.acct}")
                    pass
                else:
                    
                    # Send the post to the acct                    
                    payload = {"status": f"@{acct} {post.content}",
                            "visibility": "direct"}
                    # if quiet mode is enabled, don't send the post
                    if quiet_mode() == True:
                        logger.info(f"Not sending post to {acct}.")
                        logger.info(f"Payload content: {payload}")

                    else:
                        async with aiohttp.ClientSession() as session:
                            logger.info(f"Sending welcome message to {acct}")
                            
                            async with session.post(f"{settings.mastodon_base_url}/api/v1/statuses", 
                                                    headers={"Authorization": f"Bearer {settings.mastodon_access_token}"},
                                                    data=payload                        
                                                    ) as response:
                                if response.status == 200:
                                    logger.info(f"Response status: {response.status}")
                                    logger.info(f"Welcome message sent to {acct}")
                                else:
                                    logger.info(f"Response status: {response.status}")
                                    logger.info(f"Response content: {await response.text()}")
                        # Mark the post as sent to the acct
                        await mark_post_id_as_sent(post.id, acct.id)
                    # sleep for 2 seconds
                    await asyncio.sleep(2)
            
            # If there are no more posts to send, mark the acct as welcomed
            # If quiet mode is enabled, don't mark the acct as welcomed
            if quiet_mode() == True:
                logger.info(f"Not marking {acct} as welcomed.")
            else:
                await mark_acct_as_welcomed(acct.acct)
                logger.info(f"Marked {acct} as welcomed")



            
        except:
            logger.info(f"No welcome messages in the database")
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
        logger.info("Checking for new users")
        new_users = await stream_notifications()
        if new_users is not None:
            count = len(new_users)
        else:
            count = 0
        if new_users:
            logger.info(f"New users: {count}")
        await asyncio.sleep(120)

# Monitor the database for new users
async def monitor_database():
    # Check the database for new users every 120 seconds
    # Debug only print to console
    while True:
        logger.info("Checking the database for new users")
        with get_db() as db:
            # Check if the acct is in the database
            try:
                # Read the new users from the database
                new_users = db.query(models.MastodonAccts).filter(models.MastodonAccts.welcomed == False).all()
                logger.info(f"Read {len(new_users)} new users from the database")
                for user in new_users:
                    logger.info(f"Sending welcome message to {user.acct}")
                    await send_welcome_messages(user.acct)
            except:
                logger.info(f"No new users in the database")
                pass
        await asyncio.sleep(120)
