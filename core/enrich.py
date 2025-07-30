import scapy.all as scapy
import logging
import time
import subprocess
import shutil
import sys
from core.node import Node


def create_node_list(ip_list):
  node_list = []

  for ip, latency in ip_list:
    node_list.append(Node(ip=ip, latency=latency))
  return node_list


# Helper functions
def nslookup(ip: str) -> str | None:
    if not shutil.which("nslookup"):
        raise RuntimeError("Missing command: nslookup")

    CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0

    try:
        result = subprocess.run(
            ["nslookup", ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=0.5,
            creationflags=CREATE_NO_WINDOW
        )
        output = result.stdout.lower().splitlines()
        for line in output:
            if "name:" in line:
                return line.split(":", 1)[1].strip()
            if "name =" in line:
                return line.split("=", 1)[1].strip()
    except Exception as e:
        logging.error(f"nslookup error: {e}")
    return None


# Core enrichment functions
def reverse_dns_lookup(node_list: list[Node]) -> list[Node]:
  start = time.time()
  logging.info("[-] running reverse_dns_lookup")
  count = 0

  for node in node_list:
    if not node.ip:
      continue
    logging.debug(f" [ ] looking up: {node.ip}")
    try:
      node.dns = nslookup(node.ip)
      if node.dns:
        logging.debug(f"  [+] resolved: {node.dns}")
        count += 1
    except RuntimeError as e:
      logging.error(e)
      sys.exit(1)
    except Exception:
      node.dns = None

  duration = time.time() - start
  logging.info(" [+] DNS Responses:".ljust(35) + f"{count}")
  logging.info(" [+] reverse_dns_lookup complete: ".ljust(
      35) + f"{duration:.2f} s")
  return node_list


def find_mac_address(node_list: list[Node]) -> list[Node]:
  logging.info("[-] running find_mac_address")
  start = time.time()
  src_mac_address = ""
  for node in node_list:
    target_ip_address = scapy.ARP(pdst=node.ip)
    target_hardware_address = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")

    broadcast_packet = target_hardware_address / target_ip_address
    ans, unans = scapy.srp(broadcast_packet, timeout=0.05, verbose=0)
    if not ans or (ans[0][1]).src == src_mac_address:
      node.mac_address = "LAYER 3"
      break
    src_mac_address = (ans[0][1]).src
    node.mac_address = src_mac_address
  duration = time.time() - start
  logging.info(" [+] find_mac_address complete:".ljust(
      35) + f"{duration:.2f} s")
  return node_list


def scan_ports_tcp(node_list: list[Node]) -> list[Node]:
  PORTS = {22: "SSH", 23: "TELNET", 53: "DNS", 80: "HTTP", 443: "HTTPS"}
  logging.info("[-] scanning ports [TCP]")
  my_ip = scapy.get_if_addr(scapy.conf.iface)

  open_port_counter = 0
  start = time.time()
  for node in node_list:
    if node.ip:
      replies = {}
      destination_ip = node.ip
      ip_layer = scapy.IP(src=my_ip, dst=destination_ip)
      for port in PORTS:
        tcp_layer = scapy.TCP(sport=12345, dport=port, seq=1000)
        response = scapy.sr1(ip_layer / tcp_layer,
                             timeout=0.05,
                             verbose=0)

        if response is None:
          replies.update({port: "filtered"})
        else:
          if response["IP"].proto == 6:
            if response["TCP"].flags == "SA":
              replies.update({port: "open"})
              open_port_counter += 1
            else:
              replies.update({port: "closed"})

      node.ports = node.ports | replies
      
  duration = time.time() - start
  logging.info(" [+] Open Ports:".ljust(35) + f"{open_port_counter}")
  logging.info(" [+] port scan complete: ".ljust(35) + f"{duration:.2f} s")
  return node_list

def scan_ports_udp(node_list: list[Node]) -> list[Node]:
  PORTS = {53: "DNS", 67: "DHCP", 68: "DHCP", 123: "NTP"}
  logging.info("[-] scanning ports [UDP]")
  my_ip = scapy.get_if_addr(scapy.conf.iface)

  start = time.time()
  for node in node_list:
    if node.ip:
      replies = {}
      destination_ip = node.ip
      ip_layer = scapy.IP(src=my_ip, dst=destination_ip)
      for port in PORTS:
        udp_layer = scapy.UDP(sport=12345, dport=port)
        response = scapy.sr1(ip_layer / udp_layer,
                             timeout=0.05,
                             verbose=0)
        if response is None:
          replies.update({port: "open | filtered"})
        else:
          if response.haslayer(scapy.ICMP):
            replies.update({port: "closed"})
          elif response.haslayer(scapy.UDP):
            replies.update({port: "open"})
          else:
            replies.update({port: "filtered"})

    node.ports = node.ports | replies

  duration = time.time() - start
  logging.info(" [+] port scan complete: ".ljust(35) + f"{duration:.2f} s")
  return node_list

my_node_list = [Node(ip='192.168.1.254', latency='0.5')]