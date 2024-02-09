import os

async def create_directory(name_of_the_directory: str, path_where_need_to_create: str):
    full_path = os.path.join(path_where_need_to_create,name_of_the_directory)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
        