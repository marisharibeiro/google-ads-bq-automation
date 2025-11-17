import webbrowser
import requests


def get_refresh_token(CLIENT_ID, CLIENT_SECRET):
    """
    Get the refresh token for the Google Ads API
    Args:
        CLIENT_ID: The client ID for the Google Ads API
        CLIENT_SECRET: The client secret for the Google Ads API
        Obtain this from the Google Ads API console
    Returns:
        The refresh token for the Google Ads API. It will be used to get the access token.
        STORE IT IN THE SECRETS/GOOGLEADS-CREDENTIALS FILE. 
    """
    REDIRECT_URI = 'http://localhost:8080/'  # This is for desktop apps

    # Step 1: Generate the authorization URL and open it in a web browser
    auth_endpoint = 'https://accounts.google.com/o/oauth2/v2/auth'
    scope = 'https://www.googleapis.com/auth/adwords'

    auth_url = (f"{auth_endpoint}?response_type=code&client_id={CLIENT_ID}"
                f"&redirect_uri={REDIRECT_URI}&scope={scope}&access_type=offline")

    webbrowser.open(auth_url)

    # Step 2: After granting permissions, you'll be shown a code. Enter it here
    auth_code = input("Enter the authorization code: ")

    # Step 3: Exchange the code for a refresh token
    token_endpoint = 'https://oauth2.googleapis.com/token'

    payload = {
        'code': auth_code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }

    response = requests.post(token_endpoint, data=payload)
    token_data = response.json()

    refresh_token = token_data['refresh_token']
    print(f"Your refresh token is: {refresh_token}")
    return refresh_token

def get_access_token(client_id, client_secret, refresh_token):
    """
    Get the access token for the Google Ads API
    Args:
        client_id: The client ID for the Google Ads API
        client_secret: The client secret for the Google Ads API
        refresh_token: The refresh token for the Google Ads API obrained from the get_refresh_token function
    Returns:
        The access token for the Google Ads API. It will be used to make requests to the Google Ads API.
        Data Collector class will use this function to get the access token, no need to store this value anywhere else.     
        """
    token_url = "https://oauth2.googleapis.com/token"

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    response = requests.post(token_url, data=payload)
    token_data = response.json()

    return token_data['access_token']
