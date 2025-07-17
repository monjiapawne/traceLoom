from scapy.all import IP, ICMP, sr, sr1, socket
from typing import List, Tuple, Any
import logging, time

def run_traceroute(target: str) -> list[tuple[str, float | None]]:   
    count = 0
    logging.info(f'[ ] running traceroute to:'.ljust(33) + f'{target}')
    s = time.time()
    MAX_HOPS    = 40
    ttl         = 1
    timeout     = 0.02
    responseIP  = ''
    route: list[tuple[str, str | None]] = []
    
    try:
        target = socket.gethostbyname(target)
        logging.info(f'[+] resolved:'.ljust(33) + f'{target}')
    except socket.gaierror:
        logging.error(f'failed to resolve {target}')
        return []
    
    target_online = sr1(IP(dst=target) / ICMP(), timeout=timeout+1, verbose=0)
    
    if target_online:
    
        while ttl <= MAX_HOPS and target != responseIP:
            packet: Any = IP(dst=target, ttl=ttl) / ICMP()
            answered, _ = sr(packet, timeout=timeout, verbose=0)

            if answered:
                sent, reply = answered[0]
                responseIP = reply[IP].src
                route.append((responseIP, (reply.time - sent.sent_time) * 1000))
                count += 1
            else:
                route.append(('*', None))

            ttl += 1
            
        e = time.time()
        logging.info(f"[+] traceroute complete:".ljust(31) + f"{(e - s):>6.2f} s")
        logging.info(f'[i] ICMP responses:'.ljust(33) + f'{count}')
        return route
    
    else:
        logging.error(f'{target} is not reachable.')
        return []