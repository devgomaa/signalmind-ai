import aiohttp
import asyncio

from engine.utils.logger import get_logger

logger = get_logger("AsyncFetcher")


async def fetch_json(url, headers=None, retries=3):

    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(timeout=timeout) as session:

        for attempt in range(retries):

            try:

                async with session.get(url, headers=headers) as response:

                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}")

                    return await response.json()

            except Exception as e:

                logger.warning(f"Fetch failed {attempt+1}: {e}")

                await asyncio.sleep(1)

        return None
