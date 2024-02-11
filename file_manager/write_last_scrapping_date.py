import datetime
from dotenv import load_dotenv, set_key

load_dotenv()

async def write_last_date_scraping(name_of_the_key: str, datetime_interval_format: str="%Y-%m-%d"):
    try:
        set_key(".env", name_of_the_key, datetime.datetime.now().strftime(datetime_interval_format))
    except Exception as e:
        e.add_note("Cannot set key in function write last date scrapping")
    