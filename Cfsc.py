import os
import json
import asyncio
import logging
import sys
from aiohttp import ClientSession, ClientTimeout, TCPConnector
import ipaddress
import aiofiles
import requests  # Ensure this is available if used

# Constants
CONFIG_FILE = "config.json"
THREADS = 2  # Adjust threads for testing
TIMEOUT = 15  # Timeout for responses
SIZE = 1024 * 128  # Size of the data being sent
SECURE = "s"  # HTTP/HTTPS toggle

# Global variables
SPEED_DOMAIN = None
TYPE = "speed"  # Change this to "server" or other types as needed
NUM_IPS = 10  # Number of IPs to handle per batch

async def create_data(size=SIZE):
    created_size = 0
    while size > created_size:
        created_size += 512
        yield b"S" * 512

async def check(ip):
    global SPEED_DOMAIN
    logging.debug(f"Attempting to connect to {SPEED_DOMAIN} from {ip}")
    
    async with ClientSession(connector=TCPConnector(), timeout=ClientTimeout(total=TIMEOUT)) as sess:
        try:
            async with sess.post(
                'http{}://{}/{}up'.format(SECURE, SPEED_DOMAIN, '__' if SPEED_DOMAIN == 'speed.cloudflare.com' else ''),
                data=create_data()
            ) as r:
                if r.status != 200:
                    return
        except Exception as e:
            logging.error(f"Error checking IP {ip}: {e}")
            return
    
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

async def main():
    global SPEED_DOMAIN

    if TYPE == 'speed':
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
    
    # Process IPs in batches of THREADS
    for i in range(-(-len(cloud_ips) // THREADS)):  # Divide IPs into chunks of THREADS
        batch = cloud_ips[i * THREADS:(i + 1) * THREADS]
        await asyncio.gather(*[select(ip_range) for ip_range in batch])

    # Optional success log
    # logging.critical('All tasks completed!')

# Example IPs list (cloud_ips) to test
cloud_ips = [
    '192.168.1.0/30',  # Replace with your actual list of IP ranges
    '10.0.0.0/30'
]

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
