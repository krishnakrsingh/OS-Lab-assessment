"""
Unit Tests: Inter-Process Communication (IPC) Mechanisms
Tests:
- Anonymous Pipe byte streaming and EOF detection
- Message Queue discrete packet delivery and ordering
- Shared Memory packed struct integrity
"""

import unittest
import os
import struct
from multiprocessing import Queue, shared_memory

class TestIPCMechanisms(unittest.TestCase):
    def test_anonymous_pipe(self):
        """Validates os.pipe read/write byte fidelity."""
        if not hasattr(os, "pipe"):
            self.skipTest("os.pipe not supported on this platform.")
            
        r_fd, w_fd = os.pipe()
        payload = b"OS_ASSESSMENT_PIPE_TEST_PAYLOAD"
        os.write(w_fd, payload)
        os.close(w_fd)
        
        received = os.read(r_fd, len(payload) + 10)
        os.close(r_fd)
        self.assertEqual(received, payload)

    def test_message_queue(self):
        """Validates multiprocessing.Queue FIFO message handling."""
        q = Queue()
        items = ["alpha", "beta", "gamma", 12345]
        for item in items:
            q.put(item)
            
        retrieved = []
        for _ in range(len(items)):
            retrieved.append(q.get(timeout=2))
            
        self.assertEqual(retrieved, items)

    def test_shared_memory(self):
        """Validates shared_memory segment allocation and packing."""
        shm_name = "test_unit_shm"
        try:
            shm = shared_memory.SharedMemory(name=shm_name, create=True, size=64)
        except FileExistsError:
            shm = shared_memory.SharedMemory(name=shm_name)
            shm.close()
            shm.unlink()
            shm = shared_memory.SharedMemory(name=shm_name, create=True, size=64)
            
        try:
            val_int = 42
            val_float = 3.14159
            packed = struct.pack("!id", val_int, val_float)
            shm.buf[:len(packed)] = packed
            
            # Read back from buffer
            unpacked_int, unpacked_float = struct.unpack("!id", bytes(shm.buf[:len(packed)]))
            self.assertEqual(unpacked_int, val_int)
            self.assertAlmostEqual(unpacked_float, val_float, places=5)
        finally:
            shm.close()
            shm.unlink()

if __name__ == "__main__":
    unittest.main()
