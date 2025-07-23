import sys
import logging
import json
import shutil

from rich.logging import RichHandler
from dataclasses import dataclass
from core import trace_route, enrich, trace_report, enrich_nmap

@dataclass
class Cfg:
  target: str
  max_hops: int = 40
  timeout: float = 0.02
  logging_level: str = "INFO"


def run_traceroute(
  *,
  logging_level: str = 'INFO',
  target: str,
  dns: bool = False,
  mac: bool = False,
  ports: bool = False,
  all: bool = False,
  os: bool = False, #nmap
  nocli: bool = False,
  json_output: bool = True,
):
  print(logging_level)
  cfg = Cfg(target=target, logging_level=logging_level.upper())
  # Logging
  logging.basicConfig(
    level=getattr(logging, (cfg.logging_level)),
    format="%(message)s",
    handlers=[
      RichHandler(
        show_time=False,
        show_level=True,
        show_path=False,
        markup=False
      )
    ],
  )

  hops = trace_route.run_traceroute(cfg.target, cfg.max_hops, cfg.timeout)
  
  node_list = enrich.create_node_list(hops)
  
  if not hops:
    logging.error(f"Trace route failed to {cfg.target}")
    sys.exit(1)
  
  #  Enrichments
  if dns or all:
    node_list = enrich.reverse_dns_lookup(node_list)
  if mac or all:
    node_list = enrich.find_mac_address(node_list)
  if ports or all:
    node_list = enrich.scan_ports(node_list)
  if os or all:
    node_list = enrich_nmap.get_os_info(node_list)
  
  if not nocli:
    for node in node_list:
      print(node)

  if json_output:
    jsondata = trace_report.conv_json(target, node_list)
    print(json.dumps(jsondata, indent=2))
    