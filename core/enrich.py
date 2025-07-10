import scapy.all as scapy
import psutil

from hop import hop

ip_list = [('192.168.1.254', 10.592), ('10.0.30.1', 10.892), ('*', None), ('142.124.41.181', 10.01), ('*', None), ('*', None), ('*', None), ('142.124.127.112', 15.196), ('142.124.127.3', 12.534), ('142.250.166.254', 12.385), ('192.178.86.87', 12.636), ('142.250.235.213', 12.389), ('8.8.8.8', 12.773)]
node_list = []

def create_node_list(ip_list):
    for ip, latency in ip_list:
        print(ip, latency)
        node_list.append(hop(ip=ip, latency=latency))
    return node_list


def find_mac_address(node_list):
    """
    Sends ARP packet to destination IP
    Args:
        ip (str): destination IP
    Returns:
        str: raw output of MAC address
    """
    for node in node_list:
        target_ip_address = scapy.ARP(pdst=node.ip)
        target_hardware_address = scapy.Ether(dst = 'ff:ff:ff:ff:ff:ff')

        broadcast_packet = target_hardware_address/target_ip_address
        ans, unans = scapy.srp(broadcast_packet, timeout=0.1)

        if unans:
            print("None")
        else:
            src_mac_address = (ans[0][1]).src
            node.mac_address = src_mac_address
    

def scan_ports(ip):
    """
    Scans popular TCP ports of a given IP and returns dict of their status
    Args:
        ip (str): destination IP
    Returns:
        dict: dictionary of ports and their scan results
    """
    replies = {}
    nics = psutil.net_if_addrs()
    nic_keys = list(nics.keys())
    nic = nic_keys[0]

    PORTS = {
        20 :    'FTP', 
        21:     "SFTP",
        22:     "SSH",
        23:     "Telnet",
        25:     "SMTP",
        53:     "DNS",
        80:     "Telnet",
        110:    "POP3",
        111:    "rpcbind",
        443:    "HTTPS",
    }
    
    my_ip = scapy.get_if_addr(scapy.conf.iface)
    my_ip = scapy.get_if_addr(nic)
    ip_layer = scapy.IP(src=my_ip, dst=ip)

    for port in PORTS:
        tcp_layer = scapy.TCP(sport=12345, dport=port, seq=1000)
        response = scapy.sr1(ip_layer/tcp_layer, timeout=0.1)
        if response is None:
            replies.update({port : 'filtered/closed'})
        else:
            replies.update({port : 'open'})

    return replies

create_node_list(ip_list)
find_mac_address(node_list)
for node in node_list:
    print(node)
