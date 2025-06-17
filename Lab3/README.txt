CSE150 Lab 3 – Simple Firewall using POX Controller
===========================================


Files:
----------------
1. lab3controller.py      – POX controller implementing the firewall
2. lab3.pdf               – Screenshots and explanations for pingall, iperf, dpctl
3. README.txt             – This file

How to Run:
-----------
1. Place `lab3controller.py` in:
   ~/pox/pox/misc/

2. Start the POX controller in one terminal:
   sudo ~/pox/pox.py misc.lab3controller
   or to specify right port (for me): sudo ./pox.py openflow.of_01 --port=6653 misc.lab3controller

3. In a second terminal, start the Mininet topology:
   sudo python ~/lab3.py

4. Once in the Mininet CLI, run:
   - pingall            (should fail — ICMP blocked)
   - iperf h1 h2        (should succeed — TCP allowed)
   - dpctl dump-flows   (should show ARP/TCP flow entries)

Firewall Logic Implemented:
---------------------------
- All ARP packets are accepted and flooded.
- All TCP-over-IPv4 packets are accepted and flooded.
- All other IPv4 packets are dropped.
- Each permitted packet type results in a flow rule being installed using ofp_flow_mod.
- Switches handle traffic based on flow table entries to avoid controller overload.

Known Issues:
-------------
None.

Notes:
------
- Ensure POX controller is started before Mininet.
- Wait a few seconds after iperf before running dpctl dump-flows, so flows appear.

