"""
Process Control Block (PCB) Model and Input Validation
Represents a scheduled job and ensures original process data can be
safely preserved via immutable cloning during comparative algorithm runs.
"""

from dataclasses import dataclass
from typing import List, Optional
import copy

@dataclass
class Process:
    pid: str
    arrival_time: int
    burst_time: int
    priority: int = 0  # Lower integer indicates higher priority by default
    
    # State tracking attributes (populated during scheduling)
    remaining_time: int = 0
    start_time: Optional[int] = None
    completion_time: int = 0
    turnaround_time: int = 0
    waiting_time: int = 0
    response_time: int = 0

    def __post_init__(self):
        if self.remaining_time == 0:
            self.remaining_time = self.burst_time

    def clone(self) -> 'Process':
        """Returns a deep copy of this process with reset execution states."""
        return Process(
            pid=self.pid,
            arrival_time=self.arrival_time,
            burst_time=self.burst_time,
            priority=self.priority,
            remaining_time=self.burst_time,
            start_time=None,
            completion_time=0,
            turnaround_time=0,
            waiting_time=0,
            response_time=0
        )

def validate_workload(processes: List[Process]):
    """
    Validates process input according to OS scheduling rules:
    - Workload cannot be empty.
    - Process IDs must be non-empty strings and unique.
    - Arrival time must be an integer >= 0.
    - Burst time must be an integer > 0 (boundary check).
    """
    if not processes:
        raise ValueError("Validation Error: Process workload cannot be empty.")
    
    seen_pids = set()
    for p in processes:
        if not isinstance(p.pid, str) or not p.pid.strip():
            raise ValueError(f"Validation Error: Process PID must be a non-empty string, got {p.pid!r}")
        if p.pid in seen_pids:
            raise ValueError(f"Validation Error: Duplicate Process ID detected '{p.pid}'. PIDs must be unique.")
        seen_pids.add(p.pid)
        
        if not isinstance(p.arrival_time, int) or p.arrival_time < 0:
            raise ValueError(f"Validation Error: Process {p.pid} has invalid arrival_time={p.arrival_time}. Must be integer >= 0.")
            
        if not isinstance(p.burst_time, int) or p.burst_time <= 0:
            raise ValueError(f"Validation Error: Process {p.pid} has invalid burst_time={p.burst_time}. Must be integer > 0.")
            
        if not isinstance(p.priority, int):
            raise ValueError(f"Validation Error: Process {p.pid} has invalid priority={p.priority}. Must be integer.")

def clone_workload(processes: List[Process]) -> List[Process]:
    """
    Safely clones a list of processes to preserve the original dataset
    when comparing multiple scheduling algorithms.
    """
    validate_workload(processes)
    return [p.clone() for p in processes]
