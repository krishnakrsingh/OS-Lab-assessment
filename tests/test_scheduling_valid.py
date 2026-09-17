"""
Unit Tests: Valid Workload CPU Scheduling Cases
Validates correctness of:
- FCFS, SJF (Non-preemptive), SRTF (Preemptive), Round Robin, Priority (NP & P)
- Invariant conservation laws: sum(WT) + sum(BT) == sum(TAT)
- Original dataset preservation across invocations
"""

import unittest
import copy
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

class TestValidScheduling(unittest.TestCase):
    def setUp(self):
        # Canonical 4-process workload
        self.workload = [
            Process(pid="P1", arrival_time=0, burst_time=8, priority=3),
            Process(pid="P2", arrival_time=1, burst_time=4, priority=1),
            Process(pid="P3", arrival_time=2, burst_time=9, priority=4),
            Process(pid="P4", arrival_time=3, burst_time=5, priority=2),
        ]
        self.original_backup = [copy.deepcopy(p) for p in self.workload]

    def _assert_invariants(self, completed_procs, gantt):
        """Verifies fundamental mathematical invariants of scheduling."""
        sum_bt = sum(p.burst_time for p in completed_procs)
        sum_wt = sum(p.waiting_time for p in completed_procs)
        sum_tat = sum(p.turnaround_time for p in completed_procs)

        # Invariant 1: TAT = WT + BT for every process and in aggregate
        self.assertEqual(sum_wt + sum_bt, sum_tat, "Invariant broken: sum(WT) + sum(BT) != sum(TAT)")

        for p in completed_procs:
            self.assertEqual(p.turnaround_time, p.completion_time - p.arrival_time)
            self.assertEqual(p.waiting_time, p.turnaround_time - p.burst_time)
            self.assertGreaterEqual(p.completion_time, p.arrival_time + p.burst_time)
            self.assertGreaterEqual(p.response_time, 0)
            self.assertGreaterEqual(p.waiting_time, 0)

        # Invariant 2: Original workload must remain untouched
        for orig, curr in zip(self.original_backup, self.workload):
            self.assertEqual(orig.pid, curr.pid)
            self.assertEqual(orig.arrival_time, curr.arrival_time)
            self.assertEqual(orig.burst_time, curr.burst_time)
            self.assertEqual(orig.priority, curr.priority)
            self.assertEqual(curr.remaining_time, curr.burst_time)

    def test_fcfs(self):
        completed, gantt = schedule_fcfs(self.workload)
        self.assertEqual(len(completed), 4)
        # FCFS execution order should be P1, P2, P3, P4
        order = [seg.pid for seg in gantt.segments if not seg.is_idle]
        self.assertEqual(order, ["P1", "P2", "P3", "P4"])
        self._assert_invariants(completed, gantt)

    def test_sjf_non_preemptive(self):
        completed, gantt = schedule_sjf_non_preemptive(self.workload)
        self.assertEqual(len(completed), 4)
        # P1 runs first (0..8). At t=8, P2(4), P3(9), P4(5) have arrived.
        # Next shortest is P2(4), then P4(5), then P3(9)
        order = [seg.pid for seg in gantt.segments if not seg.is_idle]
        self.assertEqual(order, ["P1", "P2", "P4", "P3"])
        self._assert_invariants(completed, gantt)

    def test_srtf_preemptive(self):
        completed, gantt = schedule_srtf(self.workload)
        self.assertEqual(len(completed), 4)
        # At t=0, P1 starts. At t=1, P2 arrives with burst 4 < P1 remaining (7). Preempt!
        self._assert_invariants(completed, gantt)
        p2 = next(p for p in completed if p.pid == "P2")
        self.assertEqual(p2.completion_time, 5)  # runs from 1 to 5 without interruption

    def test_round_robin(self):
        completed, gantt = schedule_round_robin(self.workload, time_quantum=3)
        self.assertEqual(len(completed), 4)
        self._assert_invariants(completed, gantt)

    def test_priority_non_preemptive(self):
        completed, gantt = schedule_priority_non_preemptive(self.workload)
        self.assertEqual(len(completed), 4)
        # P1 runs 0..8. Then among arrived (P2 prio 1, P3 prio 4, P4 prio 2), P2 runs next, then P4, then P3.
        order = [seg.pid for seg in gantt.segments if not seg.is_idle]
        self.assertEqual(order, ["P1", "P2", "P4", "P3"])
        self._assert_invariants(completed, gantt)

    def test_priority_preemptive(self):
        completed, gantt = schedule_priority_preemptive(self.workload)
        self.assertEqual(len(completed), 4)
        # P1 prio 3 runs from 0..1. At t=1, P2 prio 1 arrives -> preempts P1!
        self._assert_invariants(completed, gantt)
        p2 = next(p for p in completed if p.pid == "P2")
        self.assertEqual(p2.completion_time, 5)

if __name__ == "__main__":
    unittest.main()
