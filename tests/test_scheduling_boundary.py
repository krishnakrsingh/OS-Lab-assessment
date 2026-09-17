"""
Unit Tests: Boundary & Edge Workload CPU Scheduling Cases
Tests:
- Single process workload
- Simultaneous arrivals at t=0
- Minimal burst time (BT=1)
- Explicit large idle intervals (gaps between arrivals)
- Identical burst times and priorities
"""

import unittest
from src.module3_cpu_scheduling.process import Process
from src.module3_cpu_scheduling.algorithms import (
    schedule_fcfs,
    schedule_sjf_non_preemptive,
    schedule_srtf,
    schedule_round_robin,
    schedule_priority_non_preemptive,
    schedule_priority_preemptive
)
from src.module3_cpu_scheduling.metrics import SchedulingMetrics

class TestBoundaryScheduling(unittest.TestCase):
    def test_single_process_workload(self):
        """Boundary: Exactly 1 process."""
        workload = [Process(pid="SOLO", arrival_time=5, burst_time=10, priority=1)]
        
        for sched_fn in [
            schedule_fcfs,
            schedule_sjf_non_preemptive,
            schedule_srtf,
            lambda w: schedule_round_robin(w, time_quantum=4),
            schedule_priority_non_preemptive,
            schedule_priority_preemptive
        ]:
            completed, gantt = sched_fn(workload)
            self.assertEqual(len(completed), 1)
            p = completed[0]
            self.assertEqual(p.completion_time, 15)
            self.assertEqual(p.turnaround_time, 10)
            self.assertEqual(p.waiting_time, 0)
            self.assertEqual(p.response_time, 0)
            
            # Gantt should show idle from 0 to 5, then SOLO from 5 to 15
            idles = gantt.get_idle_intervals()
            self.assertEqual(len(idles), 1)
            self.assertEqual(idles[0], (0, 5, 5))

    def test_simultaneous_arrival_at_zero(self):
        """Boundary: All processes arrive at t=0."""
        workload = [
            Process(pid="P1", arrival_time=0, burst_time=4),
            Process(pid="P2", arrival_time=0, burst_time=2),
            Process(pid="P3", arrival_time=0, burst_time=1),
        ]
        
        # In SJF, order must be P3 (1), P2 (2), P1 (4)
        completed, gantt = schedule_sjf_non_preemptive(workload)
        order = [seg.pid for seg in gantt.segments if not seg.is_idle]
        self.assertEqual(order, ["P3", "P2", "P1"])
        
        # Verify no idle time
        idles = gantt.get_idle_intervals()
        self.assertEqual(len(idles), 0)

    def test_minimal_burst_time(self):
        """Boundary: Burst time of 1."""
        workload = [
            Process(pid="P1", arrival_time=0, burst_time=1),
            Process(pid="P2", arrival_time=0, burst_time=1),
        ]
        completed, gantt = schedule_round_robin(workload, time_quantum=5)
        self.assertEqual(len(completed), 2)
        self.assertEqual(completed[0].completion_time, 1)
        self.assertEqual(completed[1].completion_time, 2)

    def test_large_idle_gaps(self):
        """Boundary: Huge gap between process arrivals to test idle handling."""
        workload = [
            Process(pid="P1", arrival_time=0, burst_time=4),
            Process(pid="P2", arrival_time=20, burst_time=5),  # 16-unit idle gap (4 to 20)
        ]
        completed, gantt = schedule_fcfs(workload)
        idles = gantt.get_idle_intervals()
        self.assertEqual(len(idles), 1)
        self.assertEqual(idles[0], (4, 20, 16))
        
        metrics = SchedulingMetrics(completed, gantt)
        self.assertEqual(metrics.total_idle_time, 16)
        self.assertEqual(metrics.total_burst, 9)
        self.assertEqual(metrics.total_time, 25)
        # Utilization = 9 / 25 = 36%
        self.assertAlmostEqual(metrics.cpu_utilization, 36.0)

    def test_identical_burst_and_priority(self):
        """Boundary: All processes have identical burst and priority (tests stable tie-breaking)."""
        workload = [
            Process(pid="P1", arrival_time=0, burst_time=3, priority=1),
            Process(pid="P2", arrival_time=0, burst_time=3, priority=1),
            Process(pid="P3", arrival_time=0, burst_time=3, priority=1),
        ]
        completed, gantt = schedule_priority_non_preemptive(workload)
        order = [seg.pid for seg in gantt.segments if not seg.is_idle]
        # Should be ordered deterministically by arrival time then PID
        self.assertEqual(order, ["P1", "P2", "P3"])

if __name__ == "__main__":
    unittest.main()
