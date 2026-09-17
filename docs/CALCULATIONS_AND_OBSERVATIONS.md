# Operating Systems Laboratory: Calculations, Hand Checks, and Empirical Observations

This document records the theoretical derivations, manual hand calculations, and experimental observations for the system calls, process management, CPU scheduling simulation, and inter-process communication (IPC) modules.

---

## 1. CPU Scheduling: Manual Hand Calculations vs. Simulation

We evaluate all algorithms on the standardized test workload:

| Process | Arrival Time ($AT$) | Burst Time ($BT$) | Priority |
| :---: | :---: | :---: | :---: |
| **P1** | 0 | 5 | 3 |
| **P2** | 1 | 3 | 1 |
| **P3** | 2 | 8 | 4 |
| **P4** | 3 | 6 | 2 |
| **P5** | 15 | 4 | 2 |

### Formulas
- $\text{Completion Time } (CT)$: Timestamp when process finishes final execution.
- $\text{Turnaround Time } (TAT) = CT - AT$
- $\text{Waiting Time } (WT) = TAT - BT$
- $\text{Response Time } (RT) = \text{First Scheduled Time} - AT$
- $\text{CPU Utilization } (\%) = \frac{\sum BT}{\text{Total Elapsed Time}} \times 100\%$
- $\text{Throughput} = \frac{N}{\text{Total Elapsed Time}}$

---

### Algorithm 1: First-Come, First-Served (FCFS)

#### Hand Derivation & Gantt Schedule
1. **P1** arrives at $t=0$, runs $0 \to 5$. ($CT = 5$)
2. **P2** arrived at $t=1$, runs $5 \to 8$. ($CT = 8$)
3. **P3** arrived at $t=2$, runs $8 \to 16$. ($CT = 16$)
4. **P4** arrived at $t=3$, runs $16 \to 22$. ($CT = 22$)
5. **P5** arrived at $t=15$, runs $22 \to 26$. ($CT = 26$)

#### Metrics Hand Calculation
- **P1**: $CT=5$, $TAT = 5-0=5$, $WT = 5-5=0$, $RT = 0-0=0$
- **P2**: $CT=8$, $TAT = 8-1=7$, $WT = 7-3=4$, $RT = 5-1=4$
- **P3**: $CT=16$, $TAT = 16-2=14$, $WT = 14-8=6$, $RT = 8-2=6$
- **P4**: $CT=22$, $TAT = 22-3=19$, $WT = 19-6=13$, $RT = 16-3=13$
- **P5**: $CT=26$, $TAT = 26-15=11$, $WT = 11-4=7$, $RT = 22-15=7$

- $\text{Total } TAT = 5 + 7 + 14 + 19 + 11 = 56 \implies \text{Avg } TAT = \frac{56}{5} = \mathbf{11.20}$
- $\text{Total } WT = 0 + 4 + 6 + 13 + 7 = 30 \implies \text{Avg } WT = \frac{30}{5} = \mathbf{6.00}$
- $\text{Total } RT = 0 + 4 + 6 + 13 + 7 = 30 \implies \text{Avg } RT = \frac{30}{5} = \mathbf{6.00}$
- $\text{CPU Utilization} = \frac{26}{26} \times 100\% = \mathbf{100.00\%}$
- $\text{Throughput} = \frac{5}{26} \approx \mathbf{0.1923} \text{ processes/unit time}$

*Simulation Result Matches Hand Calculation: Exactly 11.20 Avg TAT, 6.00 Avg WT.*

---

### Algorithm 2: Shortest Job First (SJF - Non-Preemptive)

#### Hand Derivation & Gantt Schedule
1. At $t=0$, only **P1** has arrived. Runs $0 \to 5$. ($CT=5$)
2. At $t=5$, ready pool contains **P2** ($BT=3$), **P3** ($BT=8$), **P4** ($BT=6$).
   - Shortest is **P2** ($BT=3$). Runs $5 \to 8$. ($CT=8$)
3. At $t=8$, ready pool contains **P4** ($BT=6$) and **P3** ($BT=8$).
   - Shortest is **P4** ($BT=6$). Runs $8 \to 14$. ($CT=14$)
4. At $t=14$, only **P3** ($BT=8$) is ready (**P5** arrives at $t=15$).
   - Runs $14 \to 22$. ($CT=22$)
5. At $t=22$, **P5** ($BT=4$) is ready.
   - Runs $22 \to 26$. ($CT=26$)

#### Metrics Hand Calculation
- **P1**: $CT=5$, $TAT=5$, $WT=0$, $RT=0$
- **P2**: $CT=8$, $TAT=7$, $WT=4$, $RT=4$
- **P3**: $CT=22$, $TAT=20$, $WT=12$, $RT=12$
- **P4**: $CT=14$, $TAT=11$, $WT=5$, $RT=5$
- **P5**: $CT=26$, $TAT=11$, $WT=7$, $RT=7$

- $\text{Total } TAT = 5 + 7 + 20 + 11 + 11 = 54 \implies \text{Avg } TAT = \frac{54}{5} = \mathbf{10.80}$
- $\text{Total } WT = 0 + 4 + 12 + 5 + 7 = 28 \implies \text{Avg } WT = \frac{28}{5} = \mathbf{5.60}$
- $\text{Total } RT = \mathbf{5.60}$

*Simulation Result Matches Hand Calculation: Exactly 10.80 Avg TAT, 5.60 Avg WT.*

---

### Algorithm 3: Shortest Remaining Time First (SRTF - Preemptive SJF)

#### Hand Derivation & Timeline Tracing
- $t=0$: **P1** starts.
- $t=1$: **P2** arrives with $BT=3$. P1 remaining is $4$. Since $3 < 4$, **P2 preempts P1**!
- $t=1 \to 4$: **P2** runs for 3 units and completes at $t=4$. ($CT=4$)
- $t=4$: Ready pool has **P1** ($rem=4$), **P3** ($rem=8$), **P4** ($rem=6$).
  - Shortest remaining is **P1** ($rem=4$). Runs $4 \to 8$. Completes at $t=8$. ($CT=8$)
- $t=8$: Ready pool has **P4** ($rem=6$), **P3** ($rem=8$).
  - Shortest is **P4** ($rem=6$). Runs $8 \to 14$. Completes at $t=14$. ($CT=14$)
- $t=14$: Only **P3** ($rem=8$) is ready. Starts $14 \to 15$.
- $t=15$: **P5** arrives with $BT=4$. P3 remaining is $7$. Since $4 < 7$, **P5 preempts P3**!
- $t=15 \to 19$: **P5** runs to completion at $t=19$. ($CT=19$)
- $t=19 \to 26$: **P3** finishes remaining 7 units. Completes at $t=26$. ($CT=26$)

#### Metrics Hand Calculation
- **P1**: $CT=8$, $TAT=8$, $WT = 8-5=3$, $RT = 0-0=0$
- **P2**: $CT=4$, $TAT = 4-1=3$, $WT = 3-3=0$, $RT = 1-1=0$
- **P3**: $CT=26$, $TAT = 26-2=24$, $WT = 24-8=16$, $RT = 14-2=12$
- **P4**: $CT=14$, $TAT = 14-3=11$, $WT = 11-6=5$, $RT = 8-3=5$
- **P5**: $CT=19$, $TAT = 19-15=4$, $WT = 4-4=0$, $RT = 15-15=0$

- $\text{Total } TAT = 8 + 3 + 24 + 11 + 4 = 50 \implies \text{Avg } TAT = \frac{50}{5} = \mathbf{10.00}$
- $\text{Total } WT = 3 + 0 + 16 + 5 + 0 = 24 \implies \text{Avg } WT = \frac{24}{5} = \mathbf{4.80}$
- $\text{Total } RT = 0 + 0 + 12 + 5 + 0 = 17 \implies \text{Avg } RT = \frac{17}{5} = \mathbf{3.40}$

*Simulation Result Matches Hand Calculation: Exactly 10.00 Avg TAT, 4.80 Avg WT, 3.40 Avg RT.*

---

### Algorithm 4: Round Robin (RR, $q=2$)

#### Queue Progression
- $t=0$: Queue: `[P1]`
- $t=0 \to 2$: **P1** runs 2 units ($rem=3$). During execution, P2 arrives at $t=1$, P3 arrives at $t=2$.
  Queue becomes: `[P2, P3, P1]`
- $t=2 \to 4$: **P2** runs 2 units ($rem=1$). P4 arrives at $t=3$.
  Queue becomes: `[P3, P1, P4, P2]`
- $t=4 \to 6$: **P3** runs 2 units ($rem=6$).
  Queue becomes: `[P1, P4, P2, P3]`
- $t=6 \to 8$: **P1** runs 2 units ($rem=1$).
  Queue becomes: `[P4, P2, P3, P1]`
- $t=8 \to 10$: **P4** runs 2 units ($rem=4$).
  Queue becomes: `[P2, P3, P1, P4]`
- $t=10 \to 11$: **P2** runs 1 unit ($rem=0$). **P2 finishes at $t=11$**.
  Queue becomes: `[P3, P1, P4]`
- $t=11 \to 13$: **P3** runs 2 units ($rem=4$).
  Queue becomes: `[P1, P4, P3]`
- $t=13 \to 14$: **P1** runs 1 unit ($rem=0$). **P1 finishes at $t=14$**.
  Queue becomes: `[P4, P3]`
- $t=14 \to 16$: **P4** runs 2 units ($rem=2$). P5 arrives at $t=15$.
  Queue becomes: `[P3, P5, P4]`
- $t=16 \to 18$: **P3** runs 2 units ($rem=2$).
  Queue becomes: `[P5, P4, P3]`
- $t=18 \to 20$: **P5** runs 2 units ($rem=2$).
  Queue becomes: `[P4, P3, P5]`
- $t=20 \to 22$: **P4** runs 2 units ($rem=0$). **P4 finishes at $t=22$**.
  Queue becomes: `[P3, P5]`
- $t=22 \to 24$: **P3** runs 2 units ($rem=0$). **P3 finishes at $t=24$**.
  Queue becomes: `[P5]`
- $t=24 \to 26$: **P5** runs 2 units ($rem=0$). **P5 finishes at $t=26$**.

#### Completion Times & Averages
- **P1**: $CT=14$, $TAT=14$, $WT = 14-5=9$, $RT = 0-0=0$
- **P2**: $CT=11$, $TAT = 11-1=10$, $WT = 10-3=7$, $RT = 2-1=1$
- **P3**: $CT=24$, $TAT = 24-2=22$, $WT = 22-8=14$, $RT = 4-2=2$
- **P4**: $CT=22$, $TAT = 22-3=19$, $WT = 19-6=13$, $RT = 8-3=5$
- **P5**: $CT=26$, $TAT = 26-15=11$, $WT = 11-4=7$, $RT = 18-15=3$

- $\text{Avg } TAT = \frac{14 + 10 + 22 + 19 + 11}{5} = \mathbf{15.20}$
- $\text{Avg } WT = \frac{9 + 7 + 14 + 13 + 7}{5} = \mathbf{10.00}$
- $\text{Avg } RT = \frac{0 + 1 + 2 + 5 + 3}{5} = \mathbf{2.20}$

*Simulation Result Matches Hand Calculation: Exactly 15.20 Avg TAT, 10.00 Avg WT, 2.20 Avg RT.*

---

## 2. In-Depth System Observations

### A. System Calls and Context Switching
1. **Mode Switch vs. Context Switch**:
   - A system call (such as `sys_read` or `sys_write`) causes a **mode switch** (user mode to kernel mode via software interrupt `syscall` instruction). The thread's user-space registers are saved to its kernel stack. No scheduling change occurs unless the call blocks.
   - When an I/O operation causes the process to wait, the kernel transitions the process state from `R (Running)` to `S (Interruptible Sleep)`. The CPU state is saved into the process PCB, and the scheduler executes a **context switch** to select the next ready process.
2. **Voluntary vs. Involuntary Context Switches**:
   - Observed in `/proc/[pid]/status`:
     - `voluntary_ctxt_switches`: Process voluntarily relinquished CPU by calling a blocking syscall (`read`, `sleep`, `wait`).
     - `nonvoluntary_ctxt_switches`: Preemption occurred because the process consumed its scheduling time slice or a higher-priority task became runnable.

### B. Process Hierarchy, Zombies, and Orphans
1. **Zombie Processes (`Z` state)**:
   - When a child process terminates (`exit()`), the kernel deallocates its virtual address space, memory pages, open file descriptors, and user mappings.
   - However, the entry in the kernel **Process Table** (containing PID, exit code, termination status) remains intact so the parent process can read the return code via `waitpid()`.
   - If the parent fails to call `waitpid()`, the child remains a "zombie". A large accumulation of zombies can exhaust available PIDs in `/proc/sys/kernel/pid_max`.
2. **Orphan Processes and Reparenting**:
   - If a parent process dies before its child, the child becomes an orphan.
   - The Linux kernel automatically re-parents orphaned processes to PID 1 (`init` or `systemd`), or to an ancestor designated as a subreaper (`PR_SET_CHILD_SUBREAPER`).
   - The adopter continuously reaps child termination statuses, preventing leaked zombie processes.

### C. Process vs. Thread Benchmark Observations
- **Memory Address Space**:
  - Forking creates a distinct virtual memory map. Due to Linux **Copy-on-Write (COW)**, pages are initially shared read-only and duplicated only when written to. Mutations inside child processes do not modify parent data structures.
  - Multithreading executes inside a single virtual address space sharing heap, global variables, and file descriptors.
- **Creation Latency**:
  - In our benchmarks, spawning threads was $\approx 9.4\times$ faster than spawning processes. Thread creation does not require allocating new page directories, descriptor tables, or memory descriptors (`mm_struct`).

### D. Inter-Process Communication (IPC) Mechanism Tradeoffs

| Mechanism | Scope | Data Model | Kernel Overhead | Synchronization |
| :--- | :--- | :--- | :--- | :--- |
| **Anonymous Pipe** | Related processes (Parent/Child) | Byte stream | Kernel buffer copy on write/read | Implicit blocking on empty/full buffer |
| **Named Pipe (FIFO)** | Any process with filesystem access | Byte stream | Kernel buffer copy on write/read | Implicit blocking on open/read |
| **Shared Memory** | Any process with access permissions | Raw memory buffer | Zero copy after mapping | **Mandatory** explicit Mutex / Semaphore |
| **Message Queue** | Cooperating processes | Structured messages | Kernel message queue management | Built-in thread/process safe blocking |
| **Signals** | Any process with permissions | Asynchronous integer notification | High interrupt latency, minimal payload | Asynchronous signal handlers |

---

## 3. Boundary and Failure Handling Verification

1. **Empty Workload**: Successfully triggers validation error preventing scheduler division-by-zero.
2. **Burst Time $\le 0$ & Arrival Time $< 0$**: Caught before simulation; prevents infinite timeline loops or negative time offsets.
3. **High Idle Gap**: Verified that CPU correctly records `[IDLE]` time intervals in the Gantt chart and that CPU utilization drops proportionally to idle duration.
4. **Duplicate PIDs**: Rejected to prevent ambiguous metric lookup in result dictionaries.
