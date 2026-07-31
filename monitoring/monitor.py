from .cpu_monitor import CPUMonitor
from .gpu_monitor import GPUMonitor
from .timer import Timer

class SystemMonitor:

    def __init__(self, interval=0.5):

        self.timer = Timer()

        self.cpu_mon = CPUMonitor(interval)
        self.gpu_mon = GPUMonitor(interval)

    def start(self):

        self.timer.start()

        self.cpu_mon.start()
        self.gpu_mon.start()

    def stop(self):

        execution_time = self.timer.stop()

        self.cpu_mon.stop()
        self.gpu_mon.stop()

        self.cpu_mon.join()
        self.gpu_mon.join()

        results = {
            "execution_time_s": execution_time
        }

        results.update(self.cpu_mon.get_results())
        results.update(self.gpu_mon.get_results())

        return results