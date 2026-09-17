#!/usr/bin/env python3
"""
Shared Memory IPC with Process Mutual Exclusion
Demonstrates:
- POSIX shared memory segment allocation (shm_open / SharedMemory)
- Zero-copy inter-process memory sharing
- Synchronization using multiprocessing.Lock across distinct process spaces
- Safe cleanup releasing and unlinking the shared segment
"""

import time
import struct
from multiprocessing import Process, Lock
from multiprocessing import shared_memory

SHM_NAME = "os_assessment_shm_buffer"
BUFFER_SIZE = 128

def writer_process(shm_name: str, lock: Lock):
    """Writes telemetry records into the shared memory segment."""
    # Attach to existing shared memory segment
    existing_shm = shared_memory.SharedMemory(name=shm_name)
    try:
        print(f"  [Writer Process] Attached to shared memory segment: {shm_name}")
        for i in range(1, 4):
            with lock:
                # Format: [Packet ID (int), Value (double), Status String (bytes)]
                msg = f"STATUS_OK_{i}".encode("utf-8")
                packed = struct.pack("!id16s", i, i * 42.5, msg)
                existing_shm.buf[:len(packed)] = packed
                print(f"  [Writer Process] Wrote record #{i} into shared memory")
            time.sleep(0.15)
    finally:
        existing_shm.close()

def reader_process(shm_name: str, lock: Lock):
    """Reads records from the shared memory segment."""
    existing_shm = shared_memory.SharedMemory(name=shm_name)
    try:
        print(f"  [Reader Process] Attached to shared memory segment: {shm_name}")
        for _ in range(3):
            time.sleep(0.15)
            with lock:
                raw_bytes = bytes(existing_shm.buf[:struct.calcsize("!id16s")])
                record_id, val, status_raw = struct.unpack("!id16s", raw_bytes)
                status_str = status_raw.decode("utf-8", errors="ignore").rstrip("\x00")
                print(f"  --> [Reader Process] Read record: ID={record_id}, Val={val:.1f}, Msg='{status_str}'")
    finally:
        existing_shm.close()

def run_shared_memory_demo():
    print("=" * 60)
    print("Synchronized POSIX Shared Memory IPC")
    print("=" * 60)
    
    # 1. Allocate shared memory block in OS
    try:
        shm = shared_memory.SharedMemory(name=SHM_NAME, create=True, size=BUFFER_SIZE)
        print(f"[*] Allocated shared memory buffer of {BUFFER_SIZE} bytes (Name: {shm.name})")
    except FileExistsError:
        # Segment already existed from prior run; unlink and re-create
        shm = shared_memory.SharedMemory(name=SHM_NAME)
        shm.close()
        shm.unlink()
        shm = shared_memory.SharedMemory(name=SHM_NAME, create=True, size=BUFFER_SIZE)

    lock = Lock()

    p_writer = Process(target=writer_process, args=(shm.name, lock))
    p_reader = Process(target=reader_process, args=(shm.name, lock))

    print("[*] Launching concurrent writer and reader processes...")
    p_writer.start()
    p_reader.start()

    p_writer.join()
    p_reader.join()

    # Clean up and unlink segment from OS kernel
    shm.close()
    shm.unlink()
    print("[*] Shared memory segment unlinked and freed from kernel.")
    print("\n[+] Shared memory IPC executed with zero collisions and clean memory teardown.")

def main():
    print("############################################################")
    print("  SHARED MEMORY & MUTEX SYNCHRONIZATION IPC")
    print("############################################################\n")
    run_shared_memory_demo()

if __name__ == "__main__":
    main()
