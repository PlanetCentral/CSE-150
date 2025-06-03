#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI

class FinalTopo(Topo):
    def build(self):
        # Core switch
        core = self.addSwitch('s1')

        # Floor 1 switch and hosts
        s2 = self.addSwitch('s2')
        h101 = self.addHost('h101', ip='128.114.1.101/24', mac='00:00:00:00:01:01', defaultRoute='h101-eth0')
        h102 = self.addHost('h102', ip='128.114.1.102/24', mac='00:00:00:00:01:02', defaultRoute='h102-eth0')
        h103 = self.addHost('h103', ip='128.114.1.103/24', mac='00:00:00:00:01:03', defaultRoute='h103-eth0')
        h104 = self.addHost('h104', ip='128.114.1.104/24', mac='00:00:00:00:01:04', defaultRoute='h104-eth0')
        self.addLink(h101, s2, port2=1)
        self.addLink(h102, s2, port2=2)
        self.addLink(h103, s2, port2=3)
        self.addLink(h104, s2, port2=4)

        # Floor 2 switch and hosts
        s3 = self.addSwitch('s3')
        h201 = self.addHost('h201', ip='128.114.2.201/24', mac='00:00:00:00:02:01', defaultRoute='h201-eth0')
        h202 = self.addHost('h202', ip='128.114.2.202/24', mac='00:00:00:00:02:02', defaultRoute='h202-eth0')
        h203 = self.addHost('h203', ip='128.114.2.203/24', mac='00:00:00:00:02:03', defaultRoute='h203-eth0')
        h204 = self.addHost('h204', ip='128.114.2.204/24', mac='00:00:00:00:02:04', defaultRoute='h204-eth0')
        self.addLink(h201, s3, port2=1)
        self.addLink(h202, s3, port2=2)
        self.addLink(h203, s3, port2=3)
        self.addLink(h204, s3, port2=4)

        # LLM Server in data center switch
        s4 = self.addSwitch('s4')
        h_server = self.addHost('h_server', ip='128.114.3.178/24', mac='00:00:00:00:03:78', defaultRoute='h_server-eth0')
        self.addLink(h_server, s4, port2=1)

        # Trusted Host
        h_trust = self.addHost('h_trust', ip='192.47.38.109/24', mac='00:00:00:00:09:09', defaultRoute='h_trust-eth0')
        self.addLink(h_trust, core, port2=10)

        # Untrusted Host
        h_untrust = self.addHost('h_untrust', ip='108.35.24.113/24', mac='00:00:00:00:08:13', defaultRoute='h_untrust-eth0')
        self.addLink(h_untrust, core, port2=11)

        # Connect edge switches to core switch
        self.addLink(s2, core, port1=5, port2=2)
        self.addLink(s3, core, port1=5, port2=3)
        self.addLink(s4, core, port1=5, port2=4)

topos = {'finaltopo': (lambda: FinalTopo())}

def configure():
    controller = RemoteController('c0', ip='127.0.0.1', port=6633)
    net = Mininet(topo=FinalTopo(), controller=lambda name: controller)
    net.start()

    print("\n--- Hosts Information ---")
    for host in net.hosts:
        print(f"{host.name} -> IP: {host.IP()}, MAC: {host.MAC()}")

    print("\n--- Switches Information ---")
    for switch in net.switches:
        print(f"{switch.name} -> Ports: {len(switch.intfList())} interfaces")
        for intf in switch.intfList():
            print(f"   - {intf}")

    print("\n--- Links ---")
    for link in net.links:
        intf1 = link.intf1
        intf2 = link.intf2
        print(f"{intf1.node.name} ({intf1.name}) <--> {intf2.node.name} ({intf2.name})")

    CLI(net)
    net.stop()


if __name__ == '__main__':
    configure()