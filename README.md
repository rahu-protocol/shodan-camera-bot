📸 Shodan Camera Bot
A Telegram bot that maps publicly accessible webcams based on ZIP code searches using the Shodan API. Built for passive reconnaissance, OSINT research, and awareness around internet-exposed devices.

🔍 What It Does
This bot allows users to:

Scan for exposed cameras in a given ZIP code

Retrieve live screenshots and device metadata

View a downloadable, interactive map showing camera locations

It runs entirely through Telegram using commands like:
/cams 80113
/camsfull 80113
🛠️ Features
✅ Accepts US ZIP codes and converts them to GPS coordinates
✅ Uses Shodan API to search for open RTSP cameras and embedded web interfaces
✅ Displays screenshots (if available), IP addresses, org names, and product types
✅ Generates an interactive camera_map.html using Folium
✅ Fully self-contained and ready to deploy

📸 Demo
Example output from scanning ZIP code 80113:

📸 Open Camera Found
IP: 73.229.8.252
Product: Unknown
Org: Comcast
Location: LA (39.73915, -104.9847)
View on Shodan: https://www.shodan.io/host/73.229.8.252
Interactive map:
(Insert actual screenshots or screenshots from your Telegram bot if desired)

🚀 Getting Started
🔧 Requirements
pip install shodan python-telegram-bot geopy folium
🗝️ Set Your Keys
Replace your API keys in Camera_Bot.py:
SHODAN_API_KEY = 'your_shodan_api_key'
TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token'
▶️ Run It
python Camera_Bot.py
Open Telegram, talk to your bot, and try:
🔍 Commands
Command	Description
/start	Show usage instructions
/cams <zip>	Quick RTSP scan using port:554
/camsfull <zip>	Full recon sweep across ports + products
🧠 How It Works
The bot sends Shodan queries like:
port:554 has_screenshot:true geo:39.6475,-104.9872
It loops through multiple queries:

RTSP cameras
MJPEG streamers
GoAhead-Webs
Dahua NVRs
Generic “Network Camera” titles
Results are deduplicated and returned with screenshots and location data.

⚠️ Ethical Use
This tool is designed for educational and research purposes only. It does not hack or exploit any systems — it only displays what is publicly visible via Shodan.
⚠️ Do not attempt to access or interfere with any device found using this bot unless you are authorized to do so.


📄 License
MIT License

