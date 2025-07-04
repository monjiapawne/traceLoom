import scapy.all as scapy
import psutil

def find_mac_address(ip):
    """
    Sends ARP packet to destination IP
    Args:
        ip (str): destination IP
    Returns:
        str: raw output of MAC address
    """
    traget_ip_address = scapy.ARP(pdst=ip)
    target_hardware_address = scapy.Ether(dst = 'ff:ff:ff:ff:ff:ff')

    broadcast_packet = target_hardware_address/traget_ip_address
    ans, unans = scapy.srp(broadcast_packet, timeout=0.1)

    if unans:
        return None
    else:
        src_mac_address = (ans[0][1]).src
        return(src_mac_address)
    



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