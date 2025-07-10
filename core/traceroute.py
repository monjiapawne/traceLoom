import subprocess
import platform
import time
from typing import List, Tuple, Optional

# Constants
OS_NAME = platform.system()
MAX_HOPS=30

def _run_traceroute_windows(host):
    results = []
    ttl = 1
    while ttl <= MAX_HOPS:
        cmd = ['ping', '-n', '1', '-i', str(ttl), '-w', '200', host]  # ping -n 1 -i 2 -w 200 8.8.8.8
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end = time.time()
        latency = round((end - start) * 1000, 3)

        try:
            line = next(l for l in result.stdout.splitlines() if "from" in l.lower())
            hop_ip = line.split("from ")[1].split(":")[0]
            results.append((hop_ip, latency))
            if hop_ip == host:
                return results

        except (IndexError, StopIteration):
            results.append(("*", None))

        ttl += 1

def _run_traceroute_unix(host):
    cmd = ["traceroute", "-q", "1",  host]
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout

    results = []
    for hops in output.splitlines()[1:]:
        if '*' in hops:
            results.append(('*', None))  # for null reponses
        elif '(' in hops and ')' in hops:
            # parse ip
            hop_ip = hops.split('(')[1].split(')')[0]
            # parse latency
            parts = hops.split()
            for i, p in enumerate(parts):
                if p.endswith('ms'):
                    latency = float(parts[i - 1])
                    results.append((hop_ip, latency))
                    break
    return results

def traceroute(host: str) -> List[Tuple[str, Optional[float]]]:
    """Runs and parses traceroute based on OS, returns list of hops and latency"""
    if OS_NAME == 'Windows':
        return _run_traceroute_windows(host)
    elif OS_NAME == 'Linux':
        return _run_traceroute_unix(host)
    else:
        raise NotImplementedError(f"Unsupported OS: {OS_NAME}")