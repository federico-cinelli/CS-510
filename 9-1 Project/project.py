
"""
Federico Cinelli

Simation of the following:
- Disk allocation (first-fit)
- CPU scheduling (round-robin) + CPU usage tracking
- Memory management (paging + LRU page replacement)
- Concurrency (threads simulating processes)
- Error handling for resource failures and invalid requests

How to run:
    python3 project.py

"""

import threading
import time
import random
import collections
import traceback

# --------------------- Disk Allocation (First-Fit) ---------------------
class Disk:
    def __init__(self, total_blocks=100):
        # Disk represented as list of free/used blocks. None => free, otherwise holds file_id
        self.blocks = [None] * total_blocks
        self.lock = threading.Lock()

    def first_fit_allocate(self, file_id, size):
        with self.lock:
            if size <= 0 or size > len(self.blocks):
                raise ValueError("Invalid allocation size")
            n = len(self.blocks)
            i = 0
            while i <= n - size:
                if all(self.blocks[j] is None for j in range(i, i + size)):
                    for j in range(i, i + size):
                        self.blocks[j] = file_id
                    return i
                i += 1
            raise MemoryError("Disk full or no contiguous region available")

    def free(self, file_id):
        with self.lock:
            freed = 0
            for i in range(len(self.blocks)):
                if self.blocks[i] == file_id:
                    self.blocks[i] = None
                    freed += 1
            return freed

    def utilization(self):
        with self.lock:
            used = sum(1 for b in self.blocks if b is not None)
            return used / len(self.blocks)

# --------------------- Memory Management (Paging + LRU) ---------------------
class MemoryManager:
    def __init__(self, frames=16):
        self.frames = [None] * frames  # each frame stores (process_id, page_number)
        self.frame_lock = threading.Lock()
        self.page_table = {}  # (process_id,page) -> frame_index
        self.access_order = collections.OrderedDict()  # key=(proc,page) -> None, used for LRU

    def access_page(self, process_id, page_number):
        key = (process_id, page_number)
        with self.frame_lock:
            # Page hit
            if key in self.page_table:
                frame_idx = self.page_table[key]
                # update LRU
                self.access_order.pop(key, None)
                self.access_order[key] = None
                return True, frame_idx
            # Page fault -> need to load
            free_idx = None
            for i, f in enumerate(self.frames):
                if f is None:
                    free_idx = i
                    break
            if free_idx is None:
                # need to evict LRU
                evict_key, _ = self.access_order.popitem(last=False)
                evict_frame = self.page_table.pop(evict_key)
                self.frames[evict_frame] = None
                free_idx = evict_frame
            # load page
            self.frames[free_idx] = key
            self.page_table[key] = free_idx
            self.access_order[key] = None
            return False, free_idx

    def current_usage(self):
        with self.frame_lock:
            used = sum(1 for f in self.frames if f is not None)
            return used, len(self.frames)

# --------------------- CPU Scheduling (Round-Robin) ---------------------
class CPUScheduler:
    def __init__(self, time_slice=0.1):
        self.ready_queue = collections.deque()
        self.lock = threading.Lock()
        self.time_slice = time_slice
        self.total_runtime = 0.0
        self.cpu_busy_time = 0.0
        self.start_time = time.time()

    def add_process(self, process):
        with self.lock:
            self.ready_queue.append(process)

    def run_once(self):
        with self.lock:
            if not self.ready_queue:
                return False
            proc = self.ready_queue.popleft()
        # simulate running for time_slice (or less if process finishes)
        run_for = min(self.time_slice, proc.remaining_cpu)
        proc.remaining_cpu -= run_for
        self.cpu_busy_time += run_for
        self.total_runtime += run_for
        # simulate cpu work (non-blocking sleep to yield)
        time.sleep(run_for * 0.01)  # scaled down so simulation runs fast
        if proc.remaining_cpu > 0:
            with self.lock:
                self.ready_queue.append(proc)
        else:
            proc.finished = True
        return True

    def utilization(self):
        # runtime since start
        elapsed = time.time() - self.start_time
        if elapsed <= 0:
            return 0.0
        return self.cpu_busy_time / max(1e-9, elapsed)

# --------------------- Process Representation ---------------------
class SimProcess:
    def __init__(self, pid, cpu_burst, pages_needed=3, disk_blocks=5):
        self.pid = pid
        self.total_cpu = cpu_burst
        self.remaining_cpu = cpu_burst
        self.pages_needed = pages_needed
        self.disk_blocks = disk_blocks
        self.finished = False

    def __repr__(self):
        return f"<P{self.pid} cpu_rem={self.remaining_cpu:.2f} pages={self.pages_needed} disk={self.disk_blocks}>"

# --------------------- System Simulation ---------------------
class SystemSimulator:
    def __init__(self, n_processes=8):
        self.disk = Disk(total_blocks=200)
        self.memory = MemoryManager(frames=32)
        self.cpu = CPUScheduler(time_slice=0.05)
        self.processes = []
        self.threads = []
        self.n_processes = n_processes
        self.log_lock = threading.Lock()

    def log(self, *args):
        with self.log_lock:
            print(*args)

    def create_and_start(self):
        # create processes and threads to simulate concurrent resource requests
        for i in range(self.n_processes):
            cpu_burst = random.uniform(0.1, 0.6)
            pages = random.randint(1, 6)
            disk_blocks = random.randint(1, 20)
            p = SimProcess(pid=i+1, cpu_burst=cpu_burst, pages_needed=pages, disk_blocks=disk_blocks)
            self.processes.append(p)
            t = threading.Thread(target=self.process_lifecycle, args=(p,), daemon=True)
            t.start()
            self.threads.append(t)
            # register with scheduler
            self.cpu.add_process(p)

    def process_lifecycle(self, proc: SimProcess):
        """Each process tries to allocate disk, access memory pages, and run on CPU."""
        try:
            # Disk allocation (may raise)
            try:
                start_idx = self.disk.first_fit_allocate(file_id=f"P{proc.pid}", size=proc.disk_blocks)
                self.log(f"P{proc.pid}: allocated {proc.disk_blocks} disk blocks at {start_idx}")
            except Exception as e:
                self.log(f"P{proc.pid}: disk allocation failed: {e}")
                # still continue but mark disk_blocks as 0 to avoid repeated failures
                proc.disk_blocks = 0

            # Memory accesses: simulate several page accesses
            for access in range(proc.pages_needed * 3):
                page = random.randint(0, proc.pages_needed - 1)
                hit, frame = self.memory.access_page(proc.pid, page)
                if hit:
                    self.log(f"P{proc.pid}: page {page} hit in frame {frame}")
                else:
                    self.log(f"P{proc.pid}: page {page} fault loaded into frame {frame}")
                # random short wait to simulate computation between accesses
                time.sleep(random.uniform(0.001, 0.01))

            # CPU is scheduled separately by the main loop; this thread just monitors until finished
            while not proc.finished:
                time.sleep(0.01)
        except Exception as e:
            # Robust error handling: catch unexpected exceptions in process thread
            self.log(f"P{proc.pid}: Exception in lifecycle: {e}\\n{traceback.format_exc()}")
        finally:
            # cleanup disk allocation if any
            if proc.disk_blocks > 0:
                freed = self.disk.free(f"P{proc.pid}")
                self.log(f"P{proc.pid}: freed {freed} disk blocks on exit")

    def run_scheduler_loop(self, duration=2.0):
        start = time.time()
        while time.time() - start < duration:
            progressed = self.cpu.run_once()
            # If no ready processes, idle briefly
            if not progressed:
                time.sleep(0.01)
        # wait for any threads to finish a bit
        time.sleep(0.2)

    def report(self):
        self.log("=== SYSTEM REPORT ===")
        self.log(f"Disk utilization: {self.disk.utilization()*100:.2f}%")
        used, total = self.memory.current_usage()
        self.log(f"Memory frames used: {used}/{total}")
        self.log(f"CPU utilization (approx): {self.cpu.utilization()*100:.2f}%")
        self.log("Processes status:")
        for p in self.processes:
            self.log(f"  {p} finished={p.finished}")

def main():
    sim = SystemSimulator(n_processes=10)
    sim.create_and_start()
    # run scheduler loop for a few seconds to let processes execute
    sim.run_scheduler_loop(duration=3.0)
    sim.report()

if __name__ == "__main__":
    main()
