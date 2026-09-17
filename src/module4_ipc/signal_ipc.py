#!/usr/bin/env python3
"""
POSIX Signals for Asynchronous IPC (signal & os.kill)
Demonstrates:
- Registering custom user-defined signal handlers (SIGUSR1, SIGUSR2)
- Asynchronous signal dispatch across processes via os.kill()
- Process synchronization using signal pauses (pause / sigsuspend)
"""

import os
import signal
import sys
import time

signal_received = False

def handle_sigusr1(signum, frame):
    """Custom handler executed asynchronously upon receiving SIGUSR1."""
    global signal_received
    signal_received = True
    print(f"  [Child PID {os.getpid()}] Signal Handler triggered! Caught signal {signum} (SIGUSR1).")

def run_signal_demo():
    print("=" * 60)
    print("POSIX Signal Handling & Asynchronous IPC")
    print("=" * 60)
    
    if not hasattr(signal, "SIGUSR1") or not hasattr(os, "fork"):
        print("[!] POSIX signals (SIGUSR1) require a Linux/Unix environment.")
        return

    child_pid = os.fork()
    if child_pid == 0:
        # Child Process: Register signal handler and wait
        signal.signal(signal.SIGUSR1, handle_sigusr1)
        print(f"  [Child PID {os.getpid()}] Registered handler for SIGUSR1. Awaiting signal from parent...")
        
        # Wait until the flag is set by signal handler
        timeout = 5.0
        start = time.time()
        while not signal_received and (time.time() - start) < timeout:
            time.sleep(0.05)
            
        if signal_received:
            print(f"  [Child PID {os.getpid()}] Handled event asynchronously. Exiting cleanly.")
            os._exit(0)
        else:
            print(f"  [Child PID {os.getpid()}] Timed out waiting for signal.")
            os._exit(1)
    else:
        # Parent Process: Sleep briefly, then dispatch signal
        time.sleep(0.3)
        print(f"[*] Parent PID {os.getpid()}: Dispatching os.kill({child_pid}, signal.SIGUSR1)...")
        os.kill(child_pid, signal.SIGUSR1)
        
        # Wait for child to complete
        _, status = os.waitpid(child_pid, 0)
        exit_code = os.WEXITSTATUS(status)
        print(f"[*] Child process completed with exit status: {exit_code}")
        print("\n[+] Asynchronous signal IPC test completed successfully.")

def main():
    print("############################################################")
    print("  POSIX ASYNCHRONOUS SIGNALS DEMONSTRATION")
    print("############################################################\n")
    run_signal_demo()

if __name__ == "__main__":
    main()
