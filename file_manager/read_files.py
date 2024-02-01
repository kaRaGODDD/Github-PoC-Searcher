import aiofiles
import os
from dotenv import load_dotenv
from typing import Optional, Union
from constants_and_other_stuff.enums import TypeOfTheDirectory

load_dotenv()

async def read_file_by_path(cve_object_path: str, type_of_the_directory: Optional[TypeOfTheDirectory] = None) -> Union[str, None]:
    if not os.path.exists(cve_object_path) and type_of_the_directory:
        print(f"That path doesn't exist: {cve_object_path}")
        return None
    try:
        async with aiofiles.open(cve_object_path, "r", encoding='utf-8') as f:
            content = await f.read()
            return content
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
