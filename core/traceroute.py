from scapy.all import IP, ICMP, sr, socket
from typing import List, Tuple, Any

def run_traceroute(target: str) -> list[tuple[str, str | None]]:
    
    MAX_HOPS    = 30
    ttl         = 1
    timeout     = 0.2
    responseIP  = ''
    route: list[tuple[str, str | None]] = []
    target = socket.gethostbyname(target)
    
    while ttl <= MAX_HOPS and target != responseIP:
        packet: Any = IP(dst=target, ttl=ttl) / ICMP()
        answered, _ = sr(packet, timeout=timeout, verbose=0)

        if answered:
            sent, reply = answered[0]
            responseIP = reply[IP].src
            route.append((responseIP, (reply.time - sent.sent_time) * 1000))
        else:
            route.append(('*', None))

        ttl += 1

    return route