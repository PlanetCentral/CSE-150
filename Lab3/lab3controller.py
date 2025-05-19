# lab3controller.py
#
# POX Controller: Lab 3 Simple Firewall (Fixed Version)

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.arp import arp
from pox.lib.packet.ipv4 import ipv4

log = core.getLogger()

class Firewall(object):
    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)
        log.debug("Firewall controller initialized for %s", connection)

    def install_rule(self, match, action=None, priority=100, idle_timeout=10, hard_timeout=30):
        """Install a flow rule on the switch."""
        msg = of.ofp_flow_mod()
        msg.match = match
        msg.idle_timeout = idle_timeout
        msg.hard_timeout = hard_timeout
        msg.priority = priority
        if action:
            msg.actions.append(action)
        self.connection.send(msg)
        log.debug("Installed flow rule: %s", match)

    def do_firewall(self, packet, packet_in):
        if packet.type == ethernet.ARP_TYPE:
            # Accept and flood ARP packets
            action = of.ofp_action_output(port=of.OFPP_FLOOD)
            match = of.ofp_match(dl_type=ethernet.ARP_TYPE)
            self.install_rule(match, action, priority=200)

            msg = of.ofp_packet_out()
            msg.data = packet_in
            msg.in_port = packet_in.in_port
            msg.actions.append(action)
            self.connection.send(msg)
            log.debug("Flooded ARP packet")

        elif packet.type == ethernet.IP_TYPE:
            ip_pkt = packet.find('ipv4')
            if ip_pkt is None:
                return

            if ip_pkt.protocol == ipv4.TCP_PROTOCOL:
                # Accept and flood TCP over IPv4
                action = of.ofp_action_output(port=of.OFPP_FLOOD)
                match = of.ofp_match(dl_type=ethernet.IP_TYPE, nw_proto=ipv4.TCP_PROTOCOL)
                self.install_rule(match, action, priority=150)

                msg = of.ofp_packet_out()
                msg.data = packet_in
                msg.in_port = packet_in.in_port
                msg.actions.append(action)
                self.connection.send(msg)
                log.debug("Flooded TCP IPv4 packet")

            else:
                # Drop all other IPv4 traffic
                match = of.ofp_match(dl_type=ethernet.IP_TYPE)
                self.install_rule(match, None, priority=100)
                log.debug("Dropped non-TCP IPv4 packet")

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return
        self.do_firewall(packet, event.ofp)

def launch():
    def start_switch(event):
        log.debug("Controlling %s", event.connection)
        Firewall(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
