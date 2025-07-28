import logging
import time
import subprocess
import sys
from core.node import Node

if sys.platform.startswith("win"):
  class HiddenPopen(subprocess.Popen):
    def __init__(self, *args, **kwargs):
      si = subprocess.STARTUPINFO()
      si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
      kwargs["startupinfo"] = si
      super().__init__(*args, **kwargs)
  subprocess.Popen = HiddenPopen

def get_os_info(node_list: list[Node], verbose: bool = False) -> list[Node]:
  """
  Uses nmap to OS scan each node in a node list
  Args:
      node_list (List(Node)): List of Nodes to scan and update OS
  """
  try:
    import nmap
  except ImportError:
    nmap = None
    print("Warning: python-nmap not installed, skipping nmap-based enrichment.")

  logging.info("[-] running get_os_info")
  start = time.time()
  nm = nmap.PortScanner()
  for node in node_list:
    if node.ip is not None:
      os_list = nm.scan(
          node.ip, arguments='-O -F --max-os-tries 1 --osscan-limit')['scan']
    if not os_list:
      node.os = None
    else:
      if node.ip in os_list and 'osmatch' in os_list[node.ip]:
        os_list = nm.scan(
            node.ip, arguments='-O')['scan'][node.ip]['osmatch'][0]
        os_name = os_list['name']
        os_accuracy = os_list['accuracy']
        os_line = os_list['line']
        os_summary = {"OS: ": os_name,
                      "accuracy: ": os_accuracy,
                      "line: ": os_line}
        node.os = os_summary

  duration = time.time() - start
  logging.info(" [ ] get_os_info complete:".ljust(35) + f"{duration:.2f} s")
  return node_list
