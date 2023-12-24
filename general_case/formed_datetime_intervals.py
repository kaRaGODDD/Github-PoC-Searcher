import datetime

async def generate_intervals(first_year : int, second_year : int):
    intervals = [
        (
            datetime.datetime(year, month, 1).strftime("%Y-%m-%d"),
            datetime.datetime(year, month + 1, 1).strftime("%Y-%m-%d")
        )
        for year in range(first_year, second_year + 1)
        for month in range(1, 12)
    ]
    return intervals
