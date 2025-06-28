import scapy.all as scapy


def scan(ip):
    packet1 = scapy.ARP(pdst=ip)
    etherpacket = scapy.Ether(dst = 'ff:ff:ff:ff:ff:ff')

    broadcast_packet = etherpacket/packet1
    ans, unans = scapy.srp(broadcast_packet, timeout=10)
    src_mac_address = (ans[0][1]).src
    dst_mac_address = (ans[0][1]).dst
    ether_type = (ans[0][1]).type

    print(f'src: {src_mac_address}\ndst: {dst_mac_address}\ntype: {ether_type}')
    print(ans.summary())





scan("192.168.1.254")