#!/usr/bin/env python3
"""
Named Pipe (FIFO) IPC (POSIX os.mkfifo)
Demonstrates:
- Filesystem-backed FIFO special device node creation
- Producer writing to FIFO and Consumer reading from FIFO
- Blocking semantics during open() until both ends are attached
- Clean resource removal via os.unlink()
"""

import os
import sys
import time
import stat

FIFO_PATH = "/tmp/os_assessment_fifo.pipe"

def run_fifo_demo():
    print("=" * 60)
    print("Linux Named Pipe (FIFO) Demonstration")
    print("=" * 60)
    
    if not hasattr(os, "mkfifo") or not hasattr(os, "fork"):
        print("[!] os.mkfifo() is not supported on this platform.")
        return

    # Clean up stale FIFO if one was left behind
    if os.path.exists(FIFO_PATH):
        try:
            os.unlink(FIFO_PATH)
        except OSError:
            pass

    # Create the named pipe filesystem node
    try:
        os.mkfifo(FIFO_PATH, 0o666)
        print(f"[*] Created FIFO special node at: {FIFO_PATH}")
        st = os.stat(FIFO_PATH)
        is_fifo = stat.S_ISFIFO(st.st_mode)
        print(f"[*] Verified node inode={st.st_ino}, is_fifo={is_fifo}")
    except OSError as e:
        print(f"[!] Failed to create FIFO: {e}", file=sys.stderr)
        return

    pid = os.fork()
    if pid == 0:
        # Child Process: Consumer / Reader
        print(f"  [Consumer Child PID {os.getpid()}] Opening FIFO for reading (blocks until producer opens)...")
        # Opening O_RDONLY blocks until writer opens O_WRONLY
        fifo_read = os.open(FIFO_PATH, os.O_RDONLY)
        print(f"  [Consumer Child PID {os.getpid()}] FIFO connected. Reading incoming items:")
        
        buffer = b""
        while True:
            chunk = os.read(fifo_read, 128)
            if not chunk:
                break
            buffer += chunk
            
        os.close(fifo_read)
        print(f"  [Consumer Child PID {os.getpid()}] Read complete:\n  >>> {buffer.decode('utf-8').strip()}")
        os._exit(0)
    else:
        # Parent Process: Producer / Writer
        time.sleep(0.1)  # Allow child to start opening
        print(f"[*] Parent Producer PID {os.getpid()}: Opening FIFO for writing...")
        fifo_write = os.open(FIFO_PATH, os.O_WRONLY)
        print(f"[*] Parent Producer connected. Writing payload batch...")
        
        payload = (
            "FIFO_ITEM_1: Sensor telemetry packet\n"
            "FIFO_ITEM_2: Memory allocation request\n"
            "FIFO_ITEM_3: Process scheduling checkpoint\n"
        )
        os.write(fifo_write, payload.encode("utf-8"))
        os.close(fifo_write)
        print("[*] Parent Producer closed write descriptor.")
        
        # Wait for consumer child to terminate
        os.waitpid(pid, 0)
        
        # Unlink the FIFO node
        if os.path.exists(FIFO_PATH):
            os.unlink(FIFO_PATH)
            print(f"[*] Unlinked FIFO file node {FIFO_PATH}")
            
    print("\n[+] FIFO Inter-process communication successfully executed.")

def main():
    print("############################################################")
    print("  NAMED PIPE (FIFO) PRODUCER-CONSUMER IPC")
    print("############################################################\n")
    run_fifo_demo()

if __name__ == "__main__":
    main()
