#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import TCLink

class FourHostOneSwitchTopo(Topo):
    def __init__(self):
        Topo.__init__(self)

        # Add 1 switch
        s1 = self.addSwitch('s1')

        # Add 4 hosts and connect to switch
        for i in range(1, 5):
            host = self.addHost(f'h{i}')
            self.addLink(host, s1)

if __name__ == '__main__':
    topo = FourHostOneSwitchTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    # Print network and enter CLI for testing
    print("*** Dumping host connections")
    for host in net.hosts:
        print(host.name, host.intf(), host.IP())

    CLI(net)

    net.stop()
