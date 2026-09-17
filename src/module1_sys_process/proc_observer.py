#!/usr/bin/env python3
"""
Linux /proc Filesystem Observer
Reads Linux virtual filesystem (/proc) to inspect:
- Process states (R: Running, S: Sleeping, D: Disk sleep, Z: Zombie, T: Stopped)
- Memory usage (VmSize, VmRSS, VmData, VmStk)
- Context switches (Voluntary vs Non-voluntary)
- CPU tick counters and priorities
- System-wide load averages and memory limits
"""

import os
import sys

def parse_proc_status(pid: int) -> dict:
    """Reads /proc/[pid]/status into a dictionary."""
    status_path = f"/proc/{pid}/status"
    if not os.path.exists(status_path):
        raise FileNotFoundError(f"Process {pid} does not exist in /proc.")
    
    data = {}
    with open(status_path, "r") as f:
        for line in f:
            parts = line.strip().split(":", 1)
            if len(parts) == 2:
                data[parts[0].strip()] = parts[1].strip()
    return data

def parse_proc_stat(pid: int) -> dict:
    """
    Reads /proc/[pid]/stat fields according to proc(5) man page:
    pid, comm, state, ppid, pgrp, session, tty_nr, tpgid, flags,
    minflt, cminflt, majflt, cmajflt, utime, stime, cutime, cstime,
    priority, nice, num_threads, itrealvalue, starttime, vsize, rss...
    """
    stat_path = f"/proc/{pid}/stat"
    if not os.path.exists(stat_path):
        raise FileNotFoundError(f"Process {pid} stat file missing.")
    
    with open(stat_path, "r") as f:
        content = f.read().strip()
    
    # Handle comm enclosed in parentheses (which might contain spaces)
    left_paren = content.find("(")
    right_paren = content.rfind(")")
    comm = content[left_paren + 1:right_paren]
    rest = content[right_paren + 2:].split()
    
    return {
        "pid": int(content[:left_paren].strip()),
        "comm": comm,
        "state": rest[0],
        "ppid": int(rest[1]),
        "pgrp": int(rest[2]),
        "session": int(rest[3]),
        "utime_ticks": int(rest[11]),
        "stime_ticks": int(rest[12]),
        "priority": int(rest[15]),
        "nice": int(rest[16]),
        "num_threads": int(rest[17]),
        "vsize_bytes": int(rest[20]),
        "rss_pages": int(rest[21])
    }

def print_process_details(pid: int):
    """Formats and prints detailed process metrics from /proc."""
    try:
        status = parse_proc_status(pid)
        stat = parse_proc_stat(pid)
        
        state_map = {
            "R": "Running / Runnable",
            "S": "Interruptible Sleep (Waiting for event/signal)",
            "D": "Uninterruptible Sleep (Usually disk/IO wait)",
            "Z": "Zombie / Defunct (Terminated, waiting for parent wait())",
            "T": "Stopped (by job control signal or tracer)",
            "I": "Idle kernel thread"
        }
        raw_state = status.get("State", "Unknown").split()[0]
        state_desc = state_map.get(raw_state, "Unknown state")
        
        print(f"\n--- Observation for PID {pid} [{status.get('Name', 'unknown')}] ---")
        print(f"  PID / PPID          : {pid} / {status.get('PPid', 'N/A')}")
        print(f"  Process State       : {raw_state} ({state_desc})")
        print(f"  Threads count       : {status.get('Threads', '1')}")
        print(f"  Priority / Nice     : {stat['priority']} / {stat['nice']}")
        print(f"  CPU Ticks (user/sys): {stat['utime_ticks']} ticks / {stat['stime_ticks']} ticks")
        print(f"  Virtual Memory (Vm) : {status.get('VmSize', 'N/A')}")
        print(f"  Resident Memory(RSS): {status.get('VmRSS', 'N/A')}")
        print(f"  Voluntary Switches  : {status.get('voluntary_ctxt_switches', 'N/A')}")
        print(f"  Involuntary Switches: {status.get('nonvoluntary_ctxt_switches', 'N/A')}")
    except FileNotFoundError as e:
        print(f"[!] Error inspecting PID {pid}: {e}")
    except PermissionError:
        print(f"[!] Permission denied accessing /proc/{pid}/status")

def display_system_proc_info():
    """Displays system-wide metrics from /proc/loadavg and /proc/meminfo."""
    print("=" * 60)
    print("System-Wide /proc Health & Metrics")
    print("=" * 60)
    
    # Load averages (1 min, 5 min, 15 min)
    if os.path.exists("/proc/loadavg"):
        with open("/proc/loadavg", "r") as f:
            parts = f.read().strip().split()
            print(f"[*] Load Averages (1m, 5m, 15m)  : {parts[0]}, {parts[1]}, {parts[2]}")
            print(f"[*] Running / Total Entities    : {parts[3]}")
            print(f"[*] Last Created PID            : {parts[4]}")
    
    # Memory metrics
    if os.path.exists("/proc/meminfo"):
        mem = {}
        with open("/proc/meminfo", "r") as f:
            for line in f:
                p = line.strip().split(":", 1)
                if len(p) == 2:
                    mem[p[0].strip()] = p[1].strip()
        print(f"[*] Total Physical Memory (MemTotal): {mem.get('MemTotal', 'N/A')}")
        print(f"[*] Available Memory (MemAvailable) : {mem.get('MemAvailable', 'N/A')}")
        print(f"[*] Total Swap (SwapTotal)          : {mem.get('SwapTotal', 'N/A')}")
    print()

def main():
    print("############################################################")
    print("  LINUX /proc VIRTUAL FILESYSTEM OBSERVER")
    print("############################################################")
    
    if not os.path.exists("/proc"):
        print("[!] Note: /proc is specific to Linux systems. Run this inside WSL2/Ubuntu.")
        sys.exit(0)
        
    display_system_proc_info()
    
    current_pid = os.getpid()
    parent_pid = os.getppid()
    
    print_process_details(current_pid)
    print_process_details(parent_pid)

if __name__ == "__main__":
    main()
