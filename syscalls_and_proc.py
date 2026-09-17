#!/usr/bin/env python3
import os
import sys
import time

def demo_syscalls():
    print("--- 1. System Calls Demo ---")
    print(f"Current PID : {os.getpid()}")
    print(f"Parent PID  : {os.getppid()}")
    if hasattr(os, "uname"):
        u = os.uname()
        print(f"OS/Kernel   : {u.sysname} {u.release} ({u.machine})")

    # File descriptor I/O system calls
    fd = os.open("temp_test.txt", os.O_CREAT | os.O_RDWR | os.O_TRUNC, 0o644)
    os.write(fd, b"Testing low-level POSIX write syscall.\n")
    os.lseek(fd, 0, os.SEEK_SET)
    content = os.read(fd, 100)
    print("Read from fd:", content.decode().strip())
    
    st = os.fstat(fd)
    print(f"File size from fstat: {st.st_size} bytes")
    os.close(fd)
    os.unlink("temp_test.txt")
    print()

def demo_proc_filesystem():
    print("--- 2. Linux /proc Filesystem Observation ---")
    pid = os.getpid()
    status_file = f"/proc/{pid}/status"
    
    if not os.path.exists(status_file):
        print("Not running on Linux, skipping /proc inspection.")
        return

    with open(status_file) as f:
        lines = f.readlines()
        
    interesting_keys = ["Name", "State", "PPid", "Threads", "VmRSS", "voluntary_ctxt_switches", "nonvoluntary_ctxt_switches"]
    for line in lines:
        for key in interesting_keys:
            if line.startswith(f"{key}:"):
                print(f"  {line.strip()}")

    if os.path.exists("/proc/loadavg"):
        with open("/proc/loadavg") as f:
            print(f"  Load average: {f.read().strip()}")
    print()

def demo_zombie_and_orphan():
    print("--- 3. Zombie and Orphan Processes Demo ---")
    if not hasattr(os, "fork"):
        print("os.fork() not available on Windows, run under WSL2/Linux.")
        return

    # Zombie demo
    child_pid = os.fork()
    if child_pid == 0:
        # Child exits right away
        os._exit(42)
    else:
        time.sleep(0.3)
        # Read child's state from /proc
        try:
            with open(f"/proc/{child_pid}/status") as f:
                for line in f:
                    if line.startswith("State:"):
                        print(f"Child {child_pid} state before wait(): {line.strip()}")
        except FileNotFoundError:
            pass

        reaped_pid, status = os.waitpid(child_pid, 0)
        exit_code = os.WEXITSTATUS(status)
        print(f"Reaped child {reaped_pid} with exit code: {exit_code}")

    # Orphan demo
    p = os.fork()
    if p == 0:
        # Intermediate process
        grandchild = os.fork()
        if grandchild == 0:
            time.sleep(0.4)
            print(f"Grandchild {os.getpid()} adopted by parent PID: {os.getppid()}")
            os._exit(0)
        else:
            os._exit(0)
    else:
        os.waitpid(p, 0)
        time.sleep(0.6)
    print()

if __name__ == "__main__":
    demo_syscalls()
    demo_proc_filesystem()
    demo_zombie_and_orphan()
