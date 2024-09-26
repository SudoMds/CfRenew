import os
import json
import asyncio
import logging
import sys

# Constants
CONFIG_FILE = "config.json"

def ss_input(prompt, default='', t=int):
    result = input('{}{}: '.format(
        prompt, (" [" + str(default) + "] (Enter for default)") if str(default) != '' else ''))
    if result == '':
        return default
    else:
        return t(result)

def init():
    config = {
        "COUNT": ss_input('Enter count of IPs you need', 5),
        "SPEED_DOMAIN": ss_input(
            'Enter domain of your personal server behind Cloudflare', 'speedtest.example.com', str),
        "SECURE": {'y': 's', 'n': ''}[ss_input('Secure (y. https, n. http)?', 'y', str)]
    }

    # Save config to file
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)

    print("Initialization complete. You can now run the script with `python3 main.py run`.")

def run():
    if not os.path.exists(CONFIG_FILE):
        print("Please initialize first: `python3 main.py init`")
        return

    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)

    COUNT = config["COUNT"]
    SPEED_DOMAIN = config["SPEED_DOMAIN"]
    SECURE = config["SECURE"]

    # Add your existing code logic here, using the SPEED_DOMAIN and SECURE as needed

    # Run additional script at the end
    exec(open("additional_script.py").read())

async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <init|run>")
        return

    command = sys.argv[1]

    if command == "init":
        init()
    elif command == "run":
        run()
    else:
        print("Usage: python3 main.py <init|run>")

if __name__ == "__main__":
    asyncio.run(main())
