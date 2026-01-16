import requests, os, base64, time

# Initialize cached token and expiration time variables
cached_token = None
token_expiration = None

def get_zoom_token():
    global cached_token, token_expiration

    #  Check if the token is cached and not expired
    if cached_token and token_expiration and token_expiration > time.time():
        return {
            'access_token': cached_token,
            'expires_in': token_expiration - time.time(),
            'header_config': {
                'Authorization': f'Bearer {cached_token}',
                'Content-Type': 'application/json'
            },
            'error': None
        }
    
    try:
        # Create the authorization header
        auth_string = f"{os.getenv('ZOOM_CLIENT_ID')}:{os.getenv('ZOOM_CLIENT_SECRET')}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()

        headers = {
            'Authorization': f'Basic {encoded_auth}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # Prepare the data for the POST request
        data = {
            'grant_type': 'account_credentials',
            'account_id': os.getenv('ZOOM_ACCOUNT_ID')
        }

        # Make the POST request
        response = requests.post("https://zoom.us/oauth/token", headers=headers, data=data)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        # Parse the JSON response
        result = response.json()
        access_token = result.get('access_token')
        expires_in = result.get('expires_in')

        # Update the cached token and expiration
        cached_token = access_token
        token_expiration = time.time() + expires_in

        header_config = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
        return {
            'access_token': access_token, 
            'expires_in': expires_in,
            'header_config': header_config, 
            'error': None}
    
    except requests.RequestException as error:
        return {
            'access_token': None, 
            'expires_in': None, 
            'error': str(error)}
    
def create_meeting(time):
    token = get_zoom_token()['access_token']
    if not token:
        return  "Failed to obtain Zoom access token.", None

    try:
        url = f"https://api.zoom.us/v2/users/me/meetings"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "topic": "Client Booking",
            "type": 2,
            "start_time": time.isoformat(),
            "duration": 30,
            "timezone": os.getenv("TIMEZONE", "Africa/Johannesburg"),
            "settings": {
                "host_video": True,
                "participant_video": True,
                "waiting_room": True
            }
        }

        meet_link = requests.post(url, headers=headers, json=payload).json()["join_url"]

        return None, meet_link

    except Exception as e:

        return "error occured, please try again later.", None 