import socket, time

def sendicmp(target): 
    # AF_NET       - create a layer3 socket
    # SOCK_RAW     - instead of layer4, start crafting a raw socket
    # IPPROTO_ICMP - doesnt craft the icmp packet, tell the kernal where to target the raw sock, and to mark the protocol as '1'
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    # 08 = type icmp request
    # 00 = 
    packet = b'\x08\x00\00\00\x00\x00\x00\x00'

    while True:
        time.sleep(1)
        print(f'-> {packet}')
        s.sendto(packet, (target, 0))


def checksum(data):
    # padding if odd length
    if len(data) % 2 == 1:
        data += b'\x00'

    total = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i+1]

sendicmp("192.168.1.1")