import pandas_gbq
from google.oauth2 import service_account
import google.auth.transport.requests
from google.auth import default
from config import secret_path
import traceback
import os
import json

def read_creds(platform, raw=False):
    """
    Load credentials from env or local file.
    - If `raw=True`: returns raw string (used for non-JSON secrets like .pem)
    - If `raw=False`: parses JSON (default behavior for API creds)
    """

    # Try ENV
    try:
        secret_value = os.environ[secret_path[platform]]
        return secret_value if raw else json.loads(secret_value)
    except:
        pass  # fall through to file

    # Try local file
    try:
        with open(secret_path[platform], 'r') as f:
            return f.read() if raw else json.load(f)
    except Exception as e:
        print(f"Failed to read credentials for {platform}: {e}")
        raise

def debug_credentials(credentials):
    try:
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)

    except Exception as e:
        print("⚠️ Failed to debug credentials:", e)

def bq_connect(bq_project):
    try:
        credentials, _ = default()
        debug_credentials(credentials)  # Add this for debug info
    except:
        key_paths = {
            f'{bq_project}': f'{bq_project}-bigquery.json'
        }
        key_path = f'secrets/{project_id}/{key_paths[project_id]}'  
        credentials = service_account.Credentials.from_service_account_file(key_path)

    pandas_gbq.context.credentials = credentials
    pandas_gbq.context.project = project_id

def upload_to_bq(df, destination, project, table_schema, start_date, end_date, date_column='Date'):
    try:
        try:
            pandas_gbq.read_gbq(
                f'DELETE `{destination}`'
                f'WHERE SAFE_CAST({date_column} AS DATE) BETWEEN CAST(\'{start_date}\' AS DATE) AND CAST(\'{end_date}\' AS DATE)',
                project_id=project
            )
        except Exception as e:
            if "Not found: Table" in str(e) and "was not found" in str(e):
                print(f"No data to delete for {destination} for {start_date} to {end_date} (table does not exist)")
            else:
                print(f"Error deleting data for {destination} for {start_date} to {end_date}")
                traceback.print_exc()
                raise
        else:
            print(f"Deleted data for {destination} for {start_date} to {end_date}")

        pandas_gbq.to_gbq(df, f'{destination}',
                          project_id=project,
                          if_exists='append',
                          table_schema=table_schema)

        print(f"Upload successful for {destination}!")
    except:
        print(f"oops, problem with {destination}")
        traceback.print_exc()

        raise Exception(f"Upload failed for {destination}")