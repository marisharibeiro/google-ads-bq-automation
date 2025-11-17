import requests
import pandas as pd
import pandas_gbq
from platforms.googleads import settings
from utils.helpers import bq_connect


def list_accessible_customers(access_token, developer_token):
    url = f"https://googleads.googleapis.com/{settings.api_version}/customers:listAccessibleCustomers"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "developer-token": developer_token
    }
    response = requests.get(url, headers=headers)

    status = response.status_code
    if not status == 200:
        print(response.text)
    else:
        data = response.json()
        # print(data)

        return data['resourceNames']



def list_accounts_for_customer(access_token, developer_token, customer_id):
    # Endpoint for the search method
    url = f"https://googleads.googleapis.com/{settings.api_version}/customers/{customer_id}/googleAds:searchStream"

    # Headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "developer-token": developer_token,
        "Content-Type": "application/json"
    }

    # Google Ads Query Language query to retrieve campaigns
    query = """
    SELECT
        customer_client.client_customer
    FROM
        customer_client
    """

    payload = {
        "query": query
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        # print(data)
        # print(data[0]['results'])

        # Extract client_customer values and return them as a list
        client_customers = [item['customerClient']['clientCustomer'] for item in data[0].get('results', [])]
        # print(client_customers)
        return client_customers

    else:
        # Print the status code and response content for debugging
        print("Status Code:", response.status_code)
        print("Response Content:", response.text)
        print("Failed to retrieve campaigns for the customer.")
        return None


def list_campaigns_for_customer(access_token, developer_token, customer_id, account_id):
    # Endpoint for the search method
    url = f"https://googleads.googleapis.com/{settings.api_version}/customers/{account_id}/googleAds:search"

    # Headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "developer-token": developer_token,
        "Content-Type": "application/json",
        "login-customer-id": customer_id
    }

    # Google Ads Query Language query to retrieve campaigns
    query = "SELECT campaign.id, campaign.name, campaign.status FROM campaign"

    payload = {
        "query": query
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        # print(data)
        return data['results']
    else:
        # Print the status code and response content for debugging
        print("Status Code:", response.status_code)
        print("Response Content:", response.text)
        print("Failed to retrieve campaigns for the customer.")
        return None


async def transform_data(data):
    flattened_data = []

    for dict in data:
        # Iterate through each result in the data
        for result in dict['results']:
            # Flatten the data
            flattened_result = {
                'Date': result['segments']['date'],
                'Campaign': result['campaign']['name'],
                'Ad group': result['adGroup']['name'],
                'Creative Final URL': result['adGroupAd']['ad']['finalUrls'][0],  # Assuming there's at least one URL
                'Impressions': result['metrics']['impressions'],
                'Clicks': result['metrics']['clicks'],
                'Cost': int(result['metrics']['costMicros']) / 1000000 if result['metrics']['costMicros'] else 0
            }

            # Append the flattened result to the list
            flattened_data.append(flattened_result)

    return flattened_data