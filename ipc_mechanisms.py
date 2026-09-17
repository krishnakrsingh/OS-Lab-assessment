#!/usr/bin/env python3
import os
import sys
import time
import signal
import multiprocessing
from multiprocessing import Process, Queue, Lock, shared_memory


# --- 1. Anonymous Pipe ---
def demo_pipe():
    print("--- 1. Anonymous Pipe IPC ---")
    if not hasattr(os, "pipe") or not hasattr(os, "fork"):
        print("Pipes require Linux/WSL2.")
        return

    r_fd, w_fd = os.pipe()
    sys.stdout.flush()
    pid = os.fork()
    if pid == 0:
        os.close(w_fd)
        msg = os.read(r_fd, 100).decode()
        print(f"  Child received via pipe: '{msg.strip()}'", flush=True)
        os.close(r_fd)
        os._exit(0)
    else:
        os.close(r_fd)
        os.write(w_fd, b"Data sent from parent process.\n")
        os.close(w_fd)
        os.waitpid(pid, 0)
    print()

# --- 2. Named Pipe (FIFO) ---
FIFO_FILE = "/tmp/demo_ipc_fifo"

def demo_fifo():
    print("--- 2. Named Pipe (FIFO) IPC ---")
    if not hasattr(os, "mkfifo") or not hasattr(os, "fork"):
        print("FIFOs require Linux/WSL2.")
        return

    if os.path.exists(FIFO_FILE):
        try:
            os.unlink(FIFO_FILE)
        except OSError:
            pass
    os.mkfifo(FIFO_FILE)

    sys.stdout.flush()
    pid = os.fork()
    if pid == 0:
        fifo_in = os.open(FIFO_FILE, os.O_RDONLY)
        data = os.read(fifo_in, 100).decode()
        print(f"  Child read from FIFO: '{data.strip()}'", flush=True)
        os.close(fifo_in)
        os._exit(0)
    else:
        fifo_out = os.open(FIFO_FILE, os.O_WRONLY)
        os.write(fifo_out, b"Message piped through /tmp/demo_ipc_fifo\n")
        os.close(fifo_out)
        os.waitpid(pid, 0)
        try:
            os.unlink(FIFO_FILE)
        except OSError:
            pass
    print()

# --- 3. Shared Memory ---
def shm_writer(shm_name, lock):
    shm = shared_memory.SharedMemory(name=shm_name)
    with lock:
        msg = b"Shared Memory Packet"
        shm.buf[:len(msg)] = msg
    shm.close()

def demo_shared_memory():
    print("--- 3. Shared Memory IPC with Lock ---")
    shm_name = "test_shm_buffer"
    try:
        shm = shared_memory.SharedMemory(name=shm_name, create=True, size=64)
    except FileExistsError:
        shm = shared_memory.SharedMemory(name=shm_name)
        shm.close()
        shm.unlink()
        shm = shared_memory.SharedMemory(name=shm_name, create=True, size=64)

    lock = Lock()
    p = Process(target=shm_writer, args=(shm_name, lock))
    p.start()
    p.join()

    with lock:
        read_msg = bytes(shm.buf[:20]).decode()
        print(f"  Parent read from Shared Memory: '{read_msg}'")

    shm.close()
    shm.unlink()
    print()

# --- 4. Message Queue ---
def queue_worker(q):
    for item in ["Task 1", "Task 2", "Shutdown"]:
        q.put(item)

def demo_queue():
    print("--- 4. Message Queue IPC ---")
    q = Queue()
    p = Process(target=queue_worker, args=(q,))
    p.start()
    p.join()

    while not q.empty():
        item = q.get()
        print(f"  Dequeued: {item}")
    print()

# --- 5. Signals ---
def sig_handler(signum, frame):
    print(f"  Child received signal {signum} (SIGUSR1)", flush=True)

def demo_signal():
    print("--- 5. Signal Asynchronous Notification ---")
    if not hasattr(signal, "SIGUSR1") or not hasattr(os, "fork"):
        print("Signals require Linux/WSL2.")
        return

    sys.stdout.flush()
    pid = os.fork()
    if pid == 0:
        signal.signal(signal.SIGUSR1, sig_handler)
        time.sleep(0.5)
        os._exit(0)
    else:
        time.sleep(0.1)
        os.kill(pid, signal.SIGUSR1)
        os.waitpid(pid, 0)
    print()


if __name__ == "__main__":
    try:
        multiprocessing.set_start_method("fork", force=True)
    except (RuntimeError, ValueError):
        pass
    demo_pipe()
    demo_fifo()
    demo_shared_memory()
    demo_queue()
    demo_signal()


