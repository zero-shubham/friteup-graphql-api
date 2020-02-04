import motor.motor_asyncio


client = motor.motor_asyncio.AsyncIOMotorClient()
db = client.test_database
