import asyncio
from dotenv import load_dotenv
from create_poc_database.create_poc_database import POCDatabase

load_dotenv()

async def main():
    poc_instance = POCDatabase()
    await poc_instance.update_database()

if __name__ == "__main__":
    asyncio.run(main())