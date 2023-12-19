import aiofiles
import asyncio
import os

async def write_decoded_content_of_file(file_content,file_name : str,name_of_the_directory):
    await asyncio.to_thread(os.chdir,name_of_the_directory)
    async with aiofiles.open(file_name,"w",encoding="utf-8") as f:
        await f.write(file_content.decoded_content.decode())

async def write_decoded_content_of_directory(directory_content, name_of_the_directory : str,user_name_to_create_directory : str):
    await asyncio.to_thread(os.chdir,name_of_the_directory)
    await asyncio.to_thread(os.chdir,user_name_to_create_directory)
    dirs = [directories for directories in directory_content if directories.type == "dir"]
    files = [file for file in directory_content if file.type == "file"]
    #TODO create that directory

