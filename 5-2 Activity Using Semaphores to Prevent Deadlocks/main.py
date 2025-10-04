"""
Federico Cinelli
CS-510

This program demonstrates how to use a semaphore in Python
to manage process synchronization and prevent deadlocks.
"""

import threading
import time
import random

# Initialize semaphore (limit concurrent access to 3 threads)
semaphore = threading.Semaphore(3)

def worker(task_id):
    print(f"Task {task_id} is waiting to access the resource...")
    
    # Acquire semaphore before entering critical section
    with semaphore:
        print(f"Task {task_id} has acquired access to the resource.")
        
        # Simulate work inside critical section
        time.sleep(random.uniform(1, 3))
        
        print(f"Task {task_id} has released the resource.")

def main():
    threads = []
    num_tasks = 10  # Total number of tasks to run
    
    for i in range(num_tasks):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    print("All tasks have completed successfully.")

if __name__ == "__main__":
    main()
