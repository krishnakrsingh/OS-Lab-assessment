#!/usr/bin/env python3
"""
System Calls Demonstration (POSIX / Linux)
Demonstrates direct low-level kernel interactions via system calls:
- Process identity: getpid(), getppid(), getuid(), getgid()
- File descriptor I/O: open(), write(), read(), lseek(), close()
- Filesystem metadata: stat() / fstat()
- OS/Kernel info: uname()
"""

import os
import sys
import stat
import time

def demo_identity_syscalls():
    print("=" * 60)
    print("1. Process Identity & Credentials System Calls")
    print("=" * 60)
    
    pid = os.getpid()
    ppid = os.getppid()
    print(f"[*] getpid()  -> Current PID   : {pid}")
    print(f"[*] getppid() -> Parent PID    : {ppid}")
    
    # User / Group IDs (available on POSIX/Linux)
    if hasattr(os, "getuid"):
        uid = os.getuid()
        gid = os.getgid()
        euid = os.geteuid()
        egid = os.getegid()
        print(f"[*] getuid()  -> Real UID      : {uid}")
        print(f"[*] getgid()  -> Real GID      : {gid}")
        print(f"[*] geteuid() -> Effective UID : {euid}")
        print(f"[*] getegid() -> Effective GID : {egid}")
    else:
        print("[!] POSIX UID/GID calls not available on this platform.")

    # Kernel information (uname)
    if hasattr(os, "uname"):
        u = os.uname()
        print(f"[*] uname()   -> Sysname : {u.sysname}, Release: {u.release}, Machine: {u.machine}")
    print()

def demo_file_io_syscalls(filepath="syscall_test.tmp"):
    print("=" * 60)
    print("2. File Descriptor I/O System Calls (open, write, read, close)")
    print("=" * 60)
    
    data_to_write = b"Operating Systems Lab: System call execution directly via kernel trap.\n"
    
    try:
        # sys_open: Create file for read/write, truncate if exists, mode 0644
        flags = os.O_CREAT | os.O_RDWR | os.O_TRUNC
        mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
        print(f"[*] open('{filepath}', flags=O_CREAT|O_RDWR|O_TRUNC, mode=0644)")
        fd = os.open(filepath, flags, mode)
        print(f"    -> Obtained file descriptor: {fd}")
        
        # sys_write: Write raw bytes directly to file descriptor
        bytes_written = os.write(fd, data_to_write)
        print(f"[*] write(fd={fd}, len={len(data_to_write)}) -> {bytes_written} bytes written")
        
        # sys_lseek: Reposition read/write file offset back to start (SEEK_SET)
        new_offset = os.lseek(fd, 0, os.SEEK_SET)
        print(f"[*] lseek(fd={fd}, offset=0, whence=SEEK_SET) -> offset now {new_offset}")
        
        # sys_read: Read raw bytes from file descriptor
        buffer = os.read(fd, 1024)
        print(f"[*] read(fd={fd}, count=1024) -> {len(buffer)} bytes read:")
        print(f"    Content: {buffer.decode('utf-8', errors='replace').strip()}")
        
        # sys_fstat: Retrieve file status using open file descriptor
        st = os.fstat(fd)
        print(f"[*] fstat(fd={fd}) -> Inode: {st.st_ino}, Size: {st.st_size} bytes, Mode: {oct(st.st_mode)}")
        
        # sys_close: Release the descriptor
        os.close(fd)
        print(f"[*] close(fd={fd}) -> File descriptor closed successfully")
        
    except OSError as err:
        print(f"[ERROR] System call failed with errno {err.errno}: {err.strerror}", file=sys.stderr)
    finally:
        if os.path.exists(filepath):
            try:
                os.unlink(filepath)  # sys_unlink
                print(f"[*] unlink('{filepath}') -> Temporary file removed")
            except OSError:
                pass
    print()

def demo_stat_syscall(target_path="/etc"):
    print("=" * 60)
    print("3. Filesystem Metadata System Call (stat)")
    print("=" * 60)
    # Check /etc on Linux, fallback to current dir if not present
    path = target_path if os.path.exists(target_path) else "."
    try:
        s = os.stat(path)
        print(f"[*] stat('{path}'):")
        print(f"    - Device ID (st_dev)     : {s.st_dev}")
        print(f"    - Inode number (st_ino)  : {s.st_ino}")
        print(f"    - Protection mode        : {oct(s.st_mode)}")
        print(f"    - Hard link count        : {s.st_nlink}")
        print(f"    - Owner UID / GID        : {s.st_uid} / {s.st_gid}")
        print(f"    - Total size in bytes    : {s.st_size}")
        print(f"    - Last modified time     : {time.ctime(s.st_mtime)}")
    except OSError as err:
        print(f"[ERROR] stat failed on {path}: {err}", file=sys.stderr)
    print()

def main():
    print("############################################################")
    print("  LINUX SYSTEM CALLS EXPERIMENT & OBSERVATION")
    print("############################################################\n")
    demo_identity_syscalls()
    demo_file_io_syscalls()
    demo_stat_syscall()
    print("[+] System call observation completed successfully.")

if __name__ == "__main__":
    main()
