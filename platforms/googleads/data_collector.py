from platforms.googleads import helper_functions, settings, token_functions
from platforms.googleads.googleads_collector import GoogleAdsCollector
from utils.helpers import bq_connect, upload_to_bq, read_creds
import aiohttp, asyncio, pandas as pd

class DataCollector:
    def __init__(self, client_name):
        self.client_name = client_name
        creds = read_creds('googleads')

        client_id = creds['CLIENT_ID']
        client_secret = creds['CLIENT_SECRET']
        refresh_token = creds['REFRESH_TOKEN']
        self.developer_token = creds['DEVELOPER_TOKEN']

        self.access_token = tokenFunctions.get_access_token(client_id, client_secret, refresh_token)

    async def collect_account_data(self, session, account_id, customer_id, brand):
        googleads_collector = GoogleAdsCollector(client_name=self.client_name, customer_id=customer_id,
                                                 account_id=account_id, access_token=self.access_token,
                                                 developer_token=self.developer_token, session=session, brand=brand)

        data = await googleads_collector.get_report()

        flattened_data = []

        if brand == "airlines":
            for dict in data:
                # Iterate through each result in the data
                for result in dict['results']:
                    ad_name = result['adGroupAd']['ad'].get('name')
                    if ad_name and ':D' in ad_name:
                        ad_name = ad_name.split(':D')[0]
                    elif not ad_name:
                        ad_name = result['adGroup']['name']

                    # Flatten the data
                    flattened_result = {
                        'Date': result['segments']['date'],
                        'Campaign_name': result['campaign']['name'],
                        'Ad_group_name': ad_name,  # changed to ad name

                        'Final_URL': result['adGroupAd']['ad']['finalUrls'][0],
                        # Assuming there's at least one URL
                        'Impressions': int(result['metrics']['impressions']) if result['metrics']['impressions'] else 0,
                        'Clicks': int(result['metrics']['clicks']) if result['metrics']['clicks'] else 0,
                        'Cost': int(result['metrics']['costMicros']) / 1000000 if result['metrics']['costMicros'] else 0,

                        'Video_views': int(result['metrics']['videoViews']) if result['metrics'].get('videoViews') else 0,
                        'Watch_25_rate': float(result['metrics']['videoQuartileP25Rate']) if result['metrics'].get('videoQuartileP25Rate') else 0,
                        'Watch_50_rate': float(result['metrics']['videoQuartileP50Rate']) if result['metrics'].get('videoQuartileP50Rate') else 0,
                        'Watch_75_rate': float(result['metrics']['videoQuartileP75Rate']) if result['metrics'].get('videoQuartileP75Rate') else 0,
                        'Watch_100_rate': float(result['metrics']['videoQuartileP100Rate']) if result['metrics'].get('videoQuartileP100Rate') else 0,

                        'Interactions': int(result['metrics']['interactions']) if result['metrics'].get('interactions') else 0,
                        'Engagements': int(result['metrics']['engagements']) if result['metrics'].get('engagements') else 0,
                        'Gmail_secondary_clicks': int(result['metrics']['gmailSecondaryClicks']) if result['metrics'].get('gmailSecondaryClicks') else 0
                    }

                    # Append the flattened result to the list
                    flattened_data.append(flattened_result)
        else:
            for dict in data:
                # Iterate through each result in the data
                for result in dict['results']:
                    ad_name = result['adGroupAd']['ad'].get('name')
                    if ad_name and ':D' in ad_name:
                        ad_name = ad_name.split(':D')[0]
                    elif not ad_name:
                        ad_name = result['adGroup']['name']

                    # Flatten the data
                    flattened_result = {
                        'Date': result['segments']['date'],
                        'Campaign_ID': result['campaign']['id'],
                        'Campaign_name': result['campaign']['name'],
                        'Ad_group_name': ad_name, #changed to ad name
                        'Final_URL': result['adGroupAd']['ad']['finalUrls'][0],
                        # Assuming there's at least one URL
                        'Impressions': int(result['metrics']['impressions']) if result['metrics']['impressions'] else 0,
                        'Clicks': int(result['metrics']['clicks']) if result['metrics']['clicks'] else 0,
                        'Cost': int(result['metrics']['costMicros']) / 1000000 if result['metrics']['costMicros'] else 0
                    }

                    # Append the flattened result to the list
                    flattened_data.append(flattened_result)

        return flattened_data


    async def handle_brand(self, session, brand_data):
        # print("starting brand", brand_data)
        project = brand_data['project_id']
        dataset = brand_data['dataset']
        table = brand_data['table']
        accounts_dct = {item['account_id']: item['customer_id'] for item in brand_data['accounts']}
        accounts = list(accounts_dct.keys())

        tasks = [asyncio.create_task(self.collect_account_data(session=session, account_id=account_id,
                                                               customer_id=accounts_dct[account_id],
                                                               brand=dataset))
                 for account_id in accounts]
        final_data = []
        results = await asyncio.gather(*tasks)
        for result in results:
            final_data.extend(result)

        df = pd.DataFrame(final_data)

        if not df.empty:
            bq_connect(project)
            destination = f'{dataset}.{table}'
            try:
                await asyncio.get_running_loop().run_in_executor(None, upload_to_bq, df, destination, project, settings.table_schema, settings.start, settings.end)

            except Exception as e:
                print(f"Exception from executor: {e}")

            print(f"Done uploading {table} to {dataset}")


    async def run_collectors(self):
        brands = settings.accounts_data[self.client_name]

        async with aiohttp.ClientSession(trust_env=True) as session:
            tasks = [asyncio.create_task(self.handle_brand(session=session, brand_data=brand)) for brand in brands]
            await asyncio.gather(*tasks)
