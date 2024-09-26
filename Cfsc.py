import os
import json
import asyncio
import logging
import sys
from aiohttp import ClientSession, ClientTimeout, TCPConnector
import ipaddress
import aiofiles
import requests

# Constants
CONFIG_FILE = "config.json"
THREADS = 2  # Adjust threads for testing
TIMEOUT = 15  # Timeout for responses
SIZE = 1024 * 128  # Size of the data being sent
SECURE = "s"  # HTTP/HTTPS toggle
NUM_IPS = 10  # Number of IPs to handle per batch
COUNT = 5  # Default number of IPs to scan

# Global variables
SPEED_DOMAIN = None
cloud_ips = None

class fronting:
    def __init__(self, ip):
        self.ip = ip

    async def resolve(self, hostname: str, port: int = 0, family: int = socket.AF_INET):
        result = [
            {
                "hostname": hostname,
                "host": self.ip,
                "port": port,
                "family": family,
                "proto": 6,
                "flags": socket.AI_NUMERICHOST | socket.AI_NUMERICSERV,
            }
        ]
        return result



async def create_data(size=SIZE):
    created_size = 0
    while size > created_size:
        created_size += 512
        yield b"S" * 512

async def check(ip):
    global COUNT

    if COUNT <= 0:
        f.close()
        os._exit(1)

    # Handle 'speed' type
    async with ClientSession(connector=TCPConnector(resolver=fronting(ip)), timeout=ClientTimeout(total=TIMEOUT)) as sess:
        try:
            async with sess.post(
                'http{}://{}/{}up'.format(SECURE, SPEED_DOMAIN, '__' if SPEED_DOMAIN == 'speed.cloudflare.com' else ''),
                data=create_data()
            ) as r:
                if r.status != 200:
                    return
        except Exception as e:
            logging.error(f"Error accessing speed server for IP {ip}: {e}")
            return

    COUNT -= 1
    async with aiofiles.open("good_ips.txt", "a") as f:
        await f.write(ip + "\n")

    logging.critical(f"Found good IP: {ip}")

async def select(ips):
    ipas = ipaddress.ip_network(ips)
    print(f"Progress: {cloud_ips.index(ips) / len(cloud_ips) * 100:.2f}%", end='\r')

    collect = []
    for ip in ipas:
        collect.append(str(ip))
        if len(collect) % NUM_IPS == 0:
            await asyncio.gather(*[check(ip) for ip in collect])
            collect = []

    # Process remaining IPs if any
    if collect:
        await asyncio.gather(*[check(ip) for ip in collect])

async def get_working_worker(speed_urls):
    global SPEED_DOMAIN
    for url in speed_urls:
        url = url.strip()
        try:
            async with ClientSession() as session:
                async with session.get(f"https://{url}") as r:
                    if r.status != 429:
                        return url
        except Exception as e:
            logging.error(f"Error accessing {url}: {e}")
            continue
    return None

async def init():
    count = ss_input('Enter the number of IPs you need to check', 5)
    config = {"COUNT": count}
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)
    print("Initialization complete. You can now run the script with `python3 main.py run`.")

async def run():
    global SPEED_DOMAIN, cloud_ips

    if not os.path.exists(CONFIG_FILE):
        print("Please initialize first: `python3 main.py init`")
        return

    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
        global COUNT
        COUNT = config.get("COUNT", COUNT)

    # Find speed test server
    print('Finding worker', end='\r')
    speed_urls_sources = [
        open('speedtest_urls.txt', 'r').readlines() if os.path.exists('speedtest_urls.txt') else [],
        requests.get('https://raw.githubusercontent.com/SafaSafari/ss-cloud-scanner/main/speedtest_urls.txt').content.decode().split('\n')
    ]

    for speed_urls in speed_urls_sources:
        SPEED_DOMAIN = await get_working_worker(speed_urls)
        if SPEED_DOMAIN:
            break

    if SPEED_DOMAIN is None:
        print("No worker found")
        exit()

    print(f"Selected Worker: {SPEED_DOMAIN}")

    # Logging setup
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.CRITICAL, datefmt="%H:%M:%S")

    # Load IPs from 'ips.txt'
    if not os.path.exists('ips.txt'):
        print('Please download or provide the ips.txt file')
        return

    with open('ips.txt', 'r') as f:
        cloud_ips = f.read().strip().split("\n")

    # Process IPs in batches of THREADS
    for i in range(-(-len(cloud_ips) // THREADS)):  # Divide IPs into chunks of THREADS
        batch = cloud_ips[i * THREADS:(i + 1) * THREADS]
        await asyncio.gather(*[select(ip_range) for ip_range in batch])

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

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
