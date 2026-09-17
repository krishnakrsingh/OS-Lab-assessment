# Architectural Design: System Calls, Process Engine & IPC Framework

This document details the modular layout, system call interaction layers, scheduling engine design, and synchronization models implemented in this repository.

---

## 1. Directory & Component Architecture

```
os-assesment/
├── README.md                           # Project execution overview and submission documentation
├── requirements.txt                    # Minimal dependencies
├── run_all.py                          # Master test runner & terminal evidence generator
├── docs/
│   ├── CALCULATIONS_AND_OBSERVATIONS.md # Hand derivations, comparisons, and OS metrics
│   └── ARCHITECTURE.md                 # Design decisions and data structures
├── terminal_evidence/                  # Real terminal output logs
│   ├── 01_system_calls_and_proc.txt
│   ├── 02_process_and_threads.txt
│   ├── 03_cpu_scheduling.txt
│   ├── 04_ipc_mechanisms.txt
│   └── 05_master_verification.txt
├── src/
│   ├── module1_sys_process/            # System calls, proc observation, zombie/orphan demo
│   ├── module2_proc_threads/           # Fork lifecycle, thread locks/semaphores, benchmarking
│   ├── module3_cpu_scheduling/         # Scheduling simulation, Gantt renderer, and metrics
│   └── module4_ipc/                    # Pipes, FIFOs, Shared Memory, Message Queues, Signals
└── tests/                              # Valid, boundary, and invalid/negative test cases
```

---

## 2. Process Control Block (PCB) & State Preservation

The `Process` dataclass in `src/module3_cpu_scheduling/process.py` models an operating system Process Control Block (PCB):

```python
@dataclass
class Process:
    pid: str
    arrival_time: int
    burst_time: int
    priority: int = 0
    remaining_time: int = 0
    start_time: Optional[int] = None
    completion_time: int = 0
    turnaround_time: int = 0
    waiting_time: int = 0
    response_time: int = 0
```

### Data Preservation Mechanism
To guarantee that comparisons between algorithms are fair and deterministic, `clone_workload()` creates deep clones of all process objects before passing them to any scheduling routine. This ensures:
1. The original list of processes remains immutable.
2. In-place state modifications (like `remaining_time`, `completion_time`) do not leak between algorithm runs.

---

## 3. CPU Scheduling Engine

Each algorithm function conforms to the standard signature:
```python
def schedule_algorithm(raw_processes: List[Process]) -> Tuple[List[Process], GanttChart]:
```

### Key Mechanisms:
- **Idle Interval Tracking**: When no process is ready at current time $t$, the scheduler advances time to the next process arrival and appends a `[IDLE]` segment to the Gantt chart.
- **Granular Preemption**: Preemptive algorithms (SRTF and Preemptive Priority) evaluate the ready queue at each discrete time tick ($t \to t + 1$) or arrival boundary, preempting the active job if an arriving job has a lower remaining burst time or higher priority (lower numeric value).
- **Round Robin FIFO Queue**: Maintains a strict FIFO ready queue. Any job that arrives while a process is executing its time slice is enqueued **before** the currently completing slice is re-appended, adhering to standard POSIX round-robin semantics.

---

## 4. Inter-Process Communication (IPC) Design

1. **Anonymous Pipes (`pipe_ipc.py`)**:
   - Created with `os.pipe()`.
   - File descriptor hygiene: reader closes `write_fd`; writer closes `read_fd`.
   - Closes write descriptor to trigger EOF condition on read descriptor.
2. **Named Pipes (`fifo_ipc.py`)**:
   - Created using `os.mkfifo()` with mode `0666`.
   - Operates through filesystem special node.
   - Synchronizes writer and reader via standard open blocking until both ends attach.
3. **Shared Memory (`shared_memory_ipc.py`)**:
   - Uses `multiprocessing.shared_memory.SharedMemory` to allocate kernel-backed memory.
   - Leverages `multiprocessing.Lock` to ensure mutual exclusion across distinct address spaces.
   - Guaranteed cleanup via `close()` and `unlink()`.
4. **Message Queues (`message_queue_ipc.py`)**:
   - Uses `multiprocessing.Queue` with bounded capacity.
   - Sentinel pattern (`None`) ensures clean consumer thread/process termination.
5. **Signals (`signal_ipc.py`)**:
   - Inter-process notifications via `os.kill(pid, signal.SIGUSR1)`.
   - Custom asynchronous handlers capture events without busy-wait loops.
