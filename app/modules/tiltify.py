from datetime import datetime, timezone
import threading, queue, time, requests
import main

# Constants
API_POLL_RATE = 5.0 # In seconds

# Saved credentials
credentials = None
campaign_id = None 
auth_header = None

# Other global variables
last_donation_id = None
next_event = None
attempted_refresh = False
donation_queue = queue.LifoQueue()
starttime = time.time()

# Startup routine
def initialize_tiltify():
    global campaign_id, next_event, credentials
    credentials = main.load_creds()
    update_access_token()
    campaign_id = get_campaign_id()
    next_event = get_next_event()

# Starting schedulers
def start_schedulers():
    donation_scheduler_thread = threading.Thread(target = donation_scheduler)
    donation_scheduler_thread.start()
    game_scheduler_thread = threading.Thread(target = game_scheduler)
    game_scheduler_thread.start()

# Scheduler that checks for donations every $API_POLL_RATE seconds (default: 5)
def donation_scheduler():
    global donation_queue, last_donation_id
    while True:
        check_donations(donation_queue, last_donation_id)
        time.sleep(API_POLL_RATE - ((time.time() - starttime) % API_POLL_RATE))

# Scheduler that checks if next_event has arrived every $API_POLL_RATE seconds (default: 5)
def game_scheduler():
    global next_event
    while True:
        next_event = check_event(next_event)
        time.sleep(API_POLL_RATE - ((time.time() - starttime) % API_POLL_RATE))

# Get an access token from Tiltify by authenticating with our client details
def auth_tiltify():
    timestamp = datetime.now().strftime("%H:%M:%S")

    url = "https://v5api.tiltify.com/oauth/token"
    params = {
        'client_id': credentials['tiltify_client_id'], 
        'client_secret': credentials['tiltify_client_secret'],
        'grant_type': 'client_credentials',
        'scope': 'public'
    }
    resp = requests.post(url, json = params)

    if resp.status_code == requests.codes.ok:
        return resp.json()['access_token']
    else:
        print(f"[{timestamp}] ERROR: Could not authenticate with Tiltify. Double check your credentials.")
        return None

# Requests a new access token from Tiltify and updates the authorization header
def update_access_token():
    global auth_header
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] Requesting Tiltify access token...")

    token_resp = auth_tiltify()
    if token_resp is not None:
        auth_header = {'Authorization': 'Bearer ' + token_resp}
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] Successfully obtained Tiltify access token.")
    else:
        print(f"[{timestamp}] ERROR: Tiltify access token could not be obtained. Double check your credentials.")

# Returns campaign ID from user slug and campaign slug
def get_campaign_id():
    timestamp = datetime.now().strftime("%H:%M:%S")
    url = f"https://v5api.tiltify.com/api/public/campaigns/by/slugs/{credentials['tiltify_user_slug']}/{credentials['tiltify_campaign_slug']}"
    resp = requests.get(url, headers = auth_header)
    if resp.status_code == requests.codes.ok:
        return resp.json()['data']['id']
    else:
        print(f"[{timestamp}] ERROR: Campaign data could not be obtained from Tiltify. Something might be wrong with the API.")
        return None
    
# Returns last donation information as JSON
def get_last_donation():
    global last_donation_id
    timestamp = datetime.now().strftime("%H:%M:%S")

    url = f"https://v5api.tiltify.com/api/public/campaigns/{campaign_id}/donations"
    resp = requests.get(url, headers = auth_header, params = {'limit': 1})
    if resp.status_code == requests.codes.ok:
        last_donation_id = resp.json()['data'][0]['id']
        return resp.json()['data'][0]
    else:
        print(f"[{timestamp}] ERROR: Donation data could not be obtained from Tiltify. Something might be wrong with the API.")
        return None
    
# Returns top donation information as JSON
# Tiltify API doesn't have an endpoint for this (only top DONOR, not top DONATION) so we have to do this by iterating over ALL donations
def get_top_donation():
    timestamp = datetime.now().strftime("%H:%M:%S")
    top_donation = None

    url = f"https://v5api.tiltify.com/api/public/campaigns/{campaign_id}/donations"
    resp = requests.get(url, headers = auth_header, params = {'limit': 100})

    if resp.status_code == requests.codes.ok:
        while True:
            cursor = resp.json()['metadata']['after']
            for donation in resp.json()['data']:
                if (top_donation is None or float(donation['amount']['value']) > float(top_donation['amount']['value'])):
                    top_donation = donation
            if cursor is not None:
                resp = requests.get(url, headers = auth_header, params = {'limit': 100, 'after': cursor})
            else: break
                
        return top_donation
    else:
        print(f"[{timestamp}] ERROR: Top donation data could not be obtained from Tiltify. Something might be wrong with the API.")
        return None

# Returns the total amount raised in a campaign as a string
def get_total_raised():
    timestamp = datetime.now().strftime("%H:%M:%S")

    url = f"https://v5api.tiltify.com/api/public/campaigns/{campaign_id}"
    resp = requests.get(url, headers = auth_header)

    if resp.status_code == requests.codes.ok:
        total_raised = resp.json()['data']['amount_raised']['value']
        return f"{float(total_raised):,.2f}"
    else:
        print(f"[{timestamp}] ERROR: Campaign data could not be obtained from Tiltify. Something might be wrong with the API.")
        return None

# Returns the first upcoming event in the schedule
def get_next_event():
    timestamp = datetime.now().strftime("%H:%M:%S")

    url = f"https://v5api.tiltify.com/api/public/campaigns/{campaign_id}/schedules"
    resp = requests.get(url, headers = auth_header, params={'limit': 100})
    if resp.status_code == requests.codes.ok:
        for event in resp.json()['data']:
            if event is None: break
            event_start = datetime.fromisoformat(event['starts_at'])
            if (event_start > datetime.now(timezone.utc)):
                return event
        print(f"[{timestamp}] WARNING: No upcoming events could be found in the schedule.")    
        return None
    else:
        print(f"[{timestamp}] ERROR: Schedule data could not be obtained from Tiltify. Something might be wrong with the API.")
        return None
    
# Searches for new donations by ID matching, and queues them for processing
def check_donations(donation_queue, last_donation_id):
    global attempted_refresh
    
    url = f"https://v5api.tiltify.com/api/public/campaigns/{campaign_id}/donations"
    resp = requests.get(url, headers = auth_header)

    # In case we get multiple donations in a single update, we add all of them to a queue and send alerts one at a time
    if resp.status_code == requests.codes.ok:
        for donation in resp.json()['data']:
            if donation['id'] != last_donation_id:
                # Because the API response is sorted by newest, the queue is LIFO -- so the oldest donations will be processed first
                donation_queue.put(donation)
            else: 
                break
    else:
        timestamp = datetime.now().strftime("%H:%M:%S")
        if attempted_refresh == False:
            print(f"[{timestamp}] Attempting to renew Tiltify authentication...")
            update_access_token()
            attempted_refresh = True
            check_donations(donation_queue, last_donation_id)
        else:
            print(f"[{timestamp}] ERROR: Donation data could not be obtained from Tiltify. Something might be wrong with the API.")
            attempted_refresh = False

    if not donation_queue.empty():
        threading.Thread(target = main.process_donation, args=(donation_queue,)).start()
        donation_queue.join()
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] All work in the queue has been processed.")

# Checks if an event has already happened, and requests to change the Twitch game if so
def check_event(event):
    if event is None: return None
    event_start = datetime.fromisoformat(event['starts_at'])
    if (datetime.now(timezone.utc) > event_start):
        main.change_game(event['name'])
        return get_next_event()
    else:
        return event