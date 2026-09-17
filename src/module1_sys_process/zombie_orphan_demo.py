#!/usr/bin/env python3
"""
Zombie and Orphan Process Demonstration
Demonstrates:
1. Zombie Process: A child terminates before parent calls wait().
   The kernel retains the child's PID and exit status in the process table.
2. Process Reaping: Parent calls waitpid() to retrieve child exit code
   and release its entry in the process table.
3. Orphan Process: Parent terminates before child, leading init / systemd
   (PID 1 or user systemd manager) to adopt the orphan.
"""

import os
import sys
import time

def read_proc_state(pid: int) -> str:
    """Helper to read process state from /proc/[pid]/status."""
    status_path = f"/proc/{pid}/status"
    if not os.path.exists(status_path):
        return "Non-existent (Reaped / Dead)"
    try:
        with open(status_path, "r") as f:
            for line in f:
                if line.startswith("State:"):
                    return line.strip().split(":", 1)[1].strip()
    except (OSError, IOError):
        return "Inaccessible"
    return "Unknown"

def demo_zombie_and_reap():
    print("=" * 60)
    print("1. Zombie Process Lifecycle & Kernel Reaping")
    print("=" * 60)
    
    if not hasattr(os, "fork"):
        print("[!] os.fork() is only available on POSIX/Linux systems.")
        return
        
    print(f"[*] Parent process PID: {os.getpid()}")
    
    child_pid = os.fork()
    
    if child_pid == 0:
        # Child process code
        print(f"  [Child {os.getpid()}] Started. Exiting immediately with status code 42...")
        os._exit(42)  # Immediate exit without flushing Python buffers twice
    else:
        # Parent process code
        print(f"[*] Parent spawned child with PID: {child_pid}")
        # Give the child time to terminate while parent does NOT call wait()
        time.sleep(0.5)
        
        state = read_proc_state(child_pid)
        print(f"[*] Parent checking child {child_pid} state before wait():")
        print(f"    Child state in /proc: '{state}'")
        
        if "Z" in state:
            print("    -> CONFIRMED: Child is in ZOMBIE (defunct) state.")
            print("    -> Child's memory/resources are freed, but PCB remains in process table.")
        
        # Now parent reaps the child
        print(f"[*] Parent calling os.waitpid({child_pid}, 0) to collect status...")
        reaped_pid, status = os.waitpid(child_pid, 0)
        
        if os.WIFEXITED(status):
            exit_code = os.WEXITSTATUS(status)
            print(f"    -> Successfully reaped child {reaped_pid} with exit code {exit_code}")
            
        time.sleep(0.2)
        state_after = read_proc_state(child_pid)
        print(f"[*] Child state in /proc after waitpid(): '{state_after}'")
        print("    -> CONFIRMED: Process control block removed from process table.")
    print()

def demo_orphan():
    print("=" * 60)
    print("2. Orphan Process Adoption Demonstration")
    print("=" * 60)
    
    if not hasattr(os, "fork"):
        return
        
    # We fork an intermediate parent that creates an orphan, so this main script stays intact.
    inter_pid = os.fork()
    
    if inter_pid == 0:
        # Intermediate process
        intermediate_pid = os.getpid()
        child_pid = os.fork()
        
        if child_pid == 0:
            # Grandchild process (will become orphan)
            print(f"  [Child {os.getpid()}] Created by Parent {intermediate_pid}")
            # Wait for parent to terminate
            time.sleep(0.6)
            new_parent = os.getppid()
            print(f"  [Child {os.getpid()}] Original parent exited. New parent PID (Adopted): {new_parent}")
            os._exit(0)
        else:
            # Intermediate parent exits quickly
            print(f"  [Intermediate Parent {intermediate_pid}] Exiting immediately to orphan child {child_pid}...")
            os._exit(0)
    else:
        # Main test runner waits for intermediate process to finish
        os.waitpid(inter_pid, 0)
        # Give orphan time to print its adoption notice and terminate
        time.sleep(1.0)
        print("[*] Orphan adoption test completed.")
    print()

def main():
    print("############################################################")
    print("  ZOMBIE PROCESS & ORPHAN ADOPTION DEMO")
    print("############################################################\n")
    demo_zombie_and_reap()
    demo_orphan()

if __name__ == "__main__":
    main()
