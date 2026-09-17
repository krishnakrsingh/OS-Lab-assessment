#!/usr/bin/env python3
"""
Test cases for CPU Scheduling:
- Valid test cases (standard multi-process workloads)
- Boundary test cases (single process, zero arrival, high idle gap, minimal burst)
- Invalid test cases (negative arrival/burst, zero burst, bad input types)
"""

from cpu_scheduling import Process, fcfs, sjf_non_preemptive, srtf_preemptive, round_robin

def validate_input(processes):
    if not processes:
        raise ValueError("Error: Workload cannot be empty.")
    seen = set()
    for p in processes:
        if not isinstance(p.arrival_time, int) or p.arrival_time < 0:
            raise ValueError(f"Invalid arrival time for {p.pid}: {p.arrival_time}")
        if not isinstance(p.burst_time, int) or p.burst_time <= 0:
            raise ValueError(f"Invalid burst time for {p.pid}: {p.burst_time}")
        if p.pid in seen:
            raise ValueError(f"Duplicate PID found: {p.pid}")
        seen.add(p.pid)

def run_tests():
    print("--- Running Test Cases ---\n")

    # 1. Valid Cases
    print("1. Valid Cases:")
    procs = [
        Process("P1", 0, 4),
        Process("P2", 1, 2),
        Process("P3", 2, 1),
    ]
    validate_input(procs)
    p_fcfs, _ = fcfs(procs)
    assert [p.completion_time for p in p_fcfs] == [4, 6, 7]
    print("   [PASS] Valid standard workload (FCFS completion times match)")

    # 2. Boundary Cases
    print("2. Boundary Cases:")
    
    # Boundary: Single process
    single = [Process("SOLO", 2, 5)]
    validate_input(single)
    p_single, chart_single = fcfs(single)
    assert p_single[0].completion_time == 7
    assert chart_single[0][0] == "[IDLE]" # idle from 0 to 2
    print("   [PASS] Boundary 1: Single process with initial idle period")

    # Boundary: Simultaneous arrival at t=0
    simult = [Process("A", 0, 4), Process("B", 0, 1)]
    validate_input(simult)
    p_sjf, _ = sjf_non_preemptive(simult)
    assert p_sjf[0].pid == "B" # B runs first because BT=1 < 4
    print("   [PASS] Boundary 2: Simultaneous arrival at t=0 (SJF shortest picked first)")

    # Boundary: Minimal burst time (BT=1)
    min_bt = [Process("P1", 0, 1), Process("P2", 1, 1)]
    validate_input(min_bt)
    p_rr, _ = round_robin(min_bt, quantum=2)
    assert p_rr[0].completion_time == 1 and p_rr[1].completion_time == 2
    print("   [PASS] Boundary 3: Minimal burst times (BT=1)")

    # Boundary: Large idle gap between processes
    gap_procs = [Process("P1", 0, 2), Process("P2", 10, 3)]
    validate_input(gap_procs)
    _, gap_chart = fcfs(gap_procs)
    has_idle = any(pid == "[IDLE]" and s == 2 and e == 10 for pid, s, e in gap_chart)
    assert has_idle
    print("   [PASS] Boundary 4: Large idle gap correctly logged in Gantt chart")

    # 3. Invalid Cases (Error Handling)
    print("3. Invalid Cases & Error Handling:")

    # Negative burst
    try:
        validate_input([Process("P1", 0, -5)])
        assert False, "Should have failed on negative burst"
    except ValueError as e:
        print(f"   [PASS] Caught invalid burst: {e}")

    # Zero burst
    try:
        validate_input([Process("P1", 0, 0)])
        assert False, "Should have failed on zero burst"
    except ValueError as e:
        print(f"   [PASS] Caught zero burst: {e}")

    # Negative arrival
    try:
        validate_input([Process("P1", -2, 5)])
        assert False, "Should have failed on negative arrival"
    except ValueError as e:
        print(f"   [PASS] Caught negative arrival: {e}")

    # Empty workload
    try:
        validate_input([])
        assert False, "Should have failed on empty workload"
    except ValueError as e:
        print(f"   [PASS] Caught empty workload: {e}")

    # Duplicate PID
    try:
        validate_input([Process("P1", 0, 3), Process("P1", 1, 4)])
        assert False, "Should have failed on duplicate PID"
    except ValueError as e:
        print(f"   [PASS] Caught duplicate PID: {e}")

    print("\n[OK] All valid, boundary, and invalid test cases passed.")

if __name__ == "__main__":
    run_tests()
