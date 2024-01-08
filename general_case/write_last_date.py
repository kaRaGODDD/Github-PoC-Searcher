import datetime
from dotenv import load_dotenv, set_key

load_dotenv()

async def write_last_date_scrapping(datetime):
    try:
        set_key(".env", "LAST_DATE_SCRAPPING", datetime)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    
