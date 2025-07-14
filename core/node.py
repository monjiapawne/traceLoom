class Node:
    def __init__(self, ip=None, mac_address=None, ports=None, latency=None) -> None:
        self.ip: str | None = ip
        self.latency: float | None = latency
        self.mac_address: str | None = mac_address
        self.ports: dict[int, str] | None = ports

    def __str__(self) -> str:
        latency = f"{self.latency:.1f} ms" if self.latency is not None else "-"
        return f"{self.ip}  {latency} {self.mac_address or '-':<17} {self.ports}"