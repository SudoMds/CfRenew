#!/usr/bin/env python3
import subprocess
import sys
import os
import CloudFlare
import argparse

CONFIG_FILE = 'settings.txt'
IP_FILE = 'ips.txt'

def install_requirements(requirements_file):
    """Install packages from a requirements file."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])

# Check if dependencies are installed
try:
    import cloudflare
except ImportError:
    print("Installing packages from requirements.txt...")
    install_requirements("requirements.txt")

def print_header():
    """Print a beautiful header."""
    header = """
====================================================
         Code Written by MDS - Cloudflare DNS Updater
====================================================
    """
    print(header)

def init_settings():
    """Initialize settings and save them to the configuration file."""
    print_header()
    
    email = input("Enter your Cloudflare login email: ").strip()
    api_key = input("Enter your Cloudflare global API key: ").strip()
    zone = input("Enter your Cloudflare zone name (e.g., mydomain.com): ").strip()
    subdomain = input("Enter the base subdomain to use (e.g., subdomain.mydomain.com): ").strip()

    # Initialize Cloudflare API client to fetch the zone_id
    cf = CloudFlare.CloudFlare(email=email, token=api_key)
    
    # Get zone ID
    zones = cf.zones.get(params={"name": zone})
    if len(zones) == 0:
        print(f"Could not find Cloudflare zone {zone}, please check the domain.")
        sys.exit(2)
    zone_id = zones[0]["id"]

    # Save settings to file
    with open(CONFIG_FILE, 'w') as f:
        f.write(f"email={email}\n")
        f.write(f"api_key={api_key}\n")
        f.write(f"zone_id={zone_id}\n")
        f.write(f"zone={zone}\n")
        f.write(f"subdomain={subdomain}\n")
    print(f"Settings initialized and saved to {CONFIG_FILE}.")

def read_settings():
    """Read settings from the configuration file."""
    if not os.path.exists(CONFIG_FILE):
        print(f"Configuration file '{CONFIG_FILE}' not found. Please initialize settings first.")
        sys.exit(2)

    settings = {}
    with open(CONFIG_FILE, 'r') as f:
        for line in f:
            key, value = line.strip().split('=', 1)
            settings[key] = value
    return settings

def read_ips_from_file():
    """Read IP addresses from the IP file."""
    if not os.path.exists(IP_FILE):
        print(f"IP file '{IP_FILE}' not found.")
        sys.exit(2)

    with open(IP_FILE, 'r') as file:
        ips = [line.strip() for line in file if line.strip()]
    return ips

def create_records():
    """Create A records for each IP address using the Cloudflare API."""
    print_header()

    settings = read_settings()
    cf = CloudFlare.CloudFlare(email=settings['email'], token=settings['api_key'])
    zone_id = settings['zone_id']
    base_subdomain = settings['subdomain']

    ips = read_ips_from_file()
    num_ips = len(ips)
    print(f"Found {num_ips} IP addresses in the file.")

    # Use a fixed name for all records
    record_name = base_subdomain  # Assuming base_subdomain includes the full domain path

    # Create A records for each IP address
    for ip_address in ips:
        print(f"Creating A record for {record_name} with IP {ip_address}")

        a_record = {
            "type": "A",
            "name": record_name,
            "ttl": 60,  # TTL of 1 minute
            "content": ip_address,
            "proxied": False  # Set to True if you want Cloudflare's proxy features
        }

        try:
            cf.zones.dns_records.post(zone_id, data=a_record)
            print(f"Successfully created A record: {record_name} -> {ip_address}")
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            print(f"Error creating A record for {record_name}: {e}")

    print(f"Created {num_ips} A records successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cloudflare DNS A Record Updater")
    parser.add_argument("action", choices=["iscript", "rscript"], help="Specify 'iscript' to initialize settings or 'rscript' to run the script")
    args = parser.parse_args()

    if args.action == "iscript":
        init_settings()
    elif args.action == "rscript":
        create_records()
