class hop:
    def __init__(self, ip=None, mac_address=None, ports=None, latency=None):
        self.ip= ip
        self.mac_address = mac_address
        self.ports = ports
        self.latency = latency

    @property
    def ip(self):
        return self._ip
    
    @ip.setter
    def ip(self, value):
        self._ip = value

    @property
    def mac_address(self):
        return self._mac_address
    
    @mac_address.setter
    def mac_address(self, value):
        self._mac_address = value

    @property
    def ports(self):
        return self._ports
    
    @ports.setter
    def ports(self, value):
        self._ports = value

    @property
    def latency(self):
        return self._latency
    
    @latency.setter
    def latency(self, value):
        self._latency = value

    def __str__(self):
        if self.latency is None:
            return f"{self.ip} : {self.mac_address} : {self.ports} : {self.latency}"
        else:
            return f"{self.ip} : {self.mac_address} : {self.ports} : {self.latency}ms"