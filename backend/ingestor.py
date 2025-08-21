import asyncio, yaml, httpx
from pathlib import Path

CONFIG = Path(__file__).parent / "companies.yaml"

async def main(api_base="http://localhost:8000"):
    conf = yaml.safe_load(CONFIG.read_text())
    async with httpx.AsyncClient(timeout=None) as client:
        for entry in conf.get("companies", []):
            source = entry["source"]
            company = entry["company"]  # e.g., lever handle or greenhouse board token
            url = f"{api_base}/api/ingest/{source}/{company}"
            print("->", url)
            r = await client.post(url)
            print(r.status_code, r.json())

if __name__ == "__main__":
    asyncio.run(main())
