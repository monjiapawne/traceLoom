import subprocess
import platform

# Constants
OS_NAME = platform.system()

def run_traceroute(host):
    """
    Runs traceroute command
    Args:
        host (str): destination host or IP
    Returns:
        str: raw output of traceroute command
    """
    cmd = ["tracert", host] if OS_NAME == 'Windows' else ["traceroute", "-q", "1",  host]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def parse_traceroute(output):
    """
    Parses and returns trace route output
    Args:
        output (str): raw traceroute output
    """
    results = []
    if OS_NAME == 'Windows':
        print("Windows")
    if OS_NAME == 'Linux':
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
        print(results)
        return results
    return ""

def traceroute(host):
    output = run_traceroute(host)
    return parse_traceroute(output)
