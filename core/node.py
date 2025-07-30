class Node:
  def __init__(
      self,
      ip: str | None = None,
      latency: float | None = None,
      mac_address: str | None = None,
      ports: dict[int, str] | None = {},
      dns: str | None = None,
      os: dict | None = None
  ) -> None:

    self.ip = ip
    self.latency = f"{float(latency):.1f} ms" if latency is not None else None
    self.mac_address = mac_address
    self.ports = ports
    self.dns = dns
    self.os = os

  def __str__(self) -> str:
    sorted_ports = sorted(self.ports.items())
    sorted_ports_by_key = dict(sorted_ports)
    return (
        f"{self.ip or '*':<20} "
        f"{self.latency or '*':<10} "
        f"{self.mac_address or '*':<20} "
        f"{self.dns or '*':<50} "
        f"{sorted_ports_by_key}"
        f"\t{self.os or ''}"
    )

  def to_dict(self) -> dict:
    return {
        "ip": self.ip,
        "latency": self.latency,
        "mac_address": self.mac_address,
        "dns": self.dns,
        "ports": self.ports,
        "os": self.os
    }
