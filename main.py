# from fastapi import FastAPI
from importlib import import_module
import config
from utils.email import SetEmail
import traceback
import time
from dotenv import load_dotenv
import os
from utils.helpers import bq_connect
import asyncio
import warnings 
warnings.filterwarnings("ignore")

load_dotenv()
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

platforms = [
    {
        "name": "googleads",
        "module": "platforms.googleads.main",
        "subject": "BRAND_NAME | Google Ads - BigQuery Automation",
        "to": config.to_emails
    }
]

async def run_platform(p):
    name = p["name"]
    subject = p["subject"]
    to_emails = p["to"]

    try:
        print(f"▶ Starting {name}")
        mod = import_module(p["module"])
        result = await mod.run() 
        duration = result["duration"]
        print(f"✅ {name} done in {duration}s")

        await asyncio.to_thread(SetEmail(
            to_emails=to_emails,
            subject=subject,
            status="Success",
            extra_info={
                "duration (s)": duration
            }
        ).send)

        return {"platform": name, "status": "success", "duration": duration}

    except Exception as e:
        print(f"❌ {name} failed:\n{traceback.format_exc()}")
        await asyncio.to_thread(SetEmail(
            to_emails=to_emails,
            subject=subject,
            status="Failure",
            error=traceback.format_exc()
        ).send)

        return {"platform": name, "status": "failure", "error": str(e)}
        
async def run_all_async():
    tasks = [run_platform(p) for p in platforms]
    return await asyncio.gather(*tasks)


if __name__ == "__main__":

    try:
        start = time.perf_counter()
        results = asyncio.run(run_all_async())
        end = time.perf_counter()
        print("\nAll platforms completed.")

        print("Total duration:", round(end - start, 2), "seconds")
        for r in results:
            print(r)
            
    except Exception as e:
        end = time.perf_counter()
        print(f"❌ Automation failed after {round(end - start, 2)} seconds: {e}")
        print(traceback.format_exc())
        raise