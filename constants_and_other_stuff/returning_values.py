import asyncio
import os

from dotenv import load_dotenv


load_dotenv()

async def return_github_api_url():
    return "https://api.github.com/search/repositories?q={}"

async def return_nvd_api_url():
    return "https://services.nvd.nist.gov/rest/json/cves/2.0/?pubStartDate={}T00:00:00&pubEndDate={}T23:59:59"

async def return_nvd_api_key():
    return os.getenv("NVD_API_KEY")

async def return_github_token():
    return os.getenv("GITHUB_TOKEN")