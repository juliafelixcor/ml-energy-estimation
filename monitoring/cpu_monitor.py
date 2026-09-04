import logging
import threading
import time
import psutil

<<<<<<< Updated upstream
<<<<<<< Updated upstream
logger = logging.getLogger(__name__)

class CPUMonitor(threading.Thread):
    def __init__(self, interval=0.5):
=======
class CPUMonitor(threading.Thread):
=======
class CPUMonitor(threading.Thread):
>>>>>>> Stashed changes
    def __init__(self, interval=0.5, total_ram_gb=19.88, ram_power_per_gb=0.372, idle_power=3, max_power=25):
>>>>>>> Stashed changes
        super().__init__()
        self.interval = interval
        self.stopped = threading.Event()

        self.cpu_data = []
        self.ram_data = []
<<<<<<< Updated upstream

    def run(self):
        logger.info("CPU monitor iniciado.")

=======
        self.ram_gb_data = []
        self.cpu_power_data = []
        self.ram_power_data = []

        self.total_ram_gb = total_ram_gb
        self.ram_power_per_gb = ram_power_per_gb
        self.idle_power = idle_power
        self.max_power = max_power

    def get_sample(self):
        """Retorna uma leitura instantânea sem agregação."""
        cpu_usage = psutil.cpu_percent(interval=None)
        ram_usage = psutil.virtual_memory().percent
        ram_used_gb = psutil.virtual_memory().used / (1024 ** 3)

        cpu_fraction = cpu_usage / 100
        cpu_power = self.idle_power + (self.max_power - self.idle_power) * cpu_fraction
        ram_power = ram_used_gb * self.ram_power_per_gb

        return {
            "cpu_usage_%": cpu_usage,
            "ram_usage_%": ram_usage,
            "ram_used_gb": ram_used_gb,
            "cpu_power_w": cpu_power,
            "ram_power_w": ram_power
        }

    def run(self):
<<<<<<< Updated upstream
>>>>>>> Stashed changes
        psutil.cpu_percent(interval=None)
        while not self.stopped.is_set():
<<<<<<< Updated upstream
            cpu_usage = psutil.cpu_percent(interval=None)
            ram_usage = psutil.virtual_memory().percent

            self.cpu_data.append(cpu_usage)
            self.ram_data.append(ram_usage)

            time.sleep(self.interval)

        logger.info("CPU monitor finalizado.")

=======
            sample = self.get_sample()
            self.cpu_data.append(sample["cpu_usage_%"])
            self.ram_data.append(sample["ram_usage_%"])
            self.ram_gb_data.append(sample["ram_used_gb"])
            self.cpu_power_data.append(sample["cpu_power_w"])
            self.ram_power_data.append(sample["ram_power_w"])
            time.sleep(self.interval)

>>>>>>> Stashed changes
=======
        psutil.cpu_percent(interval=None)
        while not self.stopped.is_set():
            sample = self.get_sample()
            self.cpu_data.append(sample["cpu_usage_%"])
            self.ram_data.append(sample["ram_usage_%"])
            self.ram_gb_data.append(sample["ram_used_gb"])
            self.cpu_power_data.append(sample["cpu_power_w"])
            self.ram_power_data.append(sample["ram_power_w"])
            time.sleep(self.interval)

>>>>>>> Stashed changes
    def stop(self):
        self.stopped.set()

    def get_results(self):
        if not self.cpu_data:
<<<<<<< Updated upstream
            return {
                "avg_cpu_%": None,
                "max_cpu_%": None,
                "avg_ram_%": None,
            }

=======
            return {}
        avg_cpu_power = sum(self.cpu_power_data) / len(self.cpu_power_data)
        avg_ram_power = sum(self.ram_power_data) / len(self.ram_power_data)
        execution_time = len(self.cpu_power_data) * self.interval
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        return {
            "avg_cpu_%": sum(self.cpu_data) / len(self.cpu_data),
            "max_cpu_%": max(self.cpu_data),
            "avg_ram_%": sum(self.ram_data) / len(self.ram_data),
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
=======
>>>>>>> Stashed changes
            "avg_ram_used_GB": sum(self.ram_gb_data) / len(self.ram_gb_data),
            "avg_cpu_power_W": avg_cpu_power,
            "cpu_energy_J": avg_cpu_power * execution_time,
            "avg_ram_power_W": avg_ram_power,
            "ram_energy_J": avg_ram_power * execution_time
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        }