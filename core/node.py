import json

class Node:
    def __init__(
        self, 
        ip: str | None = None, 
        latency: float | None = None, 
        mac_address: str | None = None, 
        ports: dict[int, str] | None = None, 
        dns: str | None = None
    ) -> None:
        
        self.ip = ip
        self.latency = f"{latency:.1f} ms" if latency is not None else None
        self.mac_address = mac_address
        self.ports = ports
        self.dns = dns

    def __str__(self) -> str:
        return f"{self.ip:<15}  {self.latency or '*':<7}  {self.mac_address or '*':<17} {self.dns or '*':<15} {self.ports}"
    
    def to_dict(self) -> dict:
        return {
            "ip": self.ip,
            "latency": self.latency,
            "mac_address": self.mac_address,
            "dns": self.dns,
            "ports": self.ports,
        }