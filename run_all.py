#!/usr/bin/env python3
"""
Master Assessment Runner
Executes all OS lab modules in sequence, captures terminal evidence,
and runs the automated test suites.
Outputs clean, clearly labeled logs for submission.
"""

import os
import sys
import subprocess
import time

EVIDENCE_DIR = os.path.join(os.path.dirname(__file__), "terminal_evidence")

def ensure_evidence_dir():
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

def run_step(title: str, command: list, output_filename: str):
    print("=" * 80)
    print(f"  RUNNING: {title}")
    print("=" * 80)
    
    start_time = time.time()
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    duration = time.time() - start_time
    
    output_text = result.stdout
    print(output_text)
    
    if output_filename:
        out_path = os.path.join(EVIDENCE_DIR, output_filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"=== TERMINAL EVIDENCE: {title} ===\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Command  : {' '.join(command)}\n")
            f.write(f"Exit Code: {result.returncode} (Completed in {duration:.2f}s)\n\n")
            f.write(output_text)
        print(f"[+] Saved terminal evidence to: {os.path.relpath(out_path)}")
        
    if result.returncode != 0:
        print(f"[!] Warning: Step '{title}' returned non-zero exit code {result.returncode}")
    print()
    return result.returncode == 0

def main():
    ensure_evidence_dir()
    py_exec = sys.executable
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    print("\n" + "#" * 80)
    print("  OPERATING SYSTEMS COMPREHENSIVE ASSESSMENT SUITE")
    print("  Platform: Linux / WSL2 | Python: " + sys.version.split()[0])
    print("#" * 80 + "\n")
    
    steps = [
        ("Module 1: System Calls & /proc Observation",
         [py_exec, "-c", "import src.module1_sys_process.syscalls_demo as s, src.module1_sys_process.proc_observer as p, src.module1_sys_process.zombie_orphan_demo as z; s.main(); p.main(); z.main()"],
         "01_system_calls_and_proc.txt"),
         
        ("Module 2: Process Hierarchy, Threads & Concurrency",
         [py_exec, "-c", "import src.module2_proc_threads.fork_lifecycle as f, src.module2_proc_threads.thread_concurrency as t, src.module2_proc_threads.proc_vs_thread_bench as b; f.main(); t.main(); b.main()"],
         "02_process_and_threads.txt"),
         
        ("Module 3: CPU Scheduling Simulation (FCFS, SJF, SRTF, RR, Priority)",
         [py_exec, "-m", "src.module3_cpu_scheduling.scheduler_runner"],
         "03_cpu_scheduling.txt"),
         
        ("Module 4: Inter-Process Communication (Pipes, FIFOs, Shared Memory, Queues, Signals)",
         [py_exec, "-c", "import src.module4_ipc.pipe_ipc as p, src.module4_ipc.fifo_ipc as f, src.module4_ipc.shared_memory_ipc as shm, src.module4_ipc.message_queue_ipc as q, src.module4_ipc.signal_ipc as s; p.main(); f.main(); shm.main(); q.main(); s.main()"],
         "04_ipc_mechanisms.txt"),
         
        ("Module 5: Automated Test Suite (Valid, Boundary, Invalid, IPC)",
         [py_exec, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
         "05_master_verification.txt"),
    ]
    
    all_passed = True
    for title, cmd, log_file in steps:
        success = run_step(title, cmd, log_file)
        if not success:
            all_passed = False
            
    print("=" * 80)
    if all_passed:
        print("  ALL MODULES & VERIFICATION SUITES COMPLETED SUCCESSFULLY!")
    else:
        print("  SOME TESTS OR MODULES ENCOUNTERED ISSUES. CHECK LOGS ABOVE.")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
