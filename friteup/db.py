import motor.motor_asyncio
import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
# 'mongodb+srv://zero:zero000!@friteup-o8pmp.mongodb.net/test?retryWrites=true&w=majority'
client = motor.motor_asyncio.AsyncIOMotorClient(
    'mongodb+srv://zero:zero0000@friteup-o8pmp.mongodb.net/test?retryWrites=true&w=majority', io_loop=loop)
db = client.test_database
