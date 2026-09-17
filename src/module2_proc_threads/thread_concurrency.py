#!/usr/bin/env python3
"""
Thread Concurrency, Race Conditions, and Synchronization
Demonstrates:
- Multiple concurrent worker threads
- Critical section race conditions with shared memory
- Mutual Exclusion using threading.Lock
- Controlled concurrency using threading.Semaphore
"""

import threading
import time

# Shared state variables
unprotected_counter = 0
protected_counter = 0
counter_lock = threading.Lock()

NUM_THREADS = 10
INCREMENTS_PER_THREAD = 10000

def unsafe_worker():
    """Worker function that updates shared state without synchronization."""
    global unprotected_counter
    for _ in range(INCREMENTS_PER_THREAD):
        # Read-Modify-Write cycle exposed to race condition
        current = unprotected_counter
        # Introduce a microscopic pause or context switch point
        time.sleep(0.000001)
        unprotected_counter = current + 1

def safe_worker():
    """Worker function using Lock (Mutex) for mutual exclusion."""
    global protected_counter
    for _ in range(INCREMENTS_PER_THREAD):
        with counter_lock:
            # Critical Section is atomic with respect to other threads
            current = protected_counter
            time.sleep(0.000001)
            protected_counter = current + 1

def demo_race_condition():
    print("=" * 60)
    print("1. Critical Section Race Condition Demonstration")
    print("=" * 60)
    global unprotected_counter
    unprotected_counter = 0
    threads = []
    
    expected = 5 * 200  # Smaller iteration for quick demonstration
    
    print(f"[*] Spawning 5 threads to perform 200 increments each without lock...")
    
    def fast_unsafe():
        global unprotected_counter
        for _ in range(200):
            val = unprotected_counter
            time.sleep(0.00001)
            unprotected_counter = val + 1

    for _ in range(5):
        t = threading.Thread(target=fast_unsafe)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    print(f"[*] Expected Counter Value: {expected}")
    print(f"[*] Actual Counter Value  : {unprotected_counter}")
    if unprotected_counter < expected:
        lost = expected - unprotected_counter
        print(f"[!] RACE CONDITION OCCURRED! Lost {lost} updates due to unsynchronized interleaving.")
    else:
        print("[*] (Interleaving did not collide on this run, re-run with higher contention.)")
    print()

def demo_mutex_synchronization():
    print("=" * 60)
    print("2. Mutual Exclusion Synchronization (threading.Lock)")
    print("=" * 60)
    global protected_counter
    protected_counter = 0
    threads = []
    expected = 5 * 200
    
    print(f"[*] Spawning 5 threads to perform 200 increments each with Lock...")
    
    def fast_safe():
        global protected_counter
        for _ in range(200):
            with counter_lock:
                val = protected_counter
                time.sleep(0.00001)
                protected_counter = val + 1

    for _ in range(5):
        t = threading.Thread(target=fast_safe)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    print(f"[*] Expected Counter Value: {expected}")
    print(f"[*] Actual Counter Value  : {protected_counter}")
    assert protected_counter == expected, "Lock failed to protect critical section!"
    print("[+] MUTEX SUCCESS: Lock guaranteed atomicity. Zero lost updates.")
    print()

def demo_semaphore():
    print("=" * 60)
    print("3. Bounded Concurrency using threading.Semaphore")
    print("=" * 60)
    
    # Semaphore allowing at most 2 threads at any given time
    MAX_CONCURRENT_SLOTS = 2
    pool_semaphore = threading.Semaphore(MAX_CONCURRENT_SLOTS)
    active_in_pool = 0
    pool_lock = threading.Lock()
    
    def resource_user(thread_id: int):
        nonlocal active_in_pool
        print(f"  [Thread {thread_id}] Requesting access to shared resource pool...")
        with pool_semaphore:
            with pool_lock:
                active_in_pool += 1
                current_active = active_in_pool
            print(f"  --> [Thread {thread_id}] Entered pool (Active users: {current_active}/{MAX_CONCURRENT_SLOTS})")
            time.sleep(0.15)
            with pool_lock:
                active_in_pool -= 1
            print(f"  <-- [Thread {thread_id}] Leaving pool.")

    threads = [threading.Thread(target=resource_user, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("\n[+] Semaphore properly restricted concurrent entries.")

def main():
    print("############################################################")
    print("  THREAD CONCURRENCY, RACE CONDITIONS & SYNCHRONIZATION")
    print("############################################################\n")
    demo_race_condition()
    demo_mutex_synchronization()
    demo_semaphore()

if __name__ == "__main__":
    main()
