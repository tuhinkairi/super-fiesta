from pymongo import AsyncMongoClient
from dotenv import load_dotenv
import os
load_dotenv()
import asyncio

uri= os.getenv("DB_URI")
db_name = "test"

client = AsyncMongoClient(os.getenv("DB_URI"))
db = client[db_name]
collection = "testing"
async def connect():
    
    col = db[collection]
    
    res = await col.insert_one({"name":"test", "email":"test1@gammi.com"}) 
    print( await client.list_database_names(), res)
    
    
asyncio.run(connect())