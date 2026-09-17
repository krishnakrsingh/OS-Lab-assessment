#!/usr/bin/env python3
"""
Message Queue IPC (multiprocessing.Queue)
Demonstrates:
- Message-passing model between cooperating processes
- Discrete structured message delivery (no byte parsing needed)
- Bounded capacity queue behavior (blocking when full)
- Graceful termination signaling via Sentinel (Poison Pill) pattern
"""

import time
from multiprocessing import Process, Queue

def producer(queue: Queue, num_items: int):
    """Produces discrete work items and places them on the message queue."""
    print(f"  [Producer] Commencing production of {num_items} work packages...")
    for i in range(1, num_items + 1):
        item = {
            "job_id": f"JOB_{i:03d}",
            "payload_data": f"Compute matrix chunk {i}",
            "timestamp": time.time()
        }
        # queue.put() will block if queue capacity is reached
        queue.put(item)
        print(f"  [Producer] Enqueued {item['job_id']}")
        time.sleep(0.08)

    # Sentinel poison pill to notify consumer that no more items will follow
    queue.put(None)
    print("  [Producer] Production complete. Enqueued termination sentinel.")

def consumer(queue: Queue):
    """Consumes and processes items from the message queue until sentinel."""
    print("  [Consumer] Listening on message queue...")
    processed_count = 0
    while True:
        # queue.get() blocks until an item is available
        item = queue.get()
        if item is None:
            # Poison pill received
            print("  [Consumer] Received termination sentinel. Exiting read loop.")
            break
        
        processed_count += 1
        print(f"  --> [Consumer] Processed {item['job_id']}: '{item['payload_data']}'")
        time.sleep(0.12)
        
    print(f"  [Consumer] Total messages consumed: {processed_count}")

def run_message_queue_demo():
    print("=" * 60)
    print("Message Queue Bounded Producer-Consumer IPC")
    print("=" * 60)
    
    # Bounded queue with capacity 3
    bounded_queue = Queue(maxsize=3)
    
    p_prod = Process(target=producer, args=(bounded_queue, 5))
    p_cons = Process(target=consumer, args=(bounded_queue,))
    
    p_cons.start()
    p_prod.start()
    
    p_prod.join()
    p_cons.join()
    
    print("\n[+] Message queue communication completed with full message integrity.")

def main():
    print("############################################################")
    print("  MESSAGE QUEUE IPC DEMONSTRATION")
    print("############################################################\n")
    run_message_queue_demo()

if __name__ == "__main__":
    main()
