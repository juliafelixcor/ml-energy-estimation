import threading
import time
import psutil

DEFAULT_RAM_POWER_PER_GB = 0.372
DEFAULT_CPU_IDLE_POWER_W = 3.0
DEFAULT_CPU_MAX_POWER_W = 25.0


class CPUMonitor(threading.Thread):

    def __init__(self, interval=0.5, total_ram_gb=None, ram_power_per_gb=DEFAULT_RAM_POWER_PER_GB, idle_power=DEFAULT_CPU_IDLE_POWER_W, max_power=DEFAULT_CPU_MAX_POWER_W):
        super().__init__()

        self.interval = interval
        self.stopped = threading.Event()

        self.cpu_data = []
        self.ram_data = []
        self.ram_gb_data = []
        self.cpu_power_data = []
        self.ram_power_data = []
        self.timestamps = []

        self.total_ram_gb = total_ram_gb or (psutil.virtual_memory().total / (1024 ** 3))
        self.ram_power_per_gb = ram_power_per_gb

        self.idle_power = idle_power
        self.max_power = max_power


    def run(self):

        psutil.cpu_percent(interval=None)

        while not self.stopped.is_set():

            # Obtém o tempo atual em segundos com alta precisão
            current_time = time.perf_counter()

            # CPU %
            cpu_usage = psutil.cpu_percent(interval=None)

            # RAM %
            ram_usage = psutil.virtual_memory().percent


            # RAM usada em GB
            ram_used_gb = (
                psutil.virtual_memory().used
                /
                (1024 ** 3)
            )


            # Modelo linear CPU Power
            cpu_fraction = cpu_usage / 100

            cpu_power = (
                self.idle_power
                +
                (self.max_power - self.idle_power)
                *
                cpu_fraction
            )


            # Modelo RAM Power
            ram_power = (
                ram_used_gb
                *
                self.ram_power_per_gb
            )


            self.timestamps.append(current_time)
            self.cpu_data.append(cpu_usage)
            self.ram_data.append(ram_usage)

            self.ram_gb_data.append(ram_used_gb)

            self.cpu_power_data.append(cpu_power)
            self.ram_power_data.append(ram_power)

            
            time.sleep(self.interval)



    def stop(self):
        self.stopped.set()

    def calculate_energy(self, power_samples):

        if len(power_samples) < 2:
            return None  # Not enough data to calculate energy
        
        energy = 0.0

        for i in range(1, len(power_samples)):
            dt = self.timestamps[i] - self.timestamps[i - 1]
            energy += power_samples[i - 1] * dt
        
        return energy

    def get_results(self):

        if not self.cpu_data:
            return {}


        avg_cpu_power = (
            sum(self.cpu_power_data)
            /
            len(self.cpu_power_data)
        )


        avg_ram_power = (
            sum(self.ram_power_data)
            /
            len(self.ram_power_data)
        )
        
        cpu_energy = self.calculate_energy(self.cpu_power_data)

        ram_energy = self.calculate_energy(self.ram_power_data)


        return {

            "avg_cpu_%":
                sum(self.cpu_data)
                /
                len(self.cpu_data),

            "max_cpu_%":
                max(self.cpu_data),


            "avg_ram_%":
                sum(self.ram_data)
                /
                len(self.ram_data),


            "avg_ram_used_GB":
                sum(self.ram_gb_data)
                /
                len(self.ram_gb_data),


            "avg_cpu_power_W":
                avg_cpu_power,


            "cpu_energy_J":
                cpu_energy,


            "avg_ram_power_W":
                avg_ram_power,


            "ram_energy_J":
                ram_energy
        }