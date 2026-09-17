"""
Scheduling Performance Metrics Calculator
Computes and formats OS scheduling metrics:
- Completion Time (CT)
- Turnaround Time (TAT = CT - AT)
- Waiting Time (WT = TAT - BT)
- Response Time (RT = First Start - AT)
- CPU Utilization Percentage
- Throughput
"""

from typing import List, Dict, Any
from .process import Process
from .gantt import GanttChart

class SchedulingMetrics:
    def __init__(self, completed_processes: List[Process], gantt: GanttChart):
        self.processes = sorted(completed_processes, key=lambda p: p.pid)
        self.gantt = gantt
        self.num_processes = len(self.processes)
        
        # Calculate summary statistics
        self.total_burst = sum(p.burst_time for p in self.processes)
        self.start_time = gantt.segments[0].start_time if gantt.segments else 0
        self.end_time = gantt.segments[-1].end_time if gantt.segments else 0
        self.total_time = max(self.end_time - self.start_time, 1)
        
        idle_intervals = gantt.get_idle_intervals()
        self.total_idle_time = sum(duration for _, _, duration in idle_intervals)
        self.cpu_utilization = (self.total_burst / self.total_time) * 100.0
        self.throughput = self.num_processes / self.total_time if self.total_time > 0 else 0.0

        self.avg_tat = sum(p.turnaround_time for p in self.processes) / self.num_processes if self.num_processes else 0.0
        self.avg_wt = sum(p.waiting_time for p in self.processes) / self.num_processes if self.num_processes else 0.0
        self.avg_rt = sum(p.response_time for p in self.processes) / self.num_processes if self.num_processes else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "num_processes": self.num_processes,
            "total_time": self.total_time,
            "total_idle_time": self.total_idle_time,
            "cpu_utilization": round(self.cpu_utilization, 2),
            "throughput": round(self.throughput, 4),
            "avg_tat": round(self.avg_tat, 2),
            "avg_wt": round(self.avg_wt, 2),
            "avg_rt": round(self.avg_rt, 2),
        }

    def render_process_table(self) -> str:
        """Generates a clearly formatted table of per-process metrics."""
        headers = ["PID", "Arrival (AT)", "Burst (BT)", "Priority", "Exit (CT)", "TAT (CT-AT)", "WT (TAT-BT)", "RT (Start-AT)"]
        rows = []
        for p in self.processes:
            rows.append([
                p.pid,
                str(p.arrival_time),
                str(p.burst_time),
                str(p.priority),
                str(p.completion_time),
                str(p.turnaround_time),
                str(p.waiting_time),
                str(p.response_time)
            ])

        # ASCII Table generation
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, val in enumerate(row):
                col_widths[i] = max(col_widths[i], len(val))

        sep_line = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
        head_line = "| " + " | ".join(h.center(col_widths[i]) for i, h in enumerate(headers)) + " |"
        
        table_lines = [sep_line, head_line, sep_line]
        for row in rows:
            r_str = "| " + " | ".join(val.center(col_widths[i]) for i, val in enumerate(row)) + " |"
            table_lines.append(r_str)
        table_lines.append(sep_line)

        summary_lines = [
            f"Average Turnaround Time (TAT) : {self.avg_tat:.2f} time units",
            f"Average Waiting Time    (WT)  : {self.avg_wt:.2f} time units",
            f"Average Response Time   (RT)  : {self.avg_rt:.2f} time units",
            f"CPU Utilization               : {self.cpu_utilization:.2f} %",
            f"Throughput                    : {self.throughput:.4f} processes/unit time"
        ]

        return "\n".join(table_lines) + "\n\n" + "\n".join(summary_lines)
