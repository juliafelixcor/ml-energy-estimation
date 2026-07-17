import threading
import time
import psutil

class CPUMonitor(threading.Thread):
    def __init__(self, interval=0.5):
        super().__init__()
        self.interval = interval
        self.stopped = threading.Event()
        self.cpu_data = []
        self.ram_data = []

    def run(self):
        psutil.cpu_percent(interval=None)
        
        while not self.stopped.is_set():
            cpu_usage = psutil.cpu_percent(interval=None)
            ram_usage = psutil.virtual_memory().percent 
            
            self.cpu_data.append(cpu_usage)
            self.ram_data.append(ram_usage)
            
            time.sleep(self.interval)

    def stop(self):
        self.stopped.set()
        
    def get_results(self):
        if not self.cpu_data:
            return {"avg_cpu_%": 0, "max_cpu_%": 0, "avg_ram_%": 0}
        return {
            "avg_cpu_%": sum(self.cpu_data) / len(self.cpu_data),
            "max_cpu_%": max(self.cpu_data),
            "avg_ram_%": sum(self.ram_data) / len(self.ram_data)
        }