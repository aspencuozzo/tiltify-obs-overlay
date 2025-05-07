# tiltify-obs-overlay
This project hooks into the Tiltify API to look for new donations to a Tiltify campaign, displays new donation data in an OBS scene, and sends an alert to the Twitch chat. Created for use in [Gaming For Global Change](https://gamingforglobalchange.org) events.

Before following the instructions below, make sure you [download the project here](https://github.com/aspencuozzo/tiltify-obs-overlay/archive/refs/heads/main.zip) and un-zip it.

https://github.com/user-attachments/assets/9c2f8818-02bc-414f-9b81-f63ff4f2d01e

## OBS setup
### All operating systems
1. Ensure OBS is updated to the most recent version.
2. Download and install the [Source Copy plugin.](https://obsproject.com/forum/resources/source-copy.1261/)
3. Restart OBS and make sure the scene collection you want to use is open.
4. Go to `Tools > Source Copy > Load Scene`, and select the corresponding file for your operating system:
    1. On Windows: Select `donation_bar_scene_windows.json` inside the `windows` folder.
    2. On macOS/Linux: Select `donation_bar_scene_macos_linux.json` inside the `macos_linux` folder.
5. Add the `Donation Bar` scene to the scene you want the overlay to appear on.
6. Go to `Tools > WebSocket Server Settings` and ensure `Enable WebSocket Server` is toggled.
7. Keep this window open as you will need to enter the server password and port to your credentials file during installation.

> ⚠️ The default font for the text sources is Arial. If your system does not have Arial installed, you must change their font for them to show up on your stream preview. You may customize the overlay however you like in the `Donation Bar` scene, but **do not rename any of the sources**.

## Program install
### All operating systems
Install Python if it's not already on your system. The minimum version is Python 3.7.
If you don't already have it, you can download it [from the Python website.](https://www.python.org/downloads/) If you're installing it on Windows, **you must select the `Add to PATH` option in the installer.**

Then, proceed with the following steps for your operating system.

### Windows
Go to the `windows` folder and open (double-click) the following files:
1. `install_windows.bat`
2. `run_windows.bat`

### macOS / Linux
Open the `macos_linux` folder in your terminal and run the following commands:
1. `sh install_macos_linux.sh`
2. `sh run_macos_linux.sh`

### Manual installation
If you're familiar with Python and don't want to use any of the included scripts, proceed with the following steps:
1. Open the `app` folder in your terminal.
2. Install required modules from `requirements.txt`.
3. Edit `credentials-example.json` with your credentials, and rename it to `credentials.json` when you're done.
4. Run `main.py`.

## Update credentials
If you need to update your credentials at any point (ie. change the Tiltify campaign you want alerts for), the credentials file is located in the `app` folder. Just edit `credentials.json` with a text editor like Notepad or TextEdit and save it when you're done.
