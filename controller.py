import sys
import logging
import json
import shutil

from rich.logging import RichHandler
from dataclasses import dataclass
from core import trace_route, enrich, trace_report, enrich_nmap
from core.node import Node

@dataclass
class Cfg:
  target: str
  max_hops: int = 40
  timeout: float = 0.02
  logging_level: str = "INFO"


def enrich_nodes(node_list, *, dns=False, mac=False, ports=False, os=False, all=False, return_nodes=False):
    from core.node import Node
    node_objs = [n if isinstance(n, Node) else Node(**n) for n in node_list]

    if dns or all:
        node_objs = enrich.reverse_dns_lookup(node_objs)
    if mac or all:
        node_objs = enrich.find_mac_address(node_objs)
    if ports or all:
        node_objs = enrich.scan_ports(node_objs)
    if os or all:
        node_objs = enrich_nmap.get_os_info(node_objs)

    return node_objs if return_nodes else [n.to_dict() for n in node_objs]


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
  
  node_list = enrich_nodes(node_list, dns=dns, mac=mac, ports=ports, os=os, all=all, return_nodes=True)
  
  if not nocli:
    for node in node_list:
      print(node)

  if json_output:
    return trace_report.conv_json(target, node_list)