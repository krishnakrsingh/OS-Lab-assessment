#!/usr/bin/env python3
import os
import time
import threading
import multiprocessing

# --- 1. Process Fork Hierarchy ---
def demo_process_hierarchy():
    print("--- 1. Process Hierarchy (fork & waitpid) ---")
    if not hasattr(os, "fork"):
        print("os.fork() requires Linux/WSL2.")
        return

    children = []
    for i in range(3):
        pid = os.fork()
        if pid == 0:
            print(f"  Child {i+1} (PID: {os.getpid()}, PPID: {os.getppid()}) working...")
            time.sleep(0.1 * (i + 1))
            os._exit(i * 10)
        else:
            children.append(pid)

    for pid in children:
        _, status = os.waitpid(pid, 0)
        print(f"Harvested child {pid}, exit code: {os.WEXITSTATUS(status)}")
    print()

# --- 2. Thread Concurrency & Locks ---
counter = 0
lock = threading.Lock()

def unsafe_worker():
    global counter
    for _ in range(500):
        val = counter
        time.sleep(0.00001)
        counter = val + 1

def safe_worker():
    global counter
    for _ in range(500):
        with lock:
            val = counter
            time.sleep(0.00001)
            counter = val + 1

def demo_threads():
    global counter
    print("--- 2. Threads: Race Condition vs Lock ---")
    
    # Without lock
    counter = 0
    threads = [threading.Thread(target=unsafe_worker) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    print(f"Without Lock -> Expected: 2500, Got: {counter} (Race condition: {counter != 2500})")

    # With lock
    counter = 0
    threads = [threading.Thread(target=safe_worker) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    print(f"With Lock    -> Expected: 2500, Got: {counter} (Protected: {counter == 2500})")
    print()

# --- 3. Process vs Thread Memory ---
shared_list = [1, 2, 3]

def proc_worker():
    global shared_list
    shared_list.append(99)
    print(f"  Inside child process: {shared_list}")

def thread_worker():
    global shared_list
    shared_list.append(99)
    print(f"  Inside worker thread: {shared_list}")

def demo_memory_isolation():
    global shared_list
    print("--- 3. Memory: Process Isolation vs Thread Sharing ---")
    
    shared_list = [1, 2, 3]
    p = multiprocessing.Process(target=proc_worker)
    p.start()
    p.join()
    print(f"Parent process after child: {shared_list} (Isolated: {shared_list == [1, 2, 3]})")

    shared_list = [1, 2, 3]
    t = threading.Thread(target=thread_worker)
    t.start()
    t.join()
    print(f"Main thread after worker  : {shared_list} (Shared: {shared_list == [1, 2, 3, 99]})")
    print()

if __name__ == "__main__":
    try:
        multiprocessing.set_start_method("fork", force=True)
    except (RuntimeError, ValueError):
        pass
    demo_process_hierarchy()
    demo_threads()
    demo_memory_isolation()

