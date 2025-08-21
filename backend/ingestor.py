import asyncio
import aiohttp
from aiolimiter import AsyncLimiter

# limit to 5 requests per second
limiter = AsyncLimiter(max_rate=5, time_period=1)

async def fetch(session, url):
    async with limiter:  # ensures rate limit
        try:
            async with session.get(url, timeout=20) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"⚠️ Error {response.status} for {url}")
        except Exception as e:
            print(f"❌ Request failed for {url}: {e}")
        return None

async def scrape_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

if __name__ == "__main__":
    urls = [
        "https://www.modernatx.com/careers",
        "https://www.gilead.com/careers",
        "https://www.regeneron.com/careers"
    ]
    results = asyncio.run(scrape_all(urls))
    print(f"Got {sum(r is not None for r in results)} pages successfully.")
