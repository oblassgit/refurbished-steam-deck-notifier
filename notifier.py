# refurbished steam deck notifier - notifies when refurbished steam deck is in stock
#  Copyright (C) <2025>  <Oliver Blass>
# 
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from time import gmtime, strftime
import requests
from discord_webhook import DiscordWebhook
import os
import csv
from datetime import datetime
import argparse
import json


# Default values
DEFAULT_COUNTRY_CODE = 'DE'
DEFAULT_WEBHOOK_URL = "https://discord.com/api/webhooks/some_webhook"

class SteamDeckModel:
    def __init__(self, version: str, package_id: str, is_oled: bool, is_new: bool = False):
        self.version = version
        self.package_id = package_id
        self.is_oled = is_oled
        self.is_new = is_new

def get_daily_csv_path(csv_dir: str, country_code: str) -> str:
    """Generate the CSV file path for today's date and country"""
    if not csv_dir:
        return ""
    
    # Create directory if it doesn't exist
    os.makedirs(csv_dir, exist_ok=True)
    
    # Generate filename with today's date and country code
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"{country_code}_{today}.csv"
    return os.path.join(csv_dir, filename)

def initialize_logs(csv_dir: str, country_code: str):
    """Initialize CSV log file if it doesn't exist"""
    if not csv_dir:
        return
        
    log_file = get_daily_csv_path(csv_dir, country_code)
    if not os.path.exists(log_file):
        with open(log_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['unix_timestamp', 'storage_gb', 
                        'display_type', 'package_id', 'available'])

def log_availability_data(version, package_id, available, is_oled, csv_dir: str, country_code: str):
    """Log availability data in CSV format"""
    if not csv_dir:
        return
        
    log_file = get_daily_csv_path(csv_dir, country_code)
    timestamp = datetime.now()
    unix_timestamp = int(timestamp.timestamp())
    display_type = "OLED" if is_oled else "LCD"
    
    with open(log_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([unix_timestamp, version, display_type, package_id, available])

def superduperscraper(model: SteamDeckModel, csv_dir: str, country_code: str, webhook_url: str, webhook_url_new: str, role_ids: dict):
    # Build Steam API URL with country code
    url = f'https://api.steampowered.com/IPhysicalGoodsService/CheckInventoryAvailableByPackage/v1?origin=https:%2F%2Fstore.steampowered.com&country_code={country_code}&packageid='
    
    # Determine which webhook URL to use based on model type
    active_webhook_url = webhook_url_new if (model.is_new and webhook_url_new) else webhook_url
    
    # Create Discord webhook
    webhook = DiscordWebhook(url=active_webhook_url, content="error")
    
    roleIdWithCountry = role_ids.get(model.package_id, "") if role_ids else ""
    
    oldvalue = ""
    # Get previous availability from file
    if os.path.isfile(f"{model.package_id}_{country_code}.txt"):
        with open(f"{model.package_id}_{country_code}.txt", "r") as file_read:
            oldvalue = file_read.read()
    
    print("Previous value: " + oldvalue)

    try:
        # Make request to Steam API
        response = requests.get(url+model.package_id, timeout=10)
        response.raise_for_status()
        
        # Get availability status
        availability = str(response.json()["response"]["inventory_available"])
        current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        
        print(f"{current_time} >> {model.version}GB {'OLED' if model.is_oled else 'LCD'} Result: {availability}")
        
        # Save new availability to file
        with open(f"{model.package_id}_{country_code}.txt", "w") as file:
            file.write(availability)
        
        # Check if status changed
        status_changed = oldvalue != availability and oldvalue != ""
        
        # Log data
        log_availability_data(model.version, model.package_id, availability == "True", model.is_oled, csv_dir, country_code)
        
        # Send Discord notification only on status change
        if status_changed:
            display_type = "OLED" if model.is_oled else "LCD"
            condition_type = "new" if model.is_new else "refurbished"
            if availability == "True":
                # Include role ping only if role ID exists
                role_ping = f" <@&{roleIdWithCountry}>" if roleIdWithCountry else ""
                webhook.content = f"{condition_type} {model.version}GB {display_type} steam deck available{role_ping}"
            else:
                webhook.content = f"{condition_type} {model.version}GB {display_type} steam deck not available"
            webhook.execute()
            
    except requests.RequestException as e:
        print(f"Error fetching data for {model.version}GB: {e}")
        log_availability_data(model.version, model.package_id, False, model.is_oled, csv_dir, country_code)
    except Exception as e:
        print(f"Unexpected error for {model.version}GB: {e}")

def load_role_mapping(role_file: str) -> dict:
    """Load role mapping from JSON file"""
    if not role_file or not os.path.exists(role_file):
        return {}
    
    try:
        with open(role_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not load role mapping from {role_file}: {e}")
        return {}

def main():
    """Main function to check all Steam Deck models"""
    parser = argparse.ArgumentParser(description='Check Steam Deck availability and optionally log to CSV')
    parser.add_argument('--include-new-models', action='store_true', help='Include request for new steam decks (not just refurbs)')
    parser.add_argument('--csv-dir', help='Directory path for daily CSV log files')
    parser.add_argument('--country-code', default=DEFAULT_COUNTRY_CODE, 
                       help=f'Country code for Steam API (default: {DEFAULT_COUNTRY_CODE})')
    parser.add_argument('--webhook-url', default=DEFAULT_WEBHOOK_URL,
                       help='Discord webhook URL for notifications')
    parser.add_argument('--webhook-url-new', help='Discord webhook URL for seperate new model notifications (optional, defaults to --webhook-url)')
    parser.add_argument('--role-mapping', help='JSON file containing package_id to role_id mapping')
    parser.add_argument('--csv-log', help='Deprecated: This option is no longer supported (last supported version v2.0.0).')
    
    args = parser.parse_args()

    if args.csv_log:
        print("w: Deprecated: This option is no longer supported (last supported version v2.0.0).")
    
    csv_dir = args.csv_dir if args.csv_dir else ""
    initialize_logs(csv_dir, args.country_code)
    
    # Load role mapping
    role_ids = load_role_mapping(args.role_mapping)
    
    if csv_dir:
        today_file = get_daily_csv_path(csv_dir, args.country_code)
        print(f"Logging enabled to: {today_file}")
    else:
        print("Logging disabled")
    
    print(f"Country code: {args.country_code}")
    print(f"Webhook URL: {args.webhook_url}")
    
    # Steam Deck models
    refurbModels = [
        #REFURBISHED
        SteamDeckModel("64", "903905", False),    # 64gb lcd
        SteamDeckModel("256", "903906", False),   # 256gb lcd  
        SteamDeckModel("512", "903907", False),   # 512gb lcd
        SteamDeckModel("512", "1202542", True),   # 512gb oled
        SteamDeckModel("1024", "1202547", True),  # 1tb oled
    ]   

    newModels = [
        #NEW
        SteamDeckModel("512", "946113", True, is_new=True),    # 512gb oled
        SteamDeckModel("1024", "946114", True, is_new=True),   # 1tb oled
        # Optional: Phasing out LCD models
        SteamDeckModel("256", "595604", False, is_new=True),   # 256gb lcd

        #64gb and 512gb lcd aren't being sold as new anymore
        #SteamDeckModel("64", "595603", False, is_new=True),    # 64gb lcd
        #SteamDeckModel("512", "595605", False, is_new=True),   # 512gb lcd
    ]

    if args.include_new_models:
        models = refurbModels + newModels
    else:
        models = refurbModels

    if role_ids:
        print(f"Role mapping loaded: {len(role_ids)} entries")
        if not len(role_ids) == len(models):
            print("Warning..............Role mapping doesn't match models. Pinging roles won't work as expected.")
    else:
        print("No role mapping - notifications will not ping roles")
    
    for model in models:
        superduperscraper(model, csv_dir, 
                         args.country_code, args.webhook_url, args.webhook_url_new, role_ids)

if __name__ == "__main__":
    main()