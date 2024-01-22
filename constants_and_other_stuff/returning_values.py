import asyncio
import os

from dotenv import load_dotenv

load_dotenv()

async def return_nvd_api_url():
    return os.getenv("NVD_API_URL")

async def return_github_token():
    return os.getenv("GITHUB_TOKEN")