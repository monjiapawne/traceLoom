import subprocess
import platform
import time

# Constants
OS_NAME = platform.system()

def maxhops(host):
    """
    WIP
    Function to get total hops, could be useful for progress bar..
    """
    if OS_NAME == 'Windows':
        cmd = ['ping']

def windows_customtracert(host):
    """
    Speedy fast work around to manually tracert, as windows is slow and not customizable
    Args:
        host (str): destination host or IP
    Returns:
        list: list of ips in path
    Todo:
        needs latencys, will manually trace with time, as failed ttl don't return latency in windows
    """
    results = []
    ttl = 1
    while True:
        cmd = ['ping', '-n', '1', '-i', str(ttl), '-w', '200', host]  # ping -n 1 -i 2 -w 200 8.8.8.8
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end = time.time()
        latency = f'{round((end - start) * 1000, 3)}ms'

        try:
            line = next(l for l in result.stdout.splitlines() if "from" in l.lower())
            hop_ip = line.split("from ")[1].split(":")[0]
            results.append((hop_ip, latency))
            if hop_ip == host:
                return results
                break

        except (IndexError, StopIteration):
            results.append("*, None")

        ttl += 1


def parse_traceroute(output):
    """
    -> Linux only !
    Parses and returns trace route output
    Args:
        output (str): raw traceroute output
    """
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

def run_traceroute(host):
    """
    Runs traceroute command
    Args:
        host (str): destination host or IP
    Returns:
        str: raw output of traceroute command
    """
    if OS_NAME == 'Windows':
        results = windows_customtracert(host)
        return results
    if OS_NAME == 'Linux':
        cmd = ["traceroute", "-q", "1",  host]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return parse_traceroute(result.stdout)

def traceroute(host):
    #total_hops = maxhops(host)
    output = run_traceroute(host)
    return output