#!/usr/bin/env python3
"""
CPU Scheduling Simulation Runner and Comparative Benchmark
Runs all major CPU scheduling algorithms on an identical workload,
guaranteeing preservation of the original input data.
Displays:
- Execution order
- Explicit idle intervals
- Individual ASCII Gantt charts
- Detailed per-process metrics
- Comparative summary across all algorithms
"""

import copy
from typing import List
from .process import Process, clone_workload
from .algorithms import (
    schedule_fcfs,
    schedule_sjf_non_preemptive,
    schedule_srtf,
    schedule_round_robin,
    schedule_priority_non_preemptive,
    schedule_priority_preemptive,
)
from .metrics import SchedulingMetrics

def run_all_schedulers(workload: List[Process], time_quantum: int = 2):
    print("=" * 75)
    print("  CPU SCHEDULING ALGORITHMS SIMULATION & COMPARATIVE ANALYSIS")
    print("=" * 75)
    
    # Take a deep snapshot of original workload to verify preservation
    original_snapshot = [copy.deepcopy(p) for p in workload]
    
    algorithms = [
        ("First-Come, First-Served (FCFS)", lambda w: schedule_fcfs(w)),
        ("Shortest Job First (SJF - Non-Preemptive)", lambda w: schedule_sjf_non_preemptive(w)),
        ("Shortest Remaining Time First (SRTF - Preemptive)", lambda w: schedule_srtf(w)),
        (f"Round Robin (RR, Quantum={time_quantum})", lambda w: schedule_round_robin(w, time_quantum=time_quantum)),
        ("Priority (Non-Preemptive)", lambda w: schedule_priority_non_preemptive(w)),
        ("Priority (Preemptive)", lambda w: schedule_priority_preemptive(w)),
    ]

    summary_records = []

    for name, schedule_fn in algorithms:
        print(f"\n>> Algorithm: {name}")
        print("-" * 75)
        
        # Execute scheduler
        completed_procs, gantt = schedule_fn(workload)
        metrics = SchedulingMetrics(completed_procs, gantt)
        
        # 1. Display Execution Order
        exec_order = gantt.get_execution_order()
        print(f"[*] Execution Order : {' -> '.join(exec_order)}")
        
        # 2. Display Idle Intervals
        idles = gantt.get_idle_intervals()
        if idles:
            idle_strs = [f"[{start} to {end} (duration={dur})]" for start, end, dur in idles]
            print(f"[*] Idle Intervals  : {', '.join(idle_strs)}")
        else:
            print("[*] Idle Intervals  : None (CPU 100% engaged after arrival)")

        # 3. ASCII Gantt Chart
        print("\n[*] Gantt Chart:")
        print(gantt.render())
        print()

        # 4. Detailed Process Metrics Table
        print(metrics.render_process_table())
        print("-" * 75)
        
        summary_records.append({
            "Algorithm": name,
            "Avg TAT": metrics.avg_tat,
            "Avg WT": metrics.avg_wt,
            "Avg RT": metrics.avg_rt,
            "CPU Util (%)": metrics.cpu_utilization,
            "Throughput": metrics.throughput,
        })

    # Verify original data preservation
    print("\n" + "=" * 75)
    print("  ORIGINAL DATA INTEGRITY CHECK")
    print("=" * 75)
    intact = True
    for orig, current in zip(original_snapshot, workload):
        if (orig.pid != current.pid or 
            orig.arrival_time != current.arrival_time or 
            orig.burst_time != current.burst_time or 
            orig.priority != current.priority or
            current.remaining_time != current.burst_time):
            intact = False
            break
            
    if intact:
        print("[+] VERIFIED: Original process data preserved intact across all algorithm comparisons.")
    else:
        print("[!] WARNING: Original process data was altered during scheduling!")

    # Comparative Summary Table
    print("\n" + "=" * 75)
    print("  ALGORITHM COMPARISON SUMMARY")
    print("=" * 75)
    
    headers = ["Algorithm", "Avg TAT", "Avg WT", "Avg RT", "CPU Util %", "Throughput"]
    col_widths = [max(len(h), 12) for h in headers]
    col_widths[0] = 38
    
    sep_line = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    head_line = "| " + " | ".join(h.center(col_widths[i]) for i, h in enumerate(headers)) + " |"
    
    print(sep_line)
    print(head_line)
    print(sep_line)
    
    for r in summary_records:
        row_vals = [
            r["Algorithm"].ljust(col_widths[0]),
            f"{r['Avg TAT']:.2f}".center(col_widths[1]),
            f"{r['Avg WT']:.2f}".center(col_widths[2]),
            f"{r['Avg RT']:.2f}".center(col_widths[3]),
            f"{r['CPU Util (%)']:.1f}%".center(col_widths[4]),
            f"{r['Throughput']:.3f}".center(col_widths[5]),
        ]
        print("| " + " | ".join(row_vals) + " |")
    print(sep_line)

def get_default_sample_workload() -> List[Process]:
    """
    Standard sample workload with varied arrival times, burst times,
    and priorities, including an initial arrival delay to demonstrate idle time.
    """
    return [
        Process(pid="P1", arrival_time=0, burst_time=5, priority=3),
        Process(pid="P2", arrival_time=1, burst_time=3, priority=1),
        Process(pid="P3", arrival_time=2, burst_time=8, priority=4),
        Process(pid="P4", arrival_time=3, burst_time=6, priority=2),
        Process(pid="P5", arrival_time=15, burst_time=4, priority=2),  # Arrives late to force idle interval
    ]

def main():
    workload = get_default_sample_workload()
    run_all_schedulers(workload, time_quantum=2)

if __name__ == "__main__":
    main()
