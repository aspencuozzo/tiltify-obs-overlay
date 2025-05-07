from twitchio.ext import commands
from datetime import datetime
import threading, asyncio
import main

# Global bot variable
bot = None

class Bot(commands.Bot):
    # Class variables
    credentials = None
    channels = None

    def __init__(self):
        self.credentials = main.load_creds()
        super().__init__(
            token = self.credentials['twitch_access_token'],
            prefix = ' ',
            initial_channels = self.credentials['twitch_channel_names']
        )

    # Runs when bot is ready
    async def event_ready(self):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.channels = list(map(lambda c : self.get_channel(c), self.credentials['twitch_channel_names']))
        print(f"[{timestamp}] Twitch bot running.")
    
    # Lets us call _send_alert from synchronous code (done so in main.py)
    def send_alert(self, donor_name, donation_amount, donation_message):
        asyncio.run(self._send_alert(donor_name, donation_amount, donation_message))

    # Sends an alert to the Twitch channels listed in credentials.json['twitch_channel_names']
    async def _send_alert(self, donor_name, donation_amount, donation_message):
        message = f"We have a ${donation_amount} donation from {donor_name}"
        # Don't attach a donation message if there is none
        if donation_message is not None and donation_message != 'None':
            message += f" with the comment \"{donation_message}\""
        for channel in self.channels:
            await channel.send(message)

    # Lets us call _change_game from synchronous code (done so in main.py)
    def change_game(self, game_name):
        asyncio.run(self._change_game(game_name))

    # Sends a command to change the game in Twitch channels listed in credentials.json['twitch_channel_names']
    async def _change_game(self, game_name):
        message = f"!game {game_name}"
        for channel in self.channels:
            await channel.send(message)

# Startup routine
def run_bot():
    global bot
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = Bot()
    bot.run()

# Triggers startup routine (for use in other modules)
def initialize_twitch():
    bot_thread = threading.Thread(target = run_bot)
    bot_thread.start()