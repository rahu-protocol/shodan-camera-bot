import shodan
import logging
import base64
import folium
from time import sleep
from geopy.geocoders import Nominatim
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- KEYS ---
SHODAN_API_KEY = 'your_shodan_api_key'
TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token'

# --- INIT ---
api = shodan.Shodan(SHODAN_API_KEY)
geolocator = Nominatim(user_agent="camera-bot")
logging.basicConfig(level=logging.INFO)

# --- ZIP to GEO ---
def zip_to_geo(zip_code):
    location = geolocator.geocode({'postalcode': zip_code, 'country': 'US'})
    return (location.latitude, location.longitude) if location else None

# --- Generate Folium Map ---
def generate_map(results, center):
    m = folium.Map(location=center, zoom_start=11)
    for match in results['matches']:
        ip = match.get('ip_str')
        lat = match['location'].get('latitude')
        lon = match['location'].get('longitude')
        org = match.get('org', 'Unknown')
        popup = f"<b>{ip}</b><br>{org}<br><a href='https://www.shodan.io/host/{ip}'>View on Shodan</a>"
        folium.Marker([lat, lon], popup=popup).add_to(m)
    m.save("camera_map.html")

# --- /start handler ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "👋 <b>Welcome to Camera Recon Bot!</b>\n\n"
        "You can use the following commands:\n\n"
        "🔍 <b>Quick Scan:</b>\n"
        "<code>/cams 90001</code> – Scan for open RTSP cameras in a ZIP code\n\n"
        "🧠 <b>Full Recon Sweep:</b>\n"
        "<code>/camsfull 90001</code> – Scan for a broader set of public cameras\n\n"
        "You'll receive screenshots, metadata, and a camera map file 📍"
    )
    await update.message.reply_text(welcome, parse_mode='HTML')

# --- /cams handler (quick search) ---
async def cams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /cams <zip>")
        return

    zip_code = context.args[0]
    coords = zip_to_geo(zip_code)
    if not coords:
        await update.message.reply_text("Could not find that ZIP code.")
        return

    lat, lon = coords
    query = f'port:554 has_screenshot:true geo:{lat},{lon}'

    try:
        results = api.search(query)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        return

    if results['total'] == 0:
        await update.message.reply_text("No cameras found in that area.")
        return

    for match in results['matches']:
        ip = match.get('ip_str')
        org = match.get('org', 'Unknown')
        product = match.get('product', 'Unknown')
        location = match.get('location', {})
        city = location.get('city', 'Unknown')
        lat = location.get('latitude', 'N/A')
        lon = location.get('longitude', 'N/A')

        text = (
            f"📸 <b>Open Camera Found</b>\n"
            f"<b>IP:</b> {ip}\n"
            f"<b>Product:</b> {product}\n"
            f"<b>Org:</b> {org}\n"
            f"<b>Location:</b> {city} ({lat}, {lon})\n"
            f"<a href='https://www.shodan.io/host/{ip}'>View on Shodan</a>"
        )

        screenshot_data = match.get('screenshot', {}).get('data')
        if screenshot_data:
            screenshot_bytes = base64.b64decode(screenshot_data)
            await update.message.reply_photo(photo=screenshot_bytes, caption=text, parse_mode='HTML')
        else:
            await update.message.reply_text(text, parse_mode='HTML')

    generate_map(results, coords)
    await update.message.reply_document(document=open("camera_map.html", "rb"), filename="camera_map.html")

# --- /camsfull handler (broad recon) ---
async def camsfull(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /camsfull <zip>")
        return

    zip_code = context.args[0]
    coords = zip_to_geo(zip_code)
    if not coords:
        await update.message.reply_text("Could not find that ZIP code.")
        return

    lat, lon = coords

    queries = [
        f'port:554 has_screenshot:true geo:{lat},{lon}',
        f'port:81 product:"GoAhead-Webs" has_screenshot:true geo:{lat},{lon}',
        f'"server: MJPEG-Streamer" has_screenshot:true geo:{lat},{lon}',
        f'product:"Dahua" has_screenshot:true geo:{lat},{lon}',
        f'title:"Network Camera" has_screenshot:true geo:{lat},{lon}'
    ]

    all_matches = {}
    for query in queries:
        try:
            results = api.search(query)
            for match in results.get('matches', []):
                ip = match.get('ip_str')
                if ip and ip not in all_matches:
                    all_matches[ip] = match
            sleep(1)  # avoid Shodan API rate limits
        except Exception as e:
            await update.message.reply_text(f"Error running query: {query}\n{e}")
            continue

    if not all_matches:
        await update.message.reply_text("No cameras found in that area.")
        return

    for ip, match in all_matches.items():
        org = match.get('org', 'Unknown')
        product = match.get('product', 'Unknown')
        location = match.get('location', {})
        city = location.get('city', 'Unknown')
        lat = location.get('latitude', 'N/A')
        lon = location.get('longitude', 'N/A')

        text = (
            f"📸 <b>Open Camera Found</b>\n"
            f"<b>IP:</b> {ip}\n"
            f"<b>Product:</b> {product}\n"
            f"<b>Org:</b> {org}\n"
            f"<b>Location:</b> {city} ({lat}, {lon})\n"
            f"<a href='https://www.shodan.io/host/{ip}'>View on Shodan</a>"
        )

        screenshot_data = match.get('screenshot', {}).get('data')
        if screenshot_data:
            screenshot_bytes = base64.b64decode(screenshot_data)
            await update.message.reply_photo(photo=screenshot_bytes, caption=text, parse_mode='HTML')
        else:
            await update.message.reply_text(text, parse_mode='HTML')

    generate_map({'matches': list(all_matches.values())}, coords)
    await update.message.reply_document(document=open("camera_map.html", "rb"), filename="camera_map.html")

# --- MAIN ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cams", cams))
    app.add_handler(CommandHandler("camsfull", camsfull))
    app.run_polling()
