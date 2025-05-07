import json, os
from datetime import datetime
from time import sleep
from modules import obs, tiltify, twitch

# Startup tasks for all components
def initialize_overlay():
    try:
        print(f"[{timestamp()}] Connecting to OBS...")
        obs.initialize_obs()
        print(f"[{timestamp()}] Connected to OBS.")
    except:
        print(f"[{timestamp()}] ERROR: Could not connect to OBS. Make sure the websocket server is running.")
        os._exit(1)
        
    tiltify.initialize_tiltify()
    twitch.initialize_twitch()
    init_obs_titles()

    print(f"[{timestamp()}] Connections to all services successful.")

    # Uncomment the line below to send a test alert on script startup
    test_alert()

    tiltify.start_schedulers()

# Sending donation notifications to OBS
def process_donation(donation_queue):
    while True:
        # Get a donation from the queue
        donation = donation_queue.get()
        tiltify.last_donation_id = donation['id']
        print(f"[{timestamp()}] Working on {donation['id']}")

        # Gather relevant information
        donor_name = donation['donor_name']
        donation_amount = format_amount(donation['amount']['value'])
        donation_message = donation['donor_comment']

        # Send it to Twitch and OBS
        twitch.bot.send_alert(donor_name, donation_amount, donation_message)
        send_alert_obs(donor_name, donation_amount)

        # Signal that the donation has been processed
        print(f"[{timestamp()}] Finished {donation['id']}")
        donation_queue.task_done()

# For script startup
def init_obs_titles():
    print(f"[{timestamp()}] Updating OBS overlay...")

    last_donation = tiltify.get_last_donation()
    last_donation_amount = format_amount(last_donation['amount']['value'])
    obs.update_last_donation(last_donation['donor_name'][:20], last_donation_amount)

    top_donation = tiltify.get_top_donation()
    top_donation_amount = format_amount(top_donation['amount']['value'])
    obs.update_top_donation(top_donation['donor_name'][:20], top_donation_amount)

    total_raised = tiltify.get_total_raised()
    obs.update_total_raised(total_raised)

    print(f"[{timestamp()}] OBS overlay updated.")

# Handles all of the OBS logic for processing alerts
def send_alert_obs(donor_name, donation_amount):
    # Temporarily disable the donation stats bar while we update everything
    obs.toggle_donation_stats(False)

    # Update our overlays with the new donation information in the background
    obs.update_new_donation_info(donor_name[:30], donation_amount)
    
    # Don't update the donation stats if this is just a test donation
    if (donation_amount != '0.00'):
        obs.update_donation_stats(donor_name[:20], donation_amount)

    # Show "donation recieved!" text and wait 3 seconds
    obs.toggle_donation_recieved_text(True)
    sleep(3)

    # Update our donation total right as we're about to show the donation info
    obs.add_to_total_raised(donation_amount)

    # Show donation information and wait 5 seconds
    obs.toggle_donation_recieved_text(False)
    obs.toggle_new_donation_info(True)
    sleep(5)

    # Go back to the donation stats bar (and wait 5 seconds before signalling that we're ready to process any other alerts)
    obs.toggle_new_donation_info(False)
    obs.toggle_donation_stats(True)
    sleep(5)

# Change the game on Twitch (for proxying from the other modules)
def change_game(game_name): 
    twitch.bot.change_game(game_name)

# For use in the other modules
def load_creds():
    csd = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(csd, "credentials.json")
    try:
        creds_file = open(path, 'r')
        if creds_file is not None:
            return json.load(creds_file)
        else:
            print(f"[{timestamp()}] ERROR: Could not read from credentials.json. Reason: File is empty")
    except:
        print(f"[{timestamp()}] ERROR: Could not read from credentials.json. Reason: File not found")

# Test the alert system with a fake donation
def test_alert():
    print(f"[{timestamp()}] Sending a test alert.")
    
    # Uncomment the below line to send a test alert on Twitch
    # twitch.bot.send_alert("Test Donation", "0.00", "This is a test donation.")

    send_alert_obs("Test Donation", "0.00")

# Return timestamp
def timestamp():
    return datetime.now().strftime("%H:%M:%S")

# Quick currency formatting function
def format_amount(amount):
    return f"{float(amount):.2f}"

if __name__ == '__main__':
    initialize_overlay()