#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE


import aiohttp
import json


class AsyncRestClient:
    def __init__(self, base_url):
        self.base_url = base_url

    async def fetch_data(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to fetch data from {url}, status code: {response.status}")

    async def post_data(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        body = json.dumps(data)
        async with aiohttp.ClientSession() as session:
            async with session.post(url,  data=data) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    raise Exception(f"Failed to post data to {url}, status code: {response.status}")

    async def put_data(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to update data at {url}, status code: {response.status}")

    async def delete_data(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.delete(url) as response:
                if response.status == 204:
                    return True
                else:
                    raise Exception(f"Failed to delete data at {url}, status code: {response.status}")


