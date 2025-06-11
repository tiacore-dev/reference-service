import asyncio

import aiohttp
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from app.exceptions.telegram import TelegramAPIError


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
)
async def fetch_json(session, method, url, **kwargs):
    async with session.request(method, url, **kwargs) as resp:
        text = await resp.text()
        if resp.status != 200:
            raise TelegramAPIError(resp.status, text)
        return await resp.json()


async def fetch_bytes(session, method, url):
    async with session.request(method, url) as resp:
        resp.raise_for_status()
        return await resp.read()
