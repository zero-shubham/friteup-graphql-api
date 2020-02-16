import logging

from motor.motor_asyncio import AsyncIOMotorClient
from .mongodb import db


async def connect_to_mongo():
    db.client = AsyncIOMotorClient('mongodb+srv://zero:password@friteup.mongodb.net/test?retryWrites=true&w=majority')


async def close_mongo_connection():
    db.client.close()
