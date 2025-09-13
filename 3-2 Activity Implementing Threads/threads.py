"""
Federico Cinelli
CS-510 : 3-2 Activity Implementing Threads
"""

"""
This script demonstrates the use of threading in Python by implementing two tasks:
1. Calculating the sum of numbers from 1 to 100.
2. Finding the maximum value in a randomly generated list of numbers.
"""

import threading
import random
import time

# Task one: Calculate the sum of numbers from 1 to 100
def calculate_sum():
    total = sum(range(1, 101))
    print(f"Task One: The sum of numbers from 1 to 100 is: {total}")
    time.sleep(1)  # Simulate computation delay

# Task two: Find the maximum value in a random list
def find_max_value():
    numbers = [random.randint(1, 1000) for _ in range(20)]
    max_val = max(numbers)
    print(f"Task Two: Numbers: {numbers}")
    print(f"Task Two: The maximum value in the list is: {max_val}")
    time.sleep(1)  # Simulate computation delay

def main():
    # Create threads
    thread1 = threading.Thread(target=calculate_sum)
    thread2 = threading.Thread(target=find_max_value)

    # Start threads
    thread1.start()
    thread2.start()

    # Wait for both threads to complete
    thread1.join()
    thread2.join()

    print("Both threads have completed their tasks.")

if __name__ == "__main__":
    main()