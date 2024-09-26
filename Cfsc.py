import os
import json
import asyncio
import logging
import sys
from aiohttp import ClientSession, ClientTimeout, TCPConnector
import ipaddress

# Constants
CONFIG_FILE = "config.json"
THREADS = 4
TIMEOUT = 5
SIZE = 1024 * 128

def ss_input(prompt, default='', t=int):
    result = input('{}{}: '.format(
        prompt, (" [" + str(default) + "] (Enter for default)") if str(default) != '' else ''))
    if result == '':
        return default
    else:
        return t(result)

async def create_data(size=SIZE):
    created_size = 0
    while size > created_size:
        created_size += 512
        yield b"S" * 512

async def init():
    count = ss_input('Enter the number of IPs you need', 5)
    config = {
        "COUNT": count,
    }
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)
    print("Initialization complete. You can now run the script with `python3 main.py run`.")

async def find_speed_domain():
    print('Finding working speed test server...')
    speed_urls = open('speedtest_urls.txt', 'r').read().strip().split("\n") if os.path.exists('speedtest_urls.txt') else \
                 requests.get('https://raw.githubusercontent.com/SafaSafari/ss-cloud-scanner/main/speedtest_urls.txt').content.decode().split('\n')
    async with ClientSession() as session:
        for url in speed_urls:
            url = url.strip()
            try:
                async with session.get("https://" + url) as r:
                    if r.status != 429:
                        print("Selected Server:", url)
                        return url
            except:
                continue
    print("No working speed server found.")
    exit()

async def check(ip, speed_domain, f):
    global COUNT
    if COUNT <= 0:
        return

    async with ClientSession(connector=TCPConnector(), timeout=ClientTimeout(total=TIMEOUT)) as sess:
        try:
            async with sess.post(f'http://{speed_domain}/', data=create_data()) as r:
                if r.status != 200:
                    return
        except:
            return

    COUNT -= 1
    f.write(ip + "\n")
    logging.critical("Good IP found: {}".format(ip))

async def select(ips, speed_domain, f):
    tasks = []
    for ip in ips:
        try:
            network = ipaddress.ip_network(ip.strip(), strict=False)  # Allows both network ranges and single IPs
            for individual_ip in network:
                tasks.append(check(str(individual_ip), speed_domain, f))
        except ValueError as e:
            logging.error(f"Invalid IP/network format: {ip}. Error: {e}")
    await asyncio.gather(*tasks)

async def run():
    if not os.path.exists(CONFIG_FILE):
        print("Please initialize first: `python3 main.py init`")
        return

    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)

    global COUNT
    COUNT = config["COUNT"]

    if not os.path.exists('ips.txt'):
        print('Please download ips.txt file')
        exit()

    cloud_ips = open('ips.txt', 'r').read().strip().split("\n")
    speed_domain = await find_speed_domain()

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.CRITICAL, datefmt="%H:%M:%S")
    
    with open("good.txt", "a") as f:
        for i in range(0, len(cloud_ips), THREADS):
            batch = cloud_ips[i:i+THREADS]
            await select(batch, speed_domain, f)

async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <init|run>")
        return

    command = sys.argv[1]

    if command == "init":
        await init()
    elif command == "run":
        await run()
    else:
        print("Usage: python3 main.py <init|run>")

if __name__ == "__main__":
    asyncio.run(main())
