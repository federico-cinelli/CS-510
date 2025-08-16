import psutil

def get_processes_info():
    processes = []

    for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
        try:
            # Append process info as a dictionary
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Skip processes that no longer exist or can't be accessed
            continue

    return processes

def display_processes(processes):
    """
    Displays the process information in a table.
    
    Argumentss:
        processes: List of process information.
    """
    
    print(f"{'PID':<10} {'Name':<25} {'Status':<12} {'CPU%':<8} {'Memory%':<10}")
    print("-" * 70)

    # Sort processes by CPU usage in descending order
    for proc in processes:
        print(f"{proc['pid']:<10} {proc['name'][:24]:<25} {proc['status']:<12} {proc['cpu_percent']:<8.1f} {proc['memory_percent']:<10.2f}")

def main():
    print("Retrieving running processes...\n")
    processes = get_processes_info()
    display_processes(processes)

if __name__ == "__main__":
    main()