import json

class Node:
    def __init__(self, ip=None, mac_address=None, ports=None, latency=None, dns=None) -> None:
        self.ip: str | None = ip
        self.latency = f"{latency:.1f} ms" if latency is not None else None
        self.mac_address: str | None = mac_address
        self.ports: dict[int, str] | None = ports
        self.dns: str | None = dns

    def __str__(self) -> str:
        return f"{self.ip:<15}  {self.latency or '*':<7}  {self.mac_address or '*':<17} {self.dns or '*':<5} {self.ports}"
    
    def to_dict(self) -> dict:
        return {
            "ip": self.ip,
            "latency": self.latency,
            "mac_address": self.mac_address,
            "dns": self.dns,
            "ports": self.ports,
        }