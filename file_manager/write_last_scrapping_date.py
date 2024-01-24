import datetime
from dotenv import load_dotenv, set_key

load_dotenv()

async def write_last_date_scrapping():
    try:
        set_key(".env", "LAST_DATE_SCRAPPING", datetime.datetime.now().strftime("%Y-%m-%d"))
    except Exception as e:
        e.add_note("Cannot set key in function write last date scrapping")
    