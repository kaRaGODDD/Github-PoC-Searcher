import aiofiles
import os
from dotenv import load_dotenv

load_dotenv()

async def read_file_by_path(cve_object_path: str):
    try:
        async with aiofiles.open(cve_object_path, "r", encoding='utf-8') as f:
            content = await f.read()
            return content
    except Exception as e:
        print(f"Error was occured: {e}")