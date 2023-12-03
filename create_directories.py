import subprocess

async def create_directory(name_of_the_directory : str):
    subprocess.call(["mkdir",f"{name_of_the_directory}"])
