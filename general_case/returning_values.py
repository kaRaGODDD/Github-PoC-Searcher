import os
from dotenv import load_dotenv 

load_dotenv()

async def return_token():
    return os.getenv("GITHUB_TOKEN")

async def return_url():
    return "https://api.github.com/search/repositories?q=proof%20of%20concept%20created:{}..{}"

async def return_last_date_scrapping():
    return os.getenv("LAST_DATE_SCRAPPING")