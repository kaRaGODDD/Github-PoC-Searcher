import resource

async def incr_file_descriptors():
    resource.setrlimit(resource.RLIMIT_NOFILE, (180000, 180000))

