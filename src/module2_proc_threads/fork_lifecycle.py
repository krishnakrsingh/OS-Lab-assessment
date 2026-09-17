#!/usr/bin/env python3
"""
Process Creation and Lifecycle Management using os.fork()
Demonstrates:
- Hierarchical process creation (Parent -> Multiple Children)
- Independent execution paths
- Process termination status harvesting using os.waitpid()
- Inspection of WIFEXITED, WEXITSTATUS, and WIFSIGNALED
"""

import os
import sys
import time

def child_task(task_id: int, sleep_time: float, return_code: int):
    """Execution routine for child processes."""
    pid = os.getpid()
    ppid = os.getppid()
    print(f"  [Child Task {task_id}] PID: {pid} | PPID: {ppid} starting work...")
    # Simulate processing work
    time.sleep(sleep_time)
    print(f"  [Child Task {task_id}] PID: {pid} finished. Exiting with code {return_code}.")
    os._exit(return_code)

def run_fork_hierarchy():
    print("=" * 60)
    print("Process Hierarchy & Lifecycle (fork & waitpid)")
    print("=" * 60)
    
    if not hasattr(os, "fork"):
        print("[!] os.fork() is not available on this platform.")
        return
        
    parent_pid = os.getpid()
    print(f"[*] Parent controller PID: {parent_pid}")
    
    # Define tasks: (task_id, sleep_duration_sec, exit_code)
    tasks = [
        (1, 0.2, 10),
        (2, 0.4, 20),
        (3, 0.1, 0),
    ]
    
    active_children = {}
    
    # Fork children
    for task_id, duration, code in tasks:
        try:
            child_pid = os.fork()
            if child_pid == 0:
                # Child branch
                child_task(task_id, duration, code)
            else:
                # Parent branch
                active_children[child_pid] = task_id
                print(f"[*] Parent spawned Child PID {child_pid} for Task #{task_id}")
        except OSError as e:
            print(f"[!] Fork failed for Task #{task_id}: {e}", file=sys.stderr)
            
    print(f"[*] Parent waiting for {len(active_children)} children to terminate...\n")
    
    # Parent reaps all children using waitpid()
    while active_children:
        try:
            # waitpid(-1, 0) waits for any child process
            reaped_pid, status = os.waitpid(-1, 0)
            task_id = active_children.pop(reaped_pid, "Unknown")
            
            if os.WIFEXITED(status):
                exit_code = os.WEXITSTATUS(status)
                print(f"[*] Reaped Child PID {reaped_pid} (Task #{task_id}) -> Normal exit, status={exit_code}")
            elif os.WIFSIGNALED(status):
                term_sig = os.WTERMSIG(status)
                print(f"[!] Child PID {reaped_pid} terminated by signal: {term_sig}")
            else:
                print(f"[*] Child PID {reaped_pid} exited with status: {status}")
        except ChildProcessError:
            break
            
    print("\n[+] All child processes harvested. Process table clean.")

def main():
    print("############################################################")
    print("  LINUX PROCESS CREATION & WAITPID LIFECYCLE")
    print("############################################################\n")
    run_fork_hierarchy()

if __name__ == "__main__":
    main()
