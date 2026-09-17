#!/usr/bin/env python3
"""
Process vs Thread Architectural Comparison
Demonstrates:
1. Memory Isolation: Separate virtual address space (processes) vs shared memory (threads).
2. Creation Overhead Benchmark: Measures creation and join latency between processes and threads.
"""

import os
import time
import multiprocessing
import threading

# Shared mutable object for memory test
sample_data = [1, 2, 3]

def process_memory_worker():
    global sample_data
    # Modify data inside process
    sample_data.append(999)
    print(f"  [Child Process PID {os.getpid()}] Modified sample_data: {sample_data}")

def thread_memory_worker():
    global sample_data
    # Modify data inside thread
    sample_data.append(888)
    print(f"  [Worker Thread] Modified sample_data: {sample_data}")

def demo_memory_isolation():
    print("=" * 60)
    print("1. Memory Isolation Comparison (Address Space)")
    print("=" * 60)
    global sample_data
    
    # Process test
    sample_data = [1, 2, 3]
    print(f"[*] Parent Process before child: sample_data = {sample_data}")
    p = multiprocessing.Process(target=process_memory_worker)
    p.start()
    p.join()
    print(f"[*] Parent Process after child : sample_data = {sample_data}")
    if sample_data == [1, 2, 3]:
        print("  -> CONFIRMED: Process memory is isolated (Copy-on-Write). Child mutation was local.\n")
        
    # Thread test
    sample_data = [1, 2, 3]
    print(f"[*] Main Thread before worker : sample_data = {sample_data}")
    t = threading.Thread(target=thread_memory_worker)
    t.start()
    t.join()
    print(f"[*] Main Thread after worker  : sample_data = {sample_data}")
    if 888 in sample_data:
        print("  -> CONFIRMED: Thread memory is shared across the entire process space.\n")

def dummy_task():
    pass

def benchmark_creation_latency(n_units=20):
    print("=" * 60)
    print(f"2. Creation & Join Overhead Benchmark ({n_units} units)")
    print("=" * 60)
    
    # Benchmark Thread Creation
    t0 = time.perf_counter()
    threads = [threading.Thread(target=dummy_task) for _ in range(n_units)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    thread_time = time.perf_counter() - t0
    
    # Benchmark Process Creation
    t0 = time.perf_counter()
    processes = [multiprocessing.Process(target=dummy_task) for _ in range(n_units)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    proc_time = time.perf_counter() - t0
    
    print(f"[*] {n_units} Threads creation + join time  : {thread_time * 1000:.2f} ms ({thread_time / n_units * 1000:.3f} ms/thread)")
    print(f"[*] {n_units} Processes creation + join time: {proc_time * 1000:.2f} ms ({proc_time / n_units * 1000:.3f} ms/process)")
    
    if proc_time > thread_time:
        ratio = proc_time / thread_time
        print(f"[+] Threads were ~{ratio:.1f}x faster to spawn due to avoiding full address-space duplication.")
    print()

def main():
    print("############################################################")
    print("  PROCESS VS THREAD ARCHITECTURAL BENCHMARK")
    print("############################################################\n")
    demo_memory_isolation()
    benchmark_creation_latency(25)

if __name__ == "__main__":
    main()
