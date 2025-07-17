import scapy.all as scapy
import socket, logging, time, subprocess, shutil

from core.node import Node

def create_node_list(ip_list):
    """
    Takes a list of IP's and converts them to a list of Node Objects
    Args:
        ip (List(Tuple)): list of IP's
    Returns:
        List(Node): List of Nodes with IP field filled
    """
    node_list = []

    for ip, latency in ip_list:
        node_list.append(Node(ip=ip, latency=latency))
    return node_list


def nslookup(ip: str) -> str | None:
    if not shutil.which('nslookup'):
        logging.ERROR('Missing command :nslookup')
        sys.exit(1)
    
    try:
        result = subprocess.run(
            ['nslookup', ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=0.5,
        )
        output = result.stdout.lower().splitlines()
        for line in output:
            # win
            if "name:" in line:
                dns = line.split(':')[1].strip()
                return dns
    except:
        print('error')

def reverse_dns_lookup(node_list: list[str]) -> list[str]:
    s = time.time()
    logging.info('[ ] running reverse_dns_lookup')
    count = 0
    for node in node_list:
        if node.ip != "*":
            try:
                logging.debug(f"resolving {node.ip}")
                node.dns = nslookup(node.ip)
                if node.dns: count += 1
            except Exception:
                node.dns = None

    e = time.time()
    logging.info(f'[i] DNS Responses:'.ljust(33) + f'{count}')
    logging.info(f"[+] reverse_dns_lookup complete: {e - s:.2f} s")
    return node_list


def find_mac_address(node_list):
    """Sends ARP packet to destination IP"""
    
    logging.info('[ ] running find_mac_address')
    src_mac_address = ''
    for node in node_list:
        target_ip_address = scapy.ARP(pdst=node.ip)
        target_hardware_address = scapy.Ether(dst = 'ff:ff:ff:ff:ff:ff')

        broadcast_packet = target_hardware_address/target_ip_address
        ans, unans = scapy.srp(broadcast_packet, timeout=0.05, verbose=0)

        if ans:
            if src_mac_address == (ans[0][1]).src:
                node.mac_address = "LAYER 3"
                return node_list
            src_mac_address = (ans[0][1]).src
            node.mac_address = src_mac_address
    return node_list

def scan_ports(node_list):
    """
    Scans popular TCP ports of a given IP and returns dict of their status
    Args:
        node_list (List(Node)): List of Nodes to scan and update ports
    """
    logging.info('scanning ports')
    my_ip = scapy.get_if_addr(scapy.conf.iface)
    
    PORTS = {
        22:     "SSH",
        23:     "TELNET",
        53:     'DNS',
        80:     'HTTP',
        443:    'HTTPS',
    }

    for node in node_list:
        if node.ip != '*':
            replies = {}
            destination_ip = node.ip
            ip_layer = scapy.IP(src=my_ip, dst=destination_ip)
            for port in PORTS:
                tcp_layer = scapy.TCP(sport=12345, dport=port, seq=1000)
                response = scapy.sr1(ip_layer/tcp_layer, timeout=0.05, verbose=0)

                if response is None:
                    replies.update({port : 'filtered'})
                else:
                    if response['IP'].proto == 6:
                        if response['TCP'].flags == 'SA':
                            replies.update({port : 'open'})
                        else:
                            replies.update({port : 'closed'})
            
            node.ports = replies
    return node_list