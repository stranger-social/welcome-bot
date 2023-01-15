# Mastodon Welcome Bot

This is a Mastodon bot that welcomes new users to your instance.

This bot does not offer a secure http endpoint. It is recommended to run this bot behhind a firewall or a reverse proxy.

The purpose of this bot is to welcome new users to your instance. It does this by sending a welcome message from a database to new users

## Get API Key

To use this bot, you will need to create a bot account on your Mastodon instance. You can do this by going to your instance's settings page under Development, and creating a new application. The bot requires `read:notifications`, `read:statuses` and `write:statuses` permissions. Copy the access token for the bot account, and paste it into the .env file.

The Bot will also need Moderator permissions on your instance. This is required to read the New User notifications.

## Installation

1. Clone this repository
2. Create .env file from the .env.example file
3. Fill in the .env file with your Mastodon instance's information
4. Run `docker-compose up --build -d` to start the bot.
5. Run `docker ps -a` to see the container ID of the bot.
6. Run `docker exec -ti [container_id] /bin/bash` to enter the container.
7. Run Alembic migrations by running `alembic upgrade head` in the container.
8. Run `docker-compose restart` to restart the bot.
9. Initiate admin user by visiting http://localhost:8088/docs#/Admin/init_admin_admin_init_post. 

## Usage

This bot is designed to be controlled through an API. The API is documented using OpenAPI 3.0.2. The documentation is available at http://localhost:8088/docs.

## Environment Variables

The following environment variables are required to run the bot, and should be set in the .env file.
```
QUIET=True/False
MASTODON_ACCESS_TOKEN=The access token for your bot account on your Mastodon instance
MASTODON_BASE_URL=The base URL for your Mastodon instance (e.g. https://stranger.social)
DATABASE_HOSTNAME=postgres
DATABASE_PORT=5432
DATABASE_PASSWORD=password
DATABASE_NAME=welcomebot
DATABASE_USERNAME=postgres
SECRET_KEY=Use genkey.py to generate a secret key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=2
```