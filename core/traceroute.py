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
    return output 

def traceroute(host):
    output = run_traceroute(host)
    return parse_traceroute(output)
