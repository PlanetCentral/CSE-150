from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class FinalController(object):
    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)

    def do_final(self, packet, packet_in, port_on_switch, switch_id):
        # Extract IPv4 and ICMP packets if present
        ip_packet = packet.find('ipv4')
        icmp_packet = packet.find('icmp')
        srcip = str(ip_packet.srcip) if ip_packet else None
        dstip = str(ip_packet.dstip) if ip_packet else None
        proto = ip_packet.protocol if ip_packet else None

        # Allow ARP packets to flood (for address resolution)
        if packet.type == packet.ARP_TYPE:
            msg = of.ofp_packet_out()
            msg.data = packet_in
            msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            self.connection.send(msg)
            return

        # Only handle IPv4 packets from here on!
        if not ip_packet:
            return  # Ignore/don't crash on non-IPv4/non-ARP packets

        # -- FIREWALL RULES --

        # 1. Untrusted Host (h_untrust) cannot:
        #    a) send ICMP to any internal host or the server
        #    b) send any IP traffic to the LLM Server
        if srcip == '108.35.24.113':
            if proto == 1 and (dstip.startswith('128.114.1.') or dstip.startswith('128.114.2.') or dstip == '128.114.3.178'):
                return  # Block ICMP to internal/server
            if dstip == '128.114.3.178':
                return  # Block all IP traffic to LLM server

        # 2. Trusted Host (h_trust) cannot:
        #    a) send ICMP to Department B (128.114.2.x)
        #    b) send any IP traffic to the server
        #    c) send ICMP to the server
        if srcip == '192.47.38.109':
            if proto == 1 and dstip.startswith('128.114.2.'):
                return
            if dstip == '128.114.3.178':
                return
            if proto == 1 and dstip == '128.114.3.178':
                return

        # 3. Dept A (128.114.1.x) and Dept B (128.114.2.x) cannot send ICMP to each other
        if proto == 1:
            if (srcip.startswith('128.114.1.') and dstip.startswith('128.114.2.')) or \
               (srcip.startswith('128.114.2.') and dstip.startswith('128.114.1.')):
                return

        # -- ROUTING/FORWARDING LOGIC --

        # Port mapping (from topology):
        #   s1 (core): 2-Floor1, 3-Floor2, 4-Server, 10-trust, 11-untrust
        #   s2: 1-4 hosts, 5-uplink
        #   s3: 1-4 hosts, 5-uplink
        #   s4: 1-server, 5-uplink

        out_port = None
        if switch_id == 1:
            # Core switch
            if dstip.startswith('128.114.1.'):
                out_port = 2
            elif dstip.startswith('128.114.2.'):
                out_port = 3
            elif dstip == '128.114.3.178':
                out_port = 4
            elif dstip == '192.47.38.109':
                out_port = 10
            elif dstip == '108.35.24.113':
                out_port = 11
        elif switch_id == 2:
            # Floor 1 switch
            if dstip == '128.114.1.101':
                out_port = 1
            elif dstip == '128.114.1.102':
                out_port = 2
            elif dstip == '128.114.1.103':
                out_port = 3
            elif dstip == '128.114.1.104':
                out_port = 4
            else:
                out_port = 5  # uplink to core
        elif switch_id == 3:
            # Floor 2 switch
            if dstip == '128.114.2.201':
                out_port = 1
            elif dstip == '128.114.2.202':
                out_port = 2
            elif dstip == '128.114.2.203':
                out_port = 3
            elif dstip == '128.114.2.204':
                out_port = 4
            else:
                out_port = 5  # uplink to core
        elif switch_id == 4:
            # Data center/server switch
            if dstip == '128.114.3.178':
                out_port = 1
            else:
                out_port = 5  # uplink to core

        if out_port is not None:
            # Forward packet and install flow
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet, port_on_switch)
            msg.idle_timeout = 30
            msg.hard_timeout = 60
            msg.actions.append(of.ofp_action_output(port=out_port))
            msg.data = packet_in
            self.connection.send(msg)
        # else, do nothing (drop if unmatched)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return
        packet_in = event.ofp
        self.do_final(packet, packet_in, event.port, event.dpid)

def launch():
    def start_switch(event):
        log.debug("Controlling %s" % (event.connection,))
        FinalController(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
