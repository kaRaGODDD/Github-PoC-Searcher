import asyncio

from returning_values import return_token, return_url
from create_directories import create_data_directory
from scrapping_parser import scrapping

async def main():
    token = await return_token()
    url_for_scrapping_pages = await return_url()
    headers = {"Authorization": f"Bearer {token}"}
    await create_data_directory()
    await scrapping(url_for_scrapping_pages,headers,token)    

if __name__ == "__main__":
    asyncio.run(main())