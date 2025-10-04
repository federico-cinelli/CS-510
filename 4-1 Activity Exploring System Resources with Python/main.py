"""
Federico Cinelli
4-1 Activity Exploring System Resources with Python
This script retrieves and displays information about system resources such as CPU and memory usage.
"""

import psutil   # Library for retrieving system information


def bold(text: str) -> str:
    # Return the given text wrapped in ANSI codes for bold styling.
    # This is a small helper so we can consistently apply bold styling from one place.
    bold_start = "\u001b[1m"
    bold_end = "\u001b[0m"
    return f"{bold_start}{text}{bold_end}"

def display_cpu_info():
    # Get CPU usage percentage (per second interval)
    cpu_usage = psutil.cpu_percent(interval=1)
    # Get number of CPU cores (logical count)
    cpu_count = psutil.cpu_count(logical=True)

    # Print heading in bold using the helper
    print(bold("CPU Information"))
    print(f"CPU Usage: {cpu_usage}%")
    print(f"CPU Count: {cpu_count}\n")


def display_memory_info():
    # Retrieve memory statistics
    memory = psutil.virtual_memory()
    total_memory_gb = memory.total / (1024 ** 3)  # Convert bytes to GB
    used_memory_gb = memory.used / (1024 ** 3)

    print(bold("Memory Information"))
    print(f"Total Memory: {total_memory_gb:.2f} GB")
    print(f"Used Memory: {used_memory_gb:.2f} GB")
    print(f"Memory Usage: {memory.percent}%\n")


def main():
    print(bold("System Information Program\n"))
    display_cpu_info()
    display_memory_info()


# Entry point of the program
if __name__ == "__main__":
    main()