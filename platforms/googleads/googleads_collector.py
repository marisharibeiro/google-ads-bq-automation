from platforms.googleads import settings

class GoogleAdsCollector:
    def __init__(self, client_name, customer_id, account_id, access_token, developer_token, session, brand):
        self.session = session

        self.account_id = account_id
        self.customer_id = customer_id

        self.report_endpoint = f"https://googleads.googleapis.com/{settings.api_version}/customers/{self.account_id}/googleAds:searchStream"
        self.header = {
            "Authorization": f"Bearer {access_token}",
            "developer-token": developer_token,
            "Content-Type": "application/json",
            "login-customer-id": self.customer_id
        }

        if brand == "airlines":
            self.query = f"""
                    SELECT campaign.id, campaign.name, segments.date, ad_group.id, ad_group.name, ad_group_ad.ad.name,
                    ad_group_ad.ad.final_urls,
                    metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.video_views,
                    metrics.video_quartile_p25_rate, metrics.video_quartile_p50_rate, metrics.video_quartile_p75_rate,
                    metrics.video_quartile_p100_rate, metrics.interactions, metrics.engagements,
                    metrics.gmail_secondary_clicks
                    FROM ad_group_ad
                    WHERE segments.year = {settings.year}
                    """
        else:
            self.query = f"""
                    SELECT campaign.id, campaign.name, segments.date, ad_group.id, ad_group.name, ad_group_ad.ad.name,
                    ad_group_ad.ad.final_urls,
                    metrics.impressions, metrics.clicks, metrics.cost_micros FROM ad_group_ad WHERE segments.year = {settings.year}
                    """


    async def get_report(self):
        payload = {
            "query": self.query
        }

        async with self.session.post(url=self.report_endpoint, headers=self.header, json=payload) as report_response:
            response = await report_response.json()

            if report_response.status != 200:
                print(f"Bad response: {report_response.status}")
                print("Response:", response)
                raise Exception(f"Bad response: {report_response.status}")

            return response




