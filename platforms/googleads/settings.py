import config
import datetime

brand_name = 'BRAND_NAME'
today = config.today
yesterday = config.yesterday
year = config.year # Input year as integer if needed

USE_LAST_10_DAYS = True # True for last 10 days, False for full year

# Date range logic based on flag
if USE_LAST_10_DAYS:
    # Last 10 days refresh
    start = (yesterday - datetime.timedelta(days=9)).strftime('%Y-%m-%d')
    end = yesterday.strftime('%Y-%m-%d')
    print(f"🔄 Using last 10 days refresh: {start} to {end}")
else:
    # Full year refresh (default)
    start = f'{year}-01-01'
    end = yesterday.strftime('%Y-%m-%d') if year == today.year else f'{year}-12-31'
    print(f"🔄 Using full year refresh: {start} to {end}")

api_version = 'v20' # API version for Google Ads API

accounts_data = \
    {
        'BRAND_NAME': [
            {
                "accounts": [
                    {
                        "account_id": 'ACCOUNT_ID',
                        "acc_name": "ACCOUNT_NAME",
                        "customer_id": 'CUSTOMER_ID'
                    },
                    {
                        "account_id": 'ACCOUNT_ID',
                        "acc_name": "ACCOUNT_NAME",
                        "customer_id": 'CUSTOMER_ID'
                    }
                ],
                "project_id": "BQ_PROJECT_NAME",
                "dataset": "DATASET_NAME",
                "table": f'TABLE_NAME_{year}'
            }
        ]
    }

table_schema = [
    {'name': 'Date', 'type': 'DATE'},
    {'name': 'Campaign_name', 'type': 'STRING'},
    {'name': 'Ad_group_name', 'type': 'STRING'},
    {'name': 'Creative_Final_URL', 'type': 'STRING'},
    {'name': 'Impressions', 'type': 'INTEGER'},
    {'name': 'Clicks', 'type': 'INTEGER'},
    {'name': 'Cost', 'type': 'FLOAT'},
    {'name': 'Video_views', 'type': 'INTEGER'},
    {'name': 'Watch_25_rate', 'type': 'FLOAT'},
    {'name': 'Watch_50_rate', 'type': 'FLOAT'},
    {'name': 'Watch_75_rate', 'type': 'FLOAT'},
    {'name': 'Watch_100_rate', 'type': 'FLOAT'},
    {'name': 'Interactions', 'type': 'INTEGER'},
    {'name': 'Engagements', 'type': 'INTEGER'},
    {'name': 'Gmail_secondary_clicks', 'type': 'INTEGER'}
    ] # Add/adjust columns as needed as per Google Ads API documentation
