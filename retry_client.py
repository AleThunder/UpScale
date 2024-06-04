import httpx
import asyncio
from httpx import RequestError, HTTPStatusError


class RetryClient:
    def __init__(self, retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist
        self.client = httpx.AsyncClient()

    async def request(self, method, url, **kwargs):
        for attempt in range(self.retries):
            try:
                response = await self.client.request(method, url, **kwargs)
                if response.status_code not in self.status_forcelist:
                    return response
                response.raise_for_status()
            except (RequestError, HTTPStatusError) as e:
                if attempt == self.retries - 1:
                    raise
                else:
                    backoff_time = self.backoff_factor * (2 ** attempt)
                    await asyncio.sleep(backoff_time)
                    continue

    async def get(self, url, **kwargs):
        return await self.request("GET", url, **kwargs)

    async def post(self, url, **kwargs):
        return await self.request("POST", url, **kwargs)

    async def close(self):
        await self.client.aclose()

# Приклад використання

# async def main():
#     retry_client = RetryClient()
#     try:
#         response = await retry_client.get("https://example.com")
#         print(response.text)
#     finally:
#         await retry_client.close()
# 
# 
# asyncio.run(main())