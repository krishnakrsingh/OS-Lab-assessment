#!/usr/bin/env python3
"""
Anonymous Pipe IPC (POSIX os.pipe)
Demonstrates:
- Kernel buffer creation via os.pipe() returning (read_fd, write_fd)
- Parent-to-child unidirectional streaming
- Full duplex communication using two distinct pipes
- Proper descriptor cleanup avoiding deadlock / leak
"""

import os
import sys
import time

def demo_unidirectional_pipe():
    print("=" * 60)
    print("1. Unidirectional Anonymous Pipe (Parent -> Child)")
    print("=" * 60)
    
    if not hasattr(os, "pipe") or not hasattr(os, "fork"):
        print("[!] os.pipe() and os.fork() require a POSIX environment.")
        return

    # Create pipe: r_fd for reading, w_fd for writing
    r_fd, w_fd = os.pipe()
    
    pid = os.fork()
    if pid == 0:
        # Child process: Reader
        # Must close unused write end
        os.close(w_fd)
        print(f"  [Child PID {os.getpid()}] Closed write fd {w_fd}, listening on read fd {r_fd}...")
        
        # Read from pipe until EOF (when parent closes write end)
        chunks = []
        while True:
            data = os.read(r_fd, 64)
            if not data:
                break  # EOF reached
            chunks.append(data)
            
        os.close(r_fd)
        received_msg = b"".join(chunks).decode("utf-8")
        print(f"  [Child PID {os.getpid()}] Received stream message: '{received_msg.strip()}'")
        os._exit(0)
    else:
        # Parent process: Writer
        # Must close unused read end
        os.close(r_fd)
        print(f"[*] Parent PID {os.getpid()}: Closed read fd {r_fd}, writing message...")
        
        messages = [
            b"Message Chunk 1: Initializing IPC channel\n",
            b"Message Chunk 2: Streaming computational payload\n",
            b"Message Chunk 3: IPC transmission complete\n"
        ]
        
        for msg in messages:
            os.write(w_fd, msg)
            time.sleep(0.05)
            
        # Close write end to signal EOF to reader
        os.close(w_fd)
        print("[*] Parent closed write end. Awaiting child exit status...")
        os.waitpid(pid, 0)
        print("[+] Unidirectional pipe demo concluded successfully.\n")

def demo_bidirectional_pipes():
    print("=" * 60)
    print("2. Bidirectional Anonymous Pipe Pair (Request-Response)")
    print("=" * 60)
    
    # Pipe 1: Parent -> Child (Request)
    p2c_r, p2c_w = os.pipe()
    # Pipe 2: Child -> Parent (Response)
    c2p_r, c2p_w = os.pipe()
    
    pid = os.fork()
    if pid == 0:
        # Child side
        os.close(p2c_w)
        os.close(c2p_r)
        
        req = os.read(p2c_r, 128).decode("utf-8")
        print(f"  [Child PID {os.getpid()}] Received request: '{req.strip()}'")
        
        # Process request (e.g. compute square)
        number = int(req.split(":")[-1].strip())
        result = number ** 2
        response_msg = f"RESULT: {result}".encode("utf-8")
        
        os.write(c2p_w, response_msg)
        os.close(p2c_r)
        os.close(c2p_w)
        os._exit(0)
    else:
        # Parent side
        os.close(p2c_r)
        os.close(c2p_w)
        
        query_val = 16
        print(f"[*] Parent sending computation query for: {query_val}")
        os.write(p2c_w, f"SQUARE_REQUEST:{query_val}".encode("utf-8"))
        os.close(p2c_w)  # Sent query
        
        resp = os.read(c2p_r, 128).decode("utf-8")
        print(f"[*] Parent received response from child: '{resp.strip()}'")
        os.close(c2p_r)
        os.waitpid(pid, 0)
        print("[+] Bidirectional pipe RPC cycle complete.\n")

def main():
    print("############################################################")
    print("  ANONYMOUS PIPE INTER-PROCESS COMMUNICATION")
    print("############################################################\n")
    demo_unidirectional_pipe()
    demo_bidirectional_pipes()

if __name__ == "__main__":
    main()
