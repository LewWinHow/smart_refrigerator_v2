import os
import django
import time
import requests
import logging
from datetime import datetime

# ========== Django Initialization ==========
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_refrigerator_v2.settings')
django.setup()

from monitoring.models import Item  # Ensure model path is correct

# ========== Raspberry Pi Flask Interface ==========
FLASK_URL = "http://10.147.18.220:5005/receive"  # Your Raspberry Pi Flask IP + Port


def send_to_raspberry(data):
    """Send control signal to Raspberry Pi"""
    try:
        response = requests.post(FLASK_URL, json=data, timeout=3)
        response.raise_for_status()  # If return is not 200, will trigger exception
        resp_json = response.json()
        logging.info(f"✅ Raspberry Pi response: {resp_json}")
        print("✅ Raspberry Pi response:", resp_json)
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Send failed: {e}")
        print("❌ Send failed:", e)


def check_and_control_fans():
    """Check database status and decide whether to turn fans on/off"""
    try:
        item_list = Item.objects.all()
        has_items = item_list.exists()
    except Exception as e:
        logging.error(f"⚠️ Database access failed: {e}")
        print("⚠️ Database access failed:", e)
        return

    # Judgment logic
    if has_items:
        fan_1 = False
        fan_2 = False
        state = "Record detected -> Turn off fans"
    else:
        fan_2 = False
        fan_1 = False
        state = "No record -> Turn on fans"

    data = {"fan_1": fan_1, "fan_2": fan_2}

    send_to_raspberry(data)


def main():
    """Main loop, detect every 5 seconds"""
    print("🌀 Start scheduled task, detect every 5 seconds...")
    logging.info("=== Fan automatic control task started ===")

    while True:
        check_and_control_fans()
        time.sleep(5)  # Interval 5 seconds


if __name__ == "__main__":
    main()
