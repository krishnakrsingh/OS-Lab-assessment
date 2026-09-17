"""
Unit Tests: Invalid & Negative Input Validation
Tests input sanitization and exception handling:
- Negative burst times
- Zero burst times
- Negative arrival times
- Empty process workloads
- Duplicate process identifiers
- Non-integer types
- Non-positive Round Robin time quantum
"""

import unittest
from src.module3_cpu_scheduling.process import Process, validate_workload
from src.module3_cpu_scheduling.algorithms import schedule_fcfs, schedule_round_robin

class TestInvalidScheduling(unittest.TestCase):
    def test_empty_workload(self):
        with self.assertRaises(ValueError) as ctx:
            validate_workload([])
        self.assertIn("empty", str(ctx.exception).lower())

    def test_negative_burst_time(self):
        workload = [Process(pid="P1", arrival_time=0, burst_time=-5)]
        with self.assertRaises(ValueError) as ctx:
            validate_workload(workload)
        self.assertIn("burst_time", str(ctx.exception))

    def test_zero_burst_time(self):
        workload = [Process(pid="P1", arrival_time=0, burst_time=0)]
        with self.assertRaises(ValueError) as ctx:
            validate_workload(workload)
        self.assertIn("burst_time", str(ctx.exception))

    def test_negative_arrival_time(self):
        workload = [Process(pid="P1", arrival_time=-2, burst_time=5)]
        with self.assertRaises(ValueError) as ctx:
            validate_workload(workload)
        self.assertIn("arrival_time", str(ctx.exception))

    def test_duplicate_pid(self):
        workload = [
            Process(pid="P1", arrival_time=0, burst_time=3),
            Process(pid="P1", arrival_time=1, burst_time=4),
        ]
        with self.assertRaises(ValueError) as ctx:
            validate_workload(workload)
        self.assertIn("duplicate", str(ctx.exception).lower())

    def test_invalid_data_types(self):
        # String arrival time
        with self.assertRaises(ValueError):
            validate_workload([Process(pid="P1", arrival_time="zero", burst_time=5)]) # type: ignore
        # Float burst time
        with self.assertRaises(ValueError):
            validate_workload([Process(pid="P1", arrival_time=0, burst_time=3.5)]) # type: ignore

    def test_invalid_round_robin_quantum(self):
        workload = [Process(pid="P1", arrival_time=0, burst_time=5)]
        with self.assertRaises(ValueError) as ctx:
            schedule_round_robin(workload, time_quantum=0)
        self.assertIn("quantum", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            schedule_round_robin(workload, time_quantum=-2)
        self.assertIn("quantum", str(ctx.exception).lower())

if __name__ == "__main__":
    unittest.main()
