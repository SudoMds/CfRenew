import aiohttp
import asyncio
import time
import logging
import os
import argparse
import csv
from typing import List, Tuple

# Configure logging
logging.basicConfig(
    format="%(asctime)s: %(levelname)s: %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Constants for speed tests
DOWNLOAD_TEST_URL = "https://speed.hetzner.de/10MB.bin"  # 10MB test file
UPLOAD_TEST_URL = "https://httpbin.org/post"             # Upload test endpoint
DATA_SIZE_MB = 5                                         # Size of upload/download data in MB
DATA_SIZE_BYTES = DATA_SIZE_MB * 1024 * 1024            # Convert MB to Bytes

# Timeout settings
CONNECT_TIMEOUT = 10
TOTAL_TIMEOUT = 30

async def measure_download_speed(session: aiohttp.ClientSession, url: str, size: int = DATA_SIZE_BYTES) -> float:
    """
    Measures the download speed by downloading data from the specified URL.

    Args:
        session (ClientSession): The aiohttp session to use for the request.
        url (str): The URL to download data from.
        size (int, optional): The maximum number of bytes to download. Defaults to DATA_SIZE_BYTES.

    Returns:
        float: Download speed in Mbps.
    """
    start_time = time.time()
    downloaded = 0
    try:
        async with session.get(url) as response:
            if response.status != 200:
                logging.error(f"Download failed with status code {response.status}")
                return 0.0
            async for chunk in response.content.iter_chunked(1024):
                downloaded += len(chunk)
                if downloaded >= size:
                    break
        end_time = time.time()
        duration = end_time - start_time
        speed_mbps = (downloaded * 8) / (duration * 1_000_000)  # bits per second to Mbps
        return round(speed_mbps, 2)
    except Exception as e:
        logging.error(f"Download speed test failed: {e}")
        return 0.0

async def measure_upload_speed(session: aiohttp.ClientSession, url: str, size: int = DATA_SIZE_BYTES) -> float:
    """
    Measures the upload speed by uploading data to the specified URL.

    Args:
        session (ClientSession): The aiohttp session to use for the request.
        url (str): The URL to upload data to.
        size (int, optional): The size of data to upload in bytes. Defaults to DATA_SIZE_BYTES.

    Returns:
        float: Upload speed in Mbps.
    """
    data = os.urandom(size)  # Generate random data for upload
    start_time = time.time()
    try:
        async with session.post(url, data=data) as response:
            if response.status != 200:
                logging.error(f"Upload failed with status code {response.status}")
                return 0.0
            await response.text()  # Ensure the request completes
        end_time = time.time()
        duration = end_time - start_time
        speed_mbps = (size * 8) / (duration * 1_000_000)  # bits per second to Mbps
        return round(speed_mbps, 2)
    except Exception as e:
        logging.error(f"Upload speed test failed: {e}")
        return 0.0

async def check_proxy(session: aiohttp.ClientSession, proxy: str, secure: bool = False) -> Tuple[str, str, float, float]:
    """
    Checks if the proxy is operational and measures its download and upload speeds.

    Args:
        session (ClientSession): The aiohttp session to use for the request.
        proxy (str): The proxy address in the format ip:port.
        secure (bool, optional): Whether to use an HTTPS proxy. Defaults to False.

    Returns:
        Tuple[str, str, float, float]: Proxy IP, Port, Download Speed (Mbps), Upload Speed (Mbps)
    """
    ip, port = proxy.split(':')
    proxy_url = f"http://{ip}:{port}" if not secure else f"https://{ip}:{port}"
    # Configure proxy for session
    connector = aiohttp.TCPConnector(ssl=False)  # Adjust SSL as needed
    try:
        proxy_auth = None  # Add authentication if required
        test_session = aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=TOTAL_TIMEOUT))
        # Test connectivity by accessing a known website
        try:
            async with test_session.get("https://www.google.com", proxy=proxy_url, proxy_auth=proxy_auth) as resp:
                if resp.status != 200:
                    logging.warning(f"Proxy {proxy} is not functional. Status code: {resp.status}")
                    await test_session.close()
                    return (ip, port, 0.0, 0.0)
        except Exception as e:
            logging.warning(f"Proxy {proxy} connection failed: {e}")
            await test_session.close()
            return (ip, port, 0.0, 0.0)

        # If proxy is functional, perform speed tests
        download_speed = await measure_download_speed(test_session, DOWNLOAD_TEST_URL)
        upload_speed = await measure_upload_speed(test_session, UPLOAD_TEST_URL)
        await test_session.close()
        return (ip, port, download_speed, upload_speed)
    except Exception as e:
        logging.error(f"Error testing proxy {proxy}: {e}")
        return (ip, port, 0.0, 0.0)

async def test_proxies(proxies: List[str], secure: bool = False, concurrency: int = 100) -> List[Tuple[str, str, float, float]]:
    """
    Tests a list of proxies concurrently.

    Args:
        proxies (List[str]): List of proxies in the format ip:port.
        secure (bool, optional): Whether to use HTTPS proxies. Defaults to False.
        concurrency (int, optional): Number of concurrent tasks. Defaults to 100.

    Returns:
        List[Tuple[str, str, float, float]]: List of tuples containing proxy IP, Port, Download Speed, Upload Speed.
    """
    semaphore = asyncio.Semaphore(concurrency)
    results = []

    async def sem_check(proxy):
        async with semaphore:
            result = await check_proxy(session, proxy, secure)
            if result[2] > 0 or result[3] > 0:
                results.append(result)
            return

    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(sem_check(proxy)) for proxy in proxies]
        await asyncio.gather(*tasks)
    return results

def read_proxies_from_file(file_path: str) -> List[str]:
    """
    Reads a list of proxies from a file.

    Args:
        file_path (str): Path to the proxy list file.

    Returns:
        List[str]: List of proxies in the format ip:port.
    """
    proxies = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                proxy = line.strip()
                if proxy and ':' in proxy:
                    proxies.append(proxy)
    except Exception as e:
        logging.error(f"Failed to read proxies from file {file_path}: {e}")
    return proxies

def write_results_to_csv(results: List[Tuple[str, str, float, float]], output_file: str):
    """
    Writes the test results to a CSV file.

    Args:
        results (List[Tuple[str, str, float, float]]): List of test results.
        output_file (str): Path to the output CSV file.
    """
    try:
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['IP', 'Port', 'Download Speed (Mbps)', 'Upload Speed (Mbps)'])
            for row in results:
                writer.writerow(row)
        logging.info(f"Results written to {output_file}")
    except Exception as e:
        logging.error(f"Failed to write results to CSV: {e}")

def parse_arguments():
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="VLESS and VMess Proxy Speed Tester")
    parser.add_argument('--input', '-i', type=str, required=True, help='Path to the input file containing proxies (ip:port)')
    parser.add_argument('--output', '-o', type=str, default='proxy_results.csv', help='Path to the output CSV file')
    parser.add_argument('--secure', '-s', action='store_true', help='Use HTTPS proxies')
    parser.add_argument('--concurrency', '-c', type=int, default=100, help='Number of concurrent tasks')
    return parser.parse_args()

def main():
    args = parse_arguments()
    proxies = read_proxies_from_file(args.input)
    if not proxies:
        logging.error("No valid proxies found. Exiting.")
        return

    logging.info(f"Starting proxy tests for {len(proxies)} proxies with concurrency={args.concurrency} ...")
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(test_proxies(proxies, secure=args.secure, concurrency=args.concurrency))
    if results:
        write_results_to_csv(results, args.output)
    else:
        logging.info("No proxies passed the tests.")

if __name__ == "__main__":
    main()
