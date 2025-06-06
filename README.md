[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Y8Y41BZ8SM)

[![](https://dcbadge.limes.pink/api/server/5gpFTMkvJn)](https://discord.gg/5gpFTMkvJn)
# Steam Deck Availability Notifier
This script checks the availability of refurbished Steam Decks on Steam and sends notifications to a specified Discord webhook. It runs by querying Steam's API and comparing the current stock status with previously stored values.

## 🚀 Features
- Checks the availability of refurbished Steam Decks for a configurable country
- Sends notifications via a **Discord webhook** when stock availability changes
- Supports different Steam Deck models (LCD & OLED versions)
- Prevents duplicate notifications by storing the last known stock status
- **Optional CSV logging** for availability statistics
- **Configurable Discord role pings** via JSON file
- **Command-line arguments** for easy configuration

## 📋 Requirements
### Install Dependencies
Ensure you have **Python 3.x** installed. Then, install the required dependencies using:
```sh
pip install requests discord-webhook
```

## 🛠 Setup & Usage

### Basic Usage
```sh
python steam_deck_checker.py --webhook-url "https://discord.com/api/webhooks/YOUR_WEBHOOK"
```

### Command Line Arguments
- `--webhook-url`: Discord webhook URL for notifications (**required**)
- `--country-code`: Country code for Steam API (default: `DE`)
- `--role-mapping`: JSON file containing Discord role mappings (optional)
- `--csv-log`: Path to CSV file for logging availability data (optional)

### Full Example
```sh
python steam_deck_checker.py \
  --country-code US \
  --webhook-url "https://discord.com/api/webhooks/YOUR_WEBHOOK" \
  --role-mapping roles.json \
  --csv-log availability.csv
```

## 🔧 Configuration Files

### Discord Role Mapping (Optional)
Create a `roles.json` file to enable role pings when Steam Decks become available:

```json
{
  "903905": "1343233406791716875",
  "903906": "1343233552896229508", 
  "903907": "1343233731795881994",
  "1202542": "1343233909655343234",
  "1202547": "1343234052957802670"
}
```

**Format:** `"package_id": "discord_role_id"`

### Country Codes
Find valid country codes [here](https://github.com/RudeySH/SteamCountries/blob/master/json/countries.json).

## 🖥 Steam Deck Models Monitored
The script checks these models automatically:
- **64GB LCD** (Package ID: 903905)
- **256GB LCD** (Package ID: 903906)
- **512GB LCD** (Package ID: 903907)
- **512GB OLED** (Package ID: 1202542)
- **1TB OLED** (Package ID: 1202547)

## 🔧 How It Works
1. The script requests stock availability for various Steam Deck models from the Steam API
2. It compares the latest availability status with the previously stored value in text files
3. If availability changes, it sends a **Discord notification**
4. If role mapping is provided, it pings the appropriate Discord role
5. Optionally logs all availability data to a CSV file for statistics

## 📊 CSV Logging
When enabled with `--csv-log`, the script creates a CSV file with these columns:
- `unix_timestamp`: When the check was performed
- `storage_gb`: Storage capacity (64, 256, 512, 1024)
- `display_type`: LCD or OLED
- `package_id`: Steam package identifier
- `available`: True/False availability status

## ❗ Important Notes
- This script **does not continuously run**—use a cron job (Linux/macOS) or Task Scheduler (Windows) to automate execution
- You need **a Raspberry Pi or a server** if you want it running 24/7

### Configuring a cron job (for Linux/macOS):
```bash
$ crontab -e
```

Add this line to run every 3 minutes:
```bash
*/3 * * * * /usr/bin/python3 /path/to/steam_deck_checker.py --webhook-url "YOUR_WEBHOOK" >> /path/to/logfile.log 2>&1
```

Save and exit. The cron job will start automatically!

## ❤️ Support
If you find this useful, consider buying me a coffee on [**Ko-fi**](https://ko-fi.com/Y8Y41BZ8SM)

## 🥇 Special Thanks
Massive thanks to [leo-petrucci](https://github.com/leo-petrucci) for rewriting parts of the code and guiding me toward properly using the Steam API — the project was way worse before that! Your help made a huge improvement.

