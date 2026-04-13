# Task 2 & 3 Testing Guide

## Quick Summary

- **Task 2**: TCP RST Attack - Terminates telnet sessions
- **Task 3**: TCP Session Hijacking - Injects commands into telnet sessions

Both have **manual** and **automatic** versions. The automatic versions use packet sniffing to automate the process.

---

## Prerequisites

✅ Docker containers running
✅ Scapy installed
✅ Python 3 available
✅ sudo/root access for packet operations

**Verify containers:**
```bash
dockps  # (or: docker ps --format "{{.ID}} {{.Names}}")
```

Should see:
- `seed-attacker` (10.9.0.1)
- `victim-10.9.0.5` (10.9.0.5)
- `user1-10.9.0.6` (10.9.0.6)
- `user2-10.9.0.7` (10.9.0.7)

---

## Network Setup

All scripts use the bridge interface: **`br-983f4e838608`**

Verify it exists:
```bash
ip link show | grep br-
```

---

## Task 2: TCP RST Attack

### What It Does
Sends a spoofed TCP RST (reset) packet to abruptly terminate an active telnet connection.

### Method 1: Manual (Recommended for beginners)

1. **Shell into attacker container:**
   ```bash
   docksh <attacker_id>  # e.g., docksh b0730
   ```

2. **Shell into victim container (terminal 2):**
   ```bash
   docksh <victim_id>  # e.g., docksh f5b4
   ```

3. **Start Wireshark on the VM to capture packets:**
   ```bash
   wireshark &
   # Select interface: br-983f4e838608
   # Start capturing
   ```

4. **From attacker container, initiate telnet to victim:**
   ```bash
   telnet 10.9.0.5
   # Login: seed / password: dees
   # Type something to generate traffic
   ```

5. **In Wireshark, examine a packet from client→server (10.9.0.6→10.9.0.5)**
   - Note the **Sequence Number**
   - Note the **Source Port**

6. **Edit `/volumes/rst_attack.py` on the VM:**
   ```python
   SRC_IP   = "10.9.0.6"   # from Wireshark
   DST_IP   = "10.9.0.5"   # server IP
   SPORT    = <port>       # from Wireshark
   DPORT    = 23
   SEQ      = <sequence>   # from Wireshark
   ```

7. **From attacker container, run:**
   ```bash
   cd /volumes
   sudo python3 rst_attack.py
   ```

8. **Expected result:** The telnet session terminates immediately

---

### Method 2: Automatic (Advanced)

The automatic script sniffs packets and automatically sends RST packets when it detects telnet traffic.

1. **From attacker container:**
   ```bash
   cd /volumes
   sudo python3 rst_attack_auto.py &
   ```

2. **From another terminal, establish telnet:**
   ```bash
   docksh <user1_id>
   telnet 10.9.0.5
   seed / dees
   ```

3. **Expected result:** As soon as you type anything, the connection terminates automatically

---

## Task 3: TCP Session Hijacking

### What It Does
Injects a malicious command into an active telnet connection by spoofing a TCP packet.

The default command is: `touch /tmp/hijacked`

### Method 1: Manual (Recommended for beginners)

1. **Shell into attacker container:**
   ```bash
   docksh <attacker_id>
   ```

2. **Start Wireshark (on VM) capturing on `br-983f4e838608`**

3. **From attacker, start telnet to victim:**
   ```bash
   telnet 10.9.0.5
   seed / dees
   ```

4. **Type something** (generates traffic for Wireshark to capture)

5. **In Wireshark, examine client→server packet and note:**
   - **Sequence Number**
   - **Acknowledgement Number**
   - **Source Port**

6. **Edit `session_hijack.py` on the VM:**
   ```python
   SRC_IP  = "10.9.0.6"   # client IP
   DST_IP  = "10.9.0.5"   # server IP
   SPORT   = <port>       # from Wireshark
   DPORT   = 23
   SEQ     = <sequence>   # from Wireshark
   ACK     = <ack>        # from Wireshark
   DATA    = "\r touch /tmp/hijacked \r"
   ```

7. **From attacker container, run:**
   ```bash
   cd /volumes
   sudo python3 session_hijack.py
   ```

8. **Verify on victim (shell into victim container):**
   ```bash
   ls -la /tmp/hijacked
   # File should exist!
   ```

---

### Method 2: Automatic (Advanced)

1. **Start sniffing from attacker:**
   ```bash
   cd /volumes
   sudo python3 session_hijack_auto.py &
   ```

2. **From user1 terminal, start telnet:**
   ```bash
   docksh <user1_id>
   telnet 10.9.0.5
   seed / dees
   ```

3. **Type any command** (this generates the packet to be hijacked)

4. **Expected result:** The hijacking script automatically injects the malicious command

5. **Verify on victim:**
   ```bash
   ls /tmp/hijacked
   ```

---

## Troubleshooting

### "Operation not permitted" / "Permission denied"
**Solution:** Use `sudo` when running Python scripts
```bash
sudo python3 rst_attack.py
sudo python3 session_hijack.py
```

### "No address associated with hostname"
**Solution:** Make sure you're using IP addresses, not hostnames:
- ✅ `telnet 10.9.0.5`
- ❌ `telnet victim`

### Automatic scripts not detecting packets
**Solution:** Make sure telnet session is active and generating traffic while the sniffer runs

### Interface not found error
**Solution:** Verify bridge interface exists:
```bash
ip link show | grep br-
# Should show: br-983f4e838608
```

If different, update the `IFACE` variable in the scripts.

---

## Key TCPs Parameters to Extract from Wireshark

| Parameter | What it is | Where from |
|-----------|-----------|-----------|
| SEQ | Next expected sequence # | Wireshark: "Seq" field |
| ACK | Acknowledgement number | Wireshark: "Ack" field |
| SPORT | Source port (client side) | Wireshark: TCP source port |
| DPORT | Destination port | Always 23 for telnet |
| SRC_IP | Client IP | Usually 10.9.0.6 |
| DST_IP | Server IP | Usually 10.9.0.5 |

---

## Files Modified

✅ `/workspaces/NetSec/task2/rst_attack.py` - Enhanced with instructions
✅ `/workspaces/NetSec/task2/rst_attack_auto.py` - Updated with correct bridge interface
✅ `/workspaces/NetSec/task3/session_hijack.py` - Enhanced with instructions
✅ `/workspaces/NetSec/task3/session_hijack_auto.py` - Updated with correct bridge interface

---

## Next Steps

1. Test Task 2 manually first (easier to debug)
2. Verify Task 2 works, then try automatic version
3. Move to Task 3 manual, then automatic
4. Once both work, move to Task 4 (Reverse Shell)

Good luck! 🎯
