Cloudflare DNS Updater Script
Description
This script automates the process of updating Cloudflare DNS A records for a given subdomain with a list of IP addresses from a file. It uses Cloudflare's API to manage DNS records and is highly useful for dynamic IP updates, especially in cloud environments.

Features
Automatically creates A records for a list of IP addresses.
Designed to use Cloudflare's Global API key and login credentials.
Supports multiple IPs from an external file (ips.txt).
Saves and loads configuration settings (settings.txt) for easy re-use.
Easy initialization of settings through the iscript command.
Provides a clear interface using argparse for user interaction.
Requirements
Make sure to install the dependencies before running the script. The script relies on the Cloudflare Python library.

Install Python 3.x.
Install the required dependencies by running:
bash
Copy code
pip install -r requirements.txt
The script requires the following package:

cloudflare (Cloudflare API wrapper)
Installation
Clone the repository
bash
Copy code
git clone https://github.com/your-username/cloudflare-dns-updater.git
cd cloudflare-dns-updater
Install dependencies
bash
Copy code
pip install -r requirements.txt
Configuration
Before using the script, you need to set up your Cloudflare credentials and configuration.

1. Initialize Configuration
Run the following command to start the configuration setup:

bash
Copy code
python3 script.py iscript
This command will prompt you for the following information:

Cloudflare login email
Cloudflare global API key
Cloudflare zone name (e.g., mydomain.com)
Subdomain to update (e.g., sub.mydomain.com)
The configuration will be saved in a settings.txt file.

2. IP Addresses File
Create a file named ips.txt containing the list of IP addresses, one per line, that you wish to add to the DNS records:

Copy code
192.0.2.1
203.0.113.5
198.51.100.7
Usage
Creating DNS Records
Once the configuration is set up and the IP file is created, run the script to create the A records:

bash
Copy code
python3 script.py rscript
This will read the IP addresses from the ips.txt file and create A records for each IP under the specified subdomain.

Files
script.py: The main script that manages Cloudflare DNS A records.
requirements.txt: Contains the necessary Python packages.
settings.txt: Stores Cloudflare API credentials and domain settings (generated after initialization).
ips.txt: A list of IP addresses to update the DNS A records for.
License
This project is licensed under the MIT License. See the LICENSE file for more details.
