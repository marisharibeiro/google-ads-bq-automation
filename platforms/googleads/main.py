from platforms.googleads.data_collector import DataCollector
from platforms.googleads import settings
import time
import asyncio

async def run_async():
    dataCollector = DataCollector(settings.brand_name)
    await dataCollector.run_collectors()

async def run():
    start = time.time()
    yesterday_fmt = settings.yesterday.strftime('%Y%m%d')

    await run_async()

    diff = time.time() - start
    return {
        "platform": "Google Ads",
        "date": yesterday_fmt,
        "duration": round(diff, 2),
        "status": "Success"
    }