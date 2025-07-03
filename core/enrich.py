import scapy.all as scapy

def find_mac_address(ip):
    """
    Sends ARP packet to destination IP
    Args:
        ip (str): destination IP
    Returns:
        str: raw output of MAC address
    """
    packet1 = scapy.ARP(pdst=ip)
    etherpacket = scapy.Ether(dst = 'ff:ff:ff:ff:ff:ff')

    broadcast_packet = etherpacket/packet1
    ans, unans = scapy.srp(broadcast_packet, timeout=3)

    src_mac_address = (ans[0][1]).src
    return(src_mac_address)





scan("192.168.1.254")
