# Operating Systems Assessment: System Calls, Processes, CPU Scheduling, and IPC

Comprehensive laboratory implementation demonstrating operating system services, low-level system calls, process management, CPU scheduling algorithms, multithreading synchronization, and inter-process communication (IPC) under Linux (Ubuntu WSL2) using Python 3.

---

## 1. System Environment & Requirements

- **Operating System**: Linux (Ubuntu 24.04 / 26.04 LTS via WSL2)
- **Runtime**: Python 3.10+ (tested on Python 3.14.4)
- **Editor**: Visual Studio Code / Terminal
- **Dependencies**: Minimal (Standard Library preferred; optional dependencies in `requirements.txt`)

To install optional formatting dependencies:
```bash
pip install -r requirements.txt
```

---

## 2. Repository Structure

```
os-assesment/
├── README.md                           # Project documentation and execution instructions
├── requirements.txt                    # Project dependencies
├── run_all.py                          # Master test runner & terminal evidence generator
├── docs/
│   ├── CALCULATIONS_AND_OBSERVATIONS.md # Detailed hand calculations, Gantt proofs, and OS metrics
│   └── ARCHITECTURE.md                 # System architecture and design documentation
├── terminal_evidence/                  # Real terminal output logs captured during test runs
│   ├── 01_system_calls_and_proc.txt
│   ├── 02_process_and_threads.txt
│   ├── 03_cpu_scheduling.txt
│   ├── 04_ipc_mechanisms.txt
│   └── 05_master_verification.txt
├── src/
│   ├── module1_sys_process/
│   │   ├── syscalls_demo.py            # Low-level POSIX file I/O and process ID system calls
│   │   ├── proc_observer.py            # Linux /proc virtual filesystem reader
│   │   └── zombie_orphan_demo.py       # Zombie state verification, waitpid reaping, orphan adoption
│   ├── module2_proc_threads/
│   │   ├── fork_lifecycle.py           # Hierarchical process creation & waitpid status harvesting
│   │   ├── thread_concurrency.py       # Race condition demonstration, Mutex Lock & Semaphore
│   │   └── proc_vs_thread_bench.py     # Memory isolation test & creation overhead benchmark
│   ├── module3_cpu_scheduling/
│   │   ├── process.py                  # PCB dataclass, input validation & deep copy preservation
│   │   ├── algorithms.py               # FCFS, SJF (NP), SRTF (P), Round Robin, Priority (NP & P)
│   │   ├── gantt.py                    # ASCII Gantt chart renderer with idle interval markers
│   │   ├── metrics.py                  # CT, TAT, WT, RT, CPU Utilization %, and Throughput calculator
│   │   └── scheduler_runner.py         # Comparative benchmark ensuring original data preservation
│   └── module4_ipc/
│       ├── pipe_ipc.py                 # Anonymous pipes (unidirectional & full-duplex)
│       ├── fifo_ipc.py                 # Linux named pipe (mkfifo) producer-consumer
│       ├── shared_memory_ipc.py        # Shared memory segment with cross-process Lock
│       ├── message_queue_ipc.py        # Bounded buffer queue with sentinel termination
│       └── signal_ipc.py               # POSIX asynchronous signals (SIGUSR1, os.kill)
└── tests/
    ├── test_scheduling_valid.py        # Correctness tests for standard workloads and invariants
    ├── test_scheduling_boundary.py     # Single process, simultaneous arrivals, BT=1, idle gaps
    ├── test_scheduling_invalid.py      # Negative values, duplicate PIDs, empty inputs, type validation
    └── test_ipc.py                     # Byte fidelity and message ordering tests for IPC channels
```

---

## 3. How to Run

### Run Everything at Once (Master Runner)
To execute all modules in sequence, capture live logs into `terminal_evidence/`, and run the entire verification test suite:
```bash
python3 run_all.py
```

### Run Individual Modules

#### Module 1: System Calls and Linux Process Observation
```bash
python3 src/module1_sys_process/syscalls_demo.py
python3 src/module1_sys_process/proc_observer.py
python3 src/module1_sys_process/zombie_orphan_demo.py
```

#### Module 2: Process Hierarchy, Threads, and Synchronization
```bash
python3 src/module2_proc_threads/fork_lifecycle.py
python3 src/module2_proc_threads/thread_concurrency.py
python3 src/module2_proc_threads/proc_vs_thread_bench.py
```

#### Module 3: CPU Scheduling Simulation
```bash
python3 -m src.module3_cpu_scheduling.scheduler_runner
```

#### Module 4: Inter-Process Communication (IPC)
```bash
python3 src/module4_ipc/pipe_ipc.py
python3 src/module4_ipc/fifo_ipc.py
python3 src/module4_ipc/shared_memory_ipc.py
python3 src/module4_ipc/message_queue_ipc.py
python3 src/module4_ipc/signal_ipc.py
```

#### Module 5: Automated Unit Tests
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

---

## 4. CPU Scheduling Results & Comparison

On the standard benchmark workload (P1 through P5):

```
+----------------------------------------+--------------+--------------+--------------+--------------+--------------+
|               Algorithm                |   Avg TAT    |    Avg WT    |    Avg RT    |  CPU Util %  |  Throughput  |
+----------------------------------------+--------------+--------------+--------------+--------------+--------------+
| First-Come, First-Served (FCFS)        |    11.20     |     6.00     |     6.00     |    100.0%    |    0.192     |
| Shortest Job First (SJF - Non-Preemptive) |    10.80     |     5.60     |     5.60     |    100.0%    |    0.192     |
| Shortest Remaining Time First (SRTF - Preemptive) |    10.00     |     4.80     |     3.40     |    100.0%    |    0.192     |
| Round Robin (RR, Quantum=2)            |    15.20     |    10.00     |     2.20     |    100.0%    |    0.192     |
| Priority (Non-Preemptive)              |    10.80     |     5.60     |     5.60     |    100.0%    |    0.192     |
| Priority (Preemptive)                  |    10.40     |     5.20     |     2.60     |    100.0%    |    0.192     |
+----------------------------------------+--------------+--------------+--------------+--------------+--------------+
```

### Key Takeaways
1. **SRTF achieved the lowest Average Turnaround Time (10.00)** and **lowest Average Waiting Time (4.80)** by always granting the CPU to the process closest to completion.
2. **Round Robin (RR) achieved the lowest Average Response Time (2.20)**, demonstrating its superiority for interactive systems where time-sharing prevents process starvation.
3. **Data Preservation**: Original process objects were cloned independently; input workloads were mathematically proven to be 100% intact after running all comparative algorithms.

---

## 5. Verification & Test Coverage

The test suite in `tests/` covers 21 test cases:
- **Valid Cases**: Verifies invariant conservation laws ($\sum WT + \sum BT = \sum TAT$) and scheduling logic across all algorithms.
- **Boundary Cases**: Workloads with 1 process, all arrivals at $t=0$, burst time of 1, high idle intervals (gap handling), and identical burst/priorities (tie-breakers).
- **Invalid Cases**: Negative burst/arrival times, zero burst, duplicate PIDs, empty inputs, and non-positive Round Robin quanta.
- **IPC Tests**: Byte stream integrity, message queue FIFO ordering, and shared memory struct packing/unpacking.

All 21 tests pass with zero failures:
```
Ran 21 tests in 0.026s
OK
```

---

## 6. License
Academic and educational use.
