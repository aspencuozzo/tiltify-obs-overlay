import obsws_python as obsws
import main

# Text template constants
SCENE = "Donation Bar"
TOP_DONATION = "Top Donation: "
LAST_DONATION = "Last Donation: "

# Donation "constants" (close enough)
DONATION_STATS = None
DONATION_RECIEVED_TEXT = None 
NEW_DONATION_INFO = None

# Global variables
obs = None
credentials = None
top_donation_amount = 0

# Connects to websocket and sets up scene defaults
def initialize_obs():
    global obs
    credentials = main.load_creds()
    obs = obsws.ReqClient(
        host = credentials['obs_websocket_host'], 
        port = credentials['obs_websocket_port'], 
        password = credentials['obs_websocket_password']
    )
    set_constants()
    set_scene_item_defaults()

def set_constants():
    global DONATION_STATS, DONATION_RECIEVED_TEXT, NEW_DONATION_INFO
    DONATION_STATS = obs.get_scene_item_id(SCENE, "Donation Stats").scene_item_id
    DONATION_RECIEVED_TEXT = obs.get_scene_item_id(SCENE, "Donation Received Text").scene_item_id
    NEW_DONATION_INFO = obs.get_scene_item_id(SCENE, "New Donation Info").scene_item_id

# Sets default visibility for items in the donation scene
def set_scene_item_defaults():
    obs.set_scene_item_enabled(SCENE, DONATION_RECIEVED_TEXT, False)
    obs.set_scene_item_enabled(SCENE, NEW_DONATION_INFO, False)
    obs.set_scene_item_enabled(SCENE, DONATION_STATS, True)

# Updates the "Donation Stats" group, showing last/top donation information when there is not currently an alert
def update_donation_stats(donor_name, donation_amount):
    global top_donation_amount
    update_last_donation(donor_name, donation_amount)
    if (float(donation_amount) > float(top_donation_amount)):
        update_top_donation(donor_name, donation_amount)

# Update the last donation
def update_last_donation(donor_name, donation_amount):
    donation_string = f"{donor_name} - ${donation_amount}"
    obs.set_input_settings("Last Donation", {'text': LAST_DONATION + donation_string}, True)

# Update the top donation
def update_top_donation(donor_name, donation_amount):
    global top_donation_amount
    donation_string = f"{donor_name} - ${donation_amount}"
    obs.set_input_settings("Top Donation", {'text': TOP_DONATION + donation_string}, True)
    top_donation_amount = donation_amount

# Updates the "New Donation Info" group, a notification displayed when a donation has been received
def update_new_donation_info(donor_name, donation_amount):
    obs.set_input_settings("Donation Amount", {'text': f'${donation_amount}'}, True)
    obs.set_input_settings("Donation Name", {'text': donor_name}, True)

# Changes the current donation total in the "Total Raised" group
def update_total_raised(total_raised):
    obs.set_input_settings("Current Total", {'text': f'${total_raised}'}, True)

# Adds a donation to the current donation total in the "Total Raised" group
def add_to_total_raised(donation_amount):
    new_donation_total = get_current_total() + float(donation_amount)
    obs.set_input_settings("Current Total", {'text': f'${new_donation_total:,.2f}'}, True)

# Gets the current total from OBS and returns it as a float
def get_current_total():
    string_total = obs.get_input_settings("Current Total").input_settings['text']
    return float(string_total.strip('$').replace(',',''))

# Functions for toggling variable groups, to be called from other files
def toggle_donation_stats(boolean): obs.set_scene_item_enabled(SCENE, DONATION_STATS, boolean)
def toggle_donation_recieved_text(boolean): obs.set_scene_item_enabled(SCENE, DONATION_RECIEVED_TEXT, boolean)
def toggle_new_donation_info(boolean): obs.set_scene_item_enabled(SCENE, NEW_DONATION_INFO, boolean)