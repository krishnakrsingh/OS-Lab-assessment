"""
CPU Scheduling Algorithms
Implements:
1. First-Come, First-Served (FCFS)
2. Shortest Job First (SJF - Non-preemptive)
3. Shortest Remaining Time First (SRTF - Preemptive SJF)
4. Round Robin (RR - Time Quantum based)
5. Priority Scheduling (Non-preemptive)
6. Priority Scheduling (Preemptive)

All algorithms operate on safely cloned workloads to preserve original inputs.
Idle intervals are explicitly recorded in the Gantt timeline.
"""

from typing import List, Tuple
from .process import Process, clone_workload
from .gantt import GanttChart

def schedule_fcfs(raw_processes: List[Process]) -> Tuple[List[Process], GanttChart]:
    """First-Come, First-Served (FCFS) scheduling."""
    processes = clone_workload(raw_processes)
    # Sort primarily by arrival time, secondarily by PID for deterministic order
    processes.sort(key=lambda p: (p.arrival_time, p.pid))
    
    gantt = GanttChart()
    current_time = 0

    for p in processes:
        if current_time < p.arrival_time:
            # CPU is idle waiting for this job
            gantt.add_segment(current_time, p.arrival_time, "[IDLE]")
            current_time = p.arrival_time

        start = current_time
        finish = current_time + p.burst_time
        gantt.add_segment(start, finish, p.pid)

        p.start_time = start
        p.completion_time = finish
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
        p.response_time = p.start_time - p.arrival_time
        p.remaining_time = 0
        current_time = finish

    return processes, gantt

def schedule_sjf_non_preemptive(raw_processes: List[Process]) -> Tuple[List[Process], GanttChart]:
    """Shortest Job First (SJF - Non-Preemptive)."""
    processes = clone_workload(raw_processes)
    gantt = GanttChart()
    
    current_time = 0
    completed = []
    ready_pool = processes.copy()

    while len(completed) < len(processes):
        # Eligible processes that have arrived by current_time
        arrived = [p for p in ready_pool if p.arrival_time <= current_time]
        
        if not arrived:
            # CPU is idle until next process arrival
            next_arrival = min(p.arrival_time for p in ready_pool)
            gantt.add_segment(current_time, next_arrival, "[IDLE]")
            current_time = next_arrival
            continue

        # Choose job with shortest burst time; tie break by arrival time, then pid
        chosen = min(arrived, key=lambda p: (p.burst_time, p.arrival_time, p.pid))
        
        start = current_time
        finish = current_time + chosen.burst_time
        gantt.add_segment(start, finish, chosen.pid)

        chosen.start_time = start
        chosen.completion_time = finish
        chosen.turnaround_time = chosen.completion_time - chosen.arrival_time
        chosen.waiting_time = chosen.turnaround_time - chosen.burst_time
        chosen.response_time = chosen.start_time - chosen.arrival_time
        chosen.remaining_time = 0

        current_time = finish
        ready_pool.remove(chosen)
        completed.append(chosen)

    return completed, gantt

def schedule_srtf(raw_processes: List[Process]) -> Tuple[List[Process], GanttChart]:
    """Shortest Remaining Time First (SRTF - Preemptive SJF)."""
    processes = clone_workload(raw_processes)
    gantt = GanttChart()
    
    current_time = 0
    completed = []
    num_processes = len(processes)

    # Key timeline events: all arrival times
    while len(completed) < num_processes:
        arrived = [p for p in processes if p.arrival_time <= current_time and p.remaining_time > 0]
        
        if not arrived:
            # Advance to earliest upcoming arrival
            uncompleted = [p for p in processes if p.remaining_time > 0]
            next_arrival = min(p.arrival_time for p in uncompleted)
            gantt.add_segment(current_time, next_arrival, "[IDLE]")
            current_time = next_arrival
            continue

        # Select process with minimum remaining time; tie-break by arrival time, then pid
        chosen = min(arrived, key=lambda p: (p.remaining_time, p.arrival_time, p.pid))
        
        if chosen.start_time is None:
            chosen.start_time = current_time

        # Run for 1 time unit (simulation granularity)
        gantt.add_segment(current_time, current_time + 1, chosen.pid)
        chosen.remaining_time -= 1
        current_time += 1

        if chosen.remaining_time == 0:
            chosen.completion_time = current_time
            chosen.turnaround_time = chosen.completion_time - chosen.arrival_time
            chosen.waiting_time = chosen.turnaround_time - chosen.burst_time
            chosen.response_time = chosen.start_time - chosen.arrival_time
            completed.append(chosen)

    return processes, gantt

def schedule_round_robin(raw_processes: List[Process], time_quantum: int = 2) -> Tuple[List[Process], GanttChart]:
    """
    Round Robin (RR) Scheduling with configurable time quantum.
    Maintains a FIFO ready queue.
    """
    if time_quantum <= 0:
        raise ValueError(f"Time quantum must be a positive integer, got {time_quantum}")

    processes = clone_workload(raw_processes)
    # Sort initially by arrival time, then PID
    processes.sort(key=lambda p: (p.arrival_time, p.pid))
    
    gantt = GanttChart()
    current_time = 0
    ready_queue: List[Process] = []
    completed: List[Process] = []
    num_processes = len(processes)

    # Track which processes have been admitted to the ready queue
    admitted = set()

    def admit_arrived_jobs(until_time: int):
        for p in processes:
            if p.arrival_time <= until_time and p.pid not in admitted:
                ready_queue.append(p)
                admitted.add(p.pid)

    admit_arrived_jobs(current_time)

    while len(completed) < num_processes:
        if not ready_queue:
            # Find next arriving job
            unadmitted = [p for p in processes if p.pid not in admitted]
            if unadmitted:
                next_arrival = min(p.arrival_time for p in unadmitted)
                gantt.add_segment(current_time, next_arrival, "[IDLE]")
                current_time = next_arrival
                admit_arrived_jobs(current_time)
            continue

        curr = ready_queue.pop(0)

        if curr.start_time is None:
            curr.start_time = current_time

        exec_slice = min(time_quantum, curr.remaining_time)
        start = current_time
        finish = current_time + exec_slice
        
        gantt.add_segment(start, finish, curr.pid)
        curr.remaining_time -= exec_slice
        current_time = finish

        # Admit any processes that arrived during this time slice BEFORE re-queuing curr
        admit_arrived_jobs(current_time)

        if curr.remaining_time == 0:
            curr.completion_time = current_time
            curr.turnaround_time = curr.completion_time - curr.arrival_time
            curr.waiting_time = curr.turnaround_time - curr.burst_time
            curr.response_time = curr.start_time - curr.arrival_time
            completed.append(curr)
        else:
            ready_queue.append(curr)

    return processes, gantt

def schedule_priority_non_preemptive(raw_processes: List[Process]) -> Tuple[List[Process], GanttChart]:
    """Priority Scheduling (Non-Preemptive). Lower integer = higher priority."""
    processes = clone_workload(raw_processes)
    gantt = GanttChart()
    
    current_time = 0
    completed = []
    ready_pool = processes.copy()

    while len(completed) < len(processes):
        arrived = [p for p in ready_pool if p.arrival_time <= current_time]
        
        if not arrived:
            next_arrival = min(p.arrival_time for p in ready_pool)
            gantt.add_segment(current_time, next_arrival, "[IDLE]")
            current_time = next_arrival
            continue

        # Choose highest priority (lowest integer); tie break by arrival time, then PID
        chosen = min(arrived, key=lambda p: (p.priority, p.arrival_time, p.pid))

        start = current_time
        finish = current_time + chosen.burst_time
        gantt.add_segment(start, finish, chosen.pid)

        chosen.start_time = start
        chosen.completion_time = finish
        chosen.turnaround_time = chosen.completion_time - chosen.arrival_time
        chosen.waiting_time = chosen.turnaround_time - chosen.burst_time
        chosen.response_time = chosen.start_time - chosen.arrival_time
        chosen.remaining_time = 0

        current_time = finish
        ready_pool.remove(chosen)
        completed.append(chosen)

    return completed, gantt

def schedule_priority_preemptive(raw_processes: List[Process]) -> Tuple[List[Process], GanttChart]:
    """Priority Scheduling (Preemptive). Preempts when a higher-priority process arrives."""
    processes = clone_workload(raw_processes)
    gantt = GanttChart()
    
    current_time = 0
    completed = []
    num_processes = len(processes)

    while len(completed) < num_processes:
        arrived = [p for p in processes if p.arrival_time <= current_time and p.remaining_time > 0]
        
        if not arrived:
            uncompleted = [p for p in processes if p.remaining_time > 0]
            next_arrival = min(p.arrival_time for p in uncompleted)
            gantt.add_segment(current_time, next_arrival, "[IDLE]")
            current_time = next_arrival
            continue

        # Choose highest priority (lowest numeric value); tie-break by arrival time, then PID
        chosen = min(arrived, key=lambda p: (p.priority, p.arrival_time, p.pid))

        if chosen.start_time is None:
            chosen.start_time = current_time

        gantt.add_segment(current_time, current_time + 1, chosen.pid)
        chosen.remaining_time -= 1
        current_time += 1

        if chosen.remaining_time == 0:
            chosen.completion_time = current_time
            chosen.turnaround_time = chosen.completion_time - chosen.arrival_time
            chosen.waiting_time = chosen.turnaround_time - chosen.burst_time
            chosen.response_time = chosen.start_time - chosen.arrival_time
            completed.append(chosen)

    return processes, gantt
