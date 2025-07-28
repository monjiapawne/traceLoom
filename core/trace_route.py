from scapy.all import IP, ICMP, sr, sr1, socket
from typing import Any
import logging
import time


def run_traceroute(
    target: str,
    MAX_HOPS: int = 40,
    timeout: float = 0.02
) -> list[tuple[str, float | None]]:

  count = 0
  logging.info("[ ] running traceroute to:".ljust(35) + f"{target}")
  start = time.time()

  responseIP = ""
  ttl = 1
  route = []

  try:
    target = socket.gethostbyname(target)
    logging.info("[+] resolved:".ljust(35) + f"{target}")
  except socket.gaierror:
    logging.error(f"failed to resolve {target}")
    return []

  target_online = sr1(IP(dst=target) / ICMP(),
                      timeout=timeout + 1,
                      verbose=0)

  if target_online:

    while ttl <= MAX_HOPS and target != responseIP:
      packet: Any = IP(dst=target, ttl=ttl) / ICMP()
      answered, _ = sr(packet, timeout=timeout, verbose=0)

      if answered:
        sent, reply = answered[0]
        responseIP = reply[IP].src
        logging.debug(" [i] hop:".ljust(35) + f"{responseIP}")
        route.append((responseIP,
                      (reply.time - sent.sent_time) * 1000))
        count += 1
      else:
        logging.debug(" [i] hop:".ljust(35) + "*")
        route.append((None, None))

      ttl += 1

    duration = time.time() - start
    logging.info(" [+] traceroute complete:".ljust(35) + f"{duration:.2f} s")
    logging.info(" [+] ICMP responses:".ljust(35) + f"{count}")
    return route

  else:
    logging.error(f"{target} is not reachable.")
    return []
