README.txt
==========

Lab4: Router Final Project

Rahil Prakash

Description:
------------
This project simulates an enterprise network with multi-floor departments, an LLM server, and both trusted and untrusted external hosts. It includes a Mininet-based topology and a POX controller to implement routing and enforce security policies.

1. Topology (Defined in final_skel.py):
---------------------------------------
The Mininet topology models a real-world enterprise setup, including:

Switches:
- s1: Core switch
- s2: Floor 1 (Department A)
- s3: Floor 2 (Department B)
- s4: Server room

Hosts:
- Department A: h101, h102, h103, h104 (128.114.1.x)
- Department B: h201, h202, h203, h204 (128.114.2.x)
- LLM Server: h_server (128.114.3.178)
- Trusted External Host: h_trust (192.47.38.109)
- Untrusted External Host: h_untrust (108.35.24.113)

Link Setup:
- Hosts on each floor are connected to their respective switch (s2 or s3).
- s2, s3, and s4 uplink to the core switch s1.
- Trusted and untrusted hosts directly connect to the core switch.

To Run Topology: sudo python3 final_skel.py
----------------
This starts the Mininet topology and links it to the remote POX controller.

2. Controller Logic (Defined in finalcontroller_skel.py):
----------------------------------------------------------
The custom POX controller handles routing and firewall enforcement.

Core Logic:
- ARP packets are flooded to allow address resolution.
- Non-IPv4/ARP packets are ignored.
- IPv4 packets are routed based on destination IP and switch ID.
- Flow entries are installed dynamically to minimize controller load.

Firewall Rules Enforced:
- Untrusted Host (h_untrust):
  * Block ICMP to internal hosts and server
  * Block all IP traffic to the server
- Trusted Host (h_trust):
  * Block ICMP to Department B
  * Block all IP traffic and ICMP to the server
- Department A <-> Department B:
  * Block ICMP traffic in both directions

Routing:
- Each switch uses the destination IP to determine the correct output port.
- Flow entries include timeouts to simulate dynamic routing behavior.

To Run Controller:
------------------
From the POX directory, run: python3 ./pox.py misc.controller

3. Features Implemented:
------------------------
- Complete Mininet topology matching enterprise design  
- POX controller with packet forwarding and policy enforcement  
- ARP flooding functionality verified  
- All specified security/firewall rules implemented  
- Proper routing for allowed traffic using flow mods  
- Verified connectivity (ICMP, TCP) with test results and screenshots

4. Notes:
---------
- Ignore DNS parsing warnings in POX output; they are unrelated to this controller logic.
- Test cases (e.g., ping, telnet, iperf) are included in the report with screenshots.
- Flow rules are installed correctly (no overuse of OFPP_FLOOD for IP).

5. File Summary:
----------------
- `final_skel.py`: Mininet topology definition
- `finalcontroller_skel.py`: POX controller logic
- `Lab4 Report.docx`: Documentation and test verification
- `README.txt`: This file

