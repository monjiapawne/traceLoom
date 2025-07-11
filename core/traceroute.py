import subprocess
import platform
import time
from typing import List, Tuple, Optional
import socket
import ipaddress
import logging
import re

# Constants
OS_NAME = platform.system()
MAX_HOPS = 30
PING_TIMEOUT=0.05  # seconds eg: 0.04 s = 40 ms

def _sanitize_host(host):
    try:
        ipaddress.IPv4Address(host)
        return host
    except ValueError:
        return socket.gethostbyname(host)

def _run_traceroute(host):
    results = []
    ttl = 1
    while ttl <= MAX_HOPS:

        if OS_NAME == 'Windows':
            cmd = ['ping', '-n', '1', '-i', str(ttl), '-w', str(PING_TIMEOUT * 1000), host]
        elif OS_NAME == 'Linux':
            cmd = ['ping', '-c', '1', '-t', str(ttl), '-W', str(PING_TIMEOUT), host]
        else:
            raise NotImplementedError(f"Unsupported OS: {OS_NAME}")
        
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end = time.time()
        latency = round((end - start) * 1000, 3)

        try:
            line = next(l for l in result.stdout.splitlines() if "from" in l.lower())
            if OS_NAME == 'Windows':
                hop_ip = line.split("from ")[1].split(":")[0]
            else:
                match = re.search(r'(?i)from ([\d\.]+)', line)
                hop_ip = match.group(1) if match else "*"

            results.append((hop_ip, latency))

            if hop_ip == host:
                return results

        except (IndexError, StopIteration):
            results.append(("*", None))

        ttl += 1

    logging.error(f'Traceroute failed\n        PING_TIMEOUT: {float(PING_TIMEOUT)*1000}')
    return []

def traceroute(host: str) -> List[Tuple[str, Optional[float]]]:
    """Runs and parses traceroute based on OS, returns list of hops and latency"""
    host = _sanitize_host(host)
    logging.info(f"Running traceroute for: {host}")
    logging.info(f"OS Detected: {OS_NAME}")
    
    route_list = _run_traceroute(host)

    logging.info(f"Route list\n\n{route_list}\n")

    return route_list