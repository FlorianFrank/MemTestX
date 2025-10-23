class IPConfig:
    """
    Represents an IP configuration.

    Attributes:
        ip (str): The IP address.
        port (int): The port number. Defaults to 0.
        netmask (str): The network mask. Defaults to None.
    """

    def __init__(self, ip, port=0, netmask=None):
        self.ip = ip
        self.port = port
        self.netmask = netmask

    def __str__(self):
        return "IP: " + self.ip + " Port: " + str(self.port) + " Netmask: " + self.netmask

    def __repr__(self):
        return "{ip: \"" + self.ip + "\" port: " + str(self.port) + " Netmask: \"" + self.netmask + "\""

    def __dict__(self):
        return {"ip": self.ip, "port": self.port, "netmask": self.netmask}


class NetworkInterfaceConfig:
    """
    Represents a network interface configuration.

    Attributes:
        name (str): The name of the network interface.
        ip (str): The IP address associated with the interface.
        port (int): The port number associated with the interface.
    """

    def __init__(self, name: str, ip: str, port: int):
        """
        Initializes the NetworkInterfaceConfig instance.

        Args:
            name (str): The name of the network interface.
            ip (str): The IP address.
            port (int): The port number.
        """
        self.name = name
        self.ip = ip
        self.port = port
