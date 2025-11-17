from datetime import datetime, timedelta

# # 👇 manually set this if you want to simulate another day
# today_str = '2025-04-01'
# today = datetime.strptime(today_str, "%Y-%m-%d").date()


today = datetime.today()

yesterday = today - timedelta(days=1)
yesterday_str = yesterday.strftime("%Y-%m-%d")
year = yesterday.year

to_emails = ['marina.ribeiro@umww.com']

secret_path = {
    'gmail': 'secrets/gmail_credentials',
    'googleads': 'secrets/googleads-credentials'
}
