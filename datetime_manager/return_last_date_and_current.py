import os
from datetime import datetime
from dotenv import load_dotenv
from constants_and_other_stuff.structs import StringInterval


load_dotenv()

async def return_last_current_intervals_for_poc_update():
    return StringInterval(os.getenv("LAST_DATE_SCRAPPING_POC_UPDATE"),datetime.now("%Y-%m-%d"))
