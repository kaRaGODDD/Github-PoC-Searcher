from choosing_cloning_options import *
from formed_datetime_intervals import *

async def scrapping(url_for_scrapping_pages: str,headers: dict,token: str):
    choice = ParsingChoice.SINCE_LAST_SCRAPPING
    match choice:
        case ParsingChoice.YEAR_BY_YEAR:
            first_interval = "2015-01-01"
            second_interval = "2016-01-01"
            name_of_the_interval_directory = await formed_interval_and_switch_directory(first_interval,second_interval)
            await сloning_is_carried_out_by_year(url_for_scrapping_pages,headers,token,2015,2016,name_of_the_interval_directory)
        case ParsingChoice.FROM_ONE_INTERVAL_TO_SECOND:
            first_interval = "2015-03-05"
            second_interval = "2015-04-07"
            name_of_the_interval_directory = await formed_interval_and_switch_directory(first_interval,second_interval)
            await сloning_is_performed_at_specified_intervals(url_for_scrapping_pages,headers,token,first_interval,second_interval,name_of_the_interval_directory)
        case ParsingChoice.YEAR_AND_MONTH_FIXED:
            first_interval = "2015-03-01"
            second_interval = "2015-03-05"
            name_of_the_interval_directory = await formed_interval_and_switch_directory(first_interval,second_interval)
            await cloning_is_performed_according_to_a_fixed_year_and_month(url_for_scrapping_pages,headers,token,first_interval,second_interval,name_of_the_interval_directory)
        case ParsingChoice.SINCE_LAST_SCRAPPING:
            first_interval = os.getenv("LAST_DATE_SCRAPPING")
            second_interval = datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S")
            first_interval_strftime_format,second_interval_strftime_format = await to_strftime_format(first_interval,second_interval,"%Y-%m-%d%H:%M:%S")
            name_of_the_interval_directory = await formed_interval_and_switch_directory(first_interval_strftime_format,second_interval_strftime_format)
            await since_last_scrapping(url_for_scrapping_pages,headers,token,False,name_of_the_interval_directory)
        case ParsingChoice.MOST_POPULAR:
            pass
        case _:
            print("Doesnt know that option")
    