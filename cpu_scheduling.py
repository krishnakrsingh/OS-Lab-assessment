#!/usr/bin/env python3
import copy

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        self.start_time = None
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.response_time = 0

    def copy(self):
        return copy.deepcopy(self)

def render_gantt(chart):
    # chart is list of (pid, start, end)
    top = "+"
    mid = "|"
    bot = "+"
    times = [str(chart[0][1])]

    for pid, s, e in chart:
        width = max(len(pid) + 2, 6)
        top += "-" * width + "+"
        mid += pid.center(width) + "|"
        bot += "-" * width + "+"
        times.append(str(e))

    time_line = times[0]
    for i in range(len(chart)):
        width = max(len(chart[i][0]) + 2, 6)
        time_line += str(times[i+1]).rjust(width + 1)

    print(top)
    print(mid)
    print(bot)
    print(time_line)

def print_metrics(procs, chart, algo_name):
    print(f"\n==================== {algo_name} ====================")
    
    # Execution order & idle intervals
    order = [pid for pid, _, _ in chart]
    idles = [(s, e) for pid, s, e in chart if pid == "[IDLE]"]
    
    print("Execution Order:", " -> ".join(order))
    if idles:
        print("Idle Intervals :", ", ".join([f"[{s} to {e}]" for s, e in idles]))
    else:
        print("Idle Intervals : None")

    print("\nGantt Chart:")
    render_gantt(chart)

    print("\nPID | AT | BT | Priority | CT | TAT | WT | RT")
    print("-" * 48)
    for p in sorted(procs, key=lambda x: x.pid):
        print(f"{p.pid:>3} | {p.arrival_time:>2} | {p.burst_time:>2} | {p.priority:>8} | {p.completion_time:>2} | {p.turnaround_time:>3} | {p.waiting_time:>2} | {p.response_time:>2}")

    avg_tat = sum(p.turnaround_time for p in procs) / len(procs)
    avg_wt = sum(p.waiting_time for p in procs) / len(procs)
    avg_rt = sum(p.response_time for p in procs) / len(procs)
    total_time = chart[-1][2]
    total_busy = sum(p.burst_time for p in procs)
    cpu_util = (total_busy / total_time) * 100

    print(f"\nAverage TAT : {avg_tat:.2f}")
    print(f"Average WT  : {avg_wt:.2f}")
    print(f"Average RT  : {avg_rt:.2f}")
    print(f"CPU Util    : {cpu_util:.1f}%")
    print(f"Throughput  : {len(procs)/total_time:.3f} procs/unit")
    
    return {"algo": algo_name, "tat": avg_tat, "wt": avg_wt, "rt": avg_rt, "util": cpu_util}

# --- Scheduling Algorithms ---

def fcfs(original_procs):
    procs = [p.copy() for p in original_procs]
    procs.sort(key=lambda x: (x.arrival_time, x.pid))
    
    chart = []
    t = 0
    for p in procs:
        if t < p.arrival_time:
            chart.append(("[IDLE]", t, p.arrival_time))
            t = p.arrival_time
        p.start_time = t
        p.completion_time = t + p.burst_time
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
        p.response_time = p.start_time - p.arrival_time
        chart.append((p.pid, t, p.completion_time))
        t = p.completion_time
    return procs, chart

def sjf_non_preemptive(original_procs):
    procs = [p.copy() for p in original_procs]
    chart = []
    t = 0
    completed = []
    pool = procs.copy()

    while len(completed) < len(procs):
        arrived = [p for p in pool if p.arrival_time <= t]
        if not arrived:
            next_arr = min(p.arrival_time for p in pool)
            chart.append(("[IDLE]", t, next_arr))
            t = next_arr
            continue
            
        chosen = min(arrived, key=lambda x: (x.burst_time, x.arrival_time, x.pid))
        chosen.start_time = t
        chosen.completion_time = t + chosen.burst_time
        chosen.turnaround_time = chosen.completion_time - chosen.arrival_time
        chosen.waiting_time = chosen.turnaround_time - chosen.burst_time
        chosen.response_time = chosen.start_time - chosen.arrival_time
        
        chart.append((chosen.pid, t, chosen.completion_time))
        t = chosen.completion_time
        pool.remove(chosen)
        completed.append(chosen)

    return completed, chart

def srtf_preemptive(original_procs):
    procs = [p.copy() for p in original_procs]
    chart = []
    t = 0
    completed = []
    n = len(procs)

    while len(completed) < n:
        arrived = [p for p in procs if p.arrival_time <= t and p.remaining_time > 0]
        if not arrived:
            next_arr = min(p.arrival_time for p in procs if p.remaining_time > 0)
            chart.append(("[IDLE]", t, next_arr))
            t = next_arr
            continue

        chosen = min(arrived, key=lambda x: (x.remaining_time, x.arrival_time, x.pid))
        if chosen.start_time is None:
            chosen.start_time = t

        # Append to chart or extend last block
        if chart and chart[-1][0] == chosen.pid and chart[-1][2] == t:
            chart[-1] = (chosen.pid, chart[-1][1], t + 1)
        else:
            chart.append((chosen.pid, t, t + 1))

        chosen.remaining_time -= 1
        t += 1

        if chosen.remaining_time == 0:
            chosen.completion_time = t
            chosen.turnaround_time = chosen.completion_time - chosen.arrival_time
            chosen.waiting_time = chosen.turnaround_time - chosen.burst_time
            chosen.response_time = chosen.start_time - chosen.arrival_time
            completed.append(chosen)

    return procs, chart

def round_robin(original_procs, quantum=2):
    procs = [p.copy() for p in original_procs]
    procs.sort(key=lambda x: (x.arrival_time, x.pid))
    
    chart = []
    t = 0
    ready = []
    completed = []
    added = set()

    def check_arrivals(curr_t):
        for p in procs:
            if p.arrival_time <= curr_t and p.pid not in added:
                ready.append(p)
                added.add(p.pid)

    check_arrivals(0)

    while len(completed) < len(procs):
        if not ready:
            unadded = [p for p in procs if p.pid not in added]
            if unadded:
                next_arr = min(p.arrival_time for p in unadded)
                chart.append(("[IDLE]", t, next_arr))
                t = next_arr
                check_arrivals(t)
            continue

        curr = ready.pop(0)
        if curr.start_time is None:
            curr.start_time = t

        slice_time = min(quantum, curr.remaining_time)
        chart.append((curr.pid, t, t + slice_time))
        t += slice_time
        curr.remaining_time -= slice_time

        check_arrivals(t)

        if curr.remaining_time == 0:
            curr.completion_time = t
            curr.turnaround_time = curr.completion_time - curr.arrival_time
            curr.waiting_time = curr.turnaround_time - curr.burst_time
            curr.response_time = curr.start_time - curr.arrival_time
            completed.append(curr)
        else:
            ready.append(curr)

    return procs, chart

def priority_non_preemptive(original_procs):
    procs = [p.copy() for p in original_procs]
    chart = []
    t = 0
    completed = []
    pool = procs.copy()

    while len(completed) < len(procs):
        arrived = [p for p in pool if p.arrival_time <= t]
        if not arrived:
            next_arr = min(p.arrival_time for p in pool)
            chart.append(("[IDLE]", t, next_arr))
            t = next_arr
            continue
            
        chosen = min(arrived, key=lambda x: (x.priority, x.arrival_time, x.pid))
        chosen.start_time = t
        chosen.completion_time = t + chosen.burst_time
        chosen.turnaround_time = chosen.completion_time - chosen.arrival_time
        chosen.waiting_time = chosen.turnaround_time - chosen.burst_time
        chosen.response_time = chosen.start_time - chosen.arrival_time
        
        chart.append((chosen.pid, t, chosen.completion_time))
        t = chosen.completion_time
        pool.remove(chosen)
        completed.append(chosen)

    return completed, chart

def priority_preemptive(original_procs):
    procs = [p.copy() for p in original_procs]
    chart = []
    t = 0
    completed = []
    n = len(procs)

    while len(completed) < n:
        arrived = [p for p in procs if p.arrival_time <= t and p.remaining_time > 0]
        if not arrived:
            next_arr = min(p.arrival_time for p in procs if p.remaining_time > 0)
            chart.append(("[IDLE]", t, next_arr))
            t = next_arr
            continue

        chosen = min(arrived, key=lambda x: (x.priority, x.arrival_time, x.pid))
        if chosen.start_time is None:
            chosen.start_time = t

        if chart and chart[-1][0] == chosen.pid and chart[-1][2] == t:
            chart[-1] = (chosen.pid, chart[-1][1], t + 1)
        else:
            chart.append((chosen.pid, t, t + 1))

        chosen.remaining_time -= 1
        t += 1

        if chosen.remaining_time == 0:
            chosen.completion_time = t
            chosen.turnaround_time = chosen.completion_time - chosen.arrival_time
            chosen.waiting_time = chosen.turnaround_time - chosen.burst_time
            chosen.response_time = chosen.start_time - chosen.arrival_time
            completed.append(chosen)

    return procs, chart

def main():
    # Canonical workload
    workload = [
        Process("P1", arrival_time=0, burst_time=5, priority=3),
        Process("P2", arrival_time=1, burst_time=3, priority=1),
        Process("P3", arrival_time=2, burst_time=8, priority=4),
        Process("P4", arrival_time=3, burst_time=6, priority=2),
        Process("P5", arrival_time=15, burst_time=4, priority=2), # arrives later to demo idle time
    ]

    # Preserve original process data check
    original_backup = [(p.pid, p.arrival_time, p.burst_time, p.priority) for p in workload]

    summaries = []
    
    p, c = fcfs(workload)
    summaries.append(print_metrics(p, c, "FCFS"))

    p, c = sjf_non_preemptive(workload)
    summaries.append(print_metrics(p, c, "SJF (Non-Preemptive)"))

    p, c = srtf_preemptive(workload)
    summaries.append(print_metrics(p, c, "SRTF (Preemptive SJF)"))

    p, c = round_robin(workload, quantum=2)
    summaries.append(print_metrics(p, c, "Round Robin (q=2)"))

    p, c = priority_non_preemptive(workload)
    summaries.append(print_metrics(p, c, "Priority (Non-Preemptive)"))

    p, c = priority_preemptive(workload)
    summaries.append(print_metrics(p, c, "Priority (Preemptive)"))

    # Check that original workload remained untouched
    current_data = [(p.pid, p.arrival_time, p.burst_time, p.priority) for p in workload]
    assert original_backup == current_data, "Error: original process data was mutated!"
    print("\n[OK] Confirmed: Original process data was preserved across all algorithms.")

    # Comparative summary table
    print("\n==================== COMPARISON SUMMARY ====================")
    print(f"{'Algorithm':<28} | {'Avg TAT':<8} | {'Avg WT':<8} | {'Avg RT':<8} | {'CPU Util'}")
    print("-" * 65)
    for s in summaries:
        print(f"{s['algo']:<28} | {s['tat']:<8.2f} | {s['wt']:<8.2f} | {s['rt']:<8.2f} | {s['util']:.1f}%")

if __name__ == "__main__":
    main()
