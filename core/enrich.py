import scapy.all as scapy

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

def find_mac_address(node_list):
    """
    Sends ARP packet to destination IP
    Args:
        node_list (List(Node)): List of Nodes to find mac addresses and update in Node List
    """
    for node in node_list:
        target_ip_address = scapy.ARP(pdst=node.ip)
        target_hardware_address = scapy.Ether(dst = 'ff:ff:ff:ff:ff:ff')

        broadcast_packet = target_hardware_address/target_ip_address
        ans, unans = scapy.srp(broadcast_packet, timeout=0.05, verbose=0)

        if ans:
            src_mac_address = (ans[0][1]).src
            node.mac_address = src_mac_address
    return node_list

def scan_ports(node_list):
    """
    Scans popular TCP ports of a given IP and returns dict of their status
    Args:
        node_list (List(Node)): List of Nodes to scan and update ports
    """
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