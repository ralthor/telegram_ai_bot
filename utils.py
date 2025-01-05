import aiohttp

async def download_file(file_path, ogg_filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(file_path, allow_redirects=True) as response:
            data = await response.read()
            with open(ogg_filename, 'wb') as f:
                f.write(data)


async def request_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()