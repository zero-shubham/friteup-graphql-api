import motor.motor_asyncio

# 'mongodb+srv://zero:zero000!@friteup-o8pmp.mongodb.net/test?retryWrites=true&w=majority'
client = motor.motor_asyncio.AsyncIOMotorClient()
db = client.test_database
