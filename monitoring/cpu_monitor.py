import threading
import time
import psutil


class CPUMonitor(threading.Thread):

    def __init__(self, interval=0.5, total_ram_gb=19.88, ram_power_per_gb=0.372, idle_power=3, max_power=25):
        super().__init__()

        self.interval = interval
        self.stopped = threading.Event()

        self.cpu_data = []
        self.ram_data = []
        self.ram_gb_data = []
        self.cpu_power_data = []
        self.ram_power_data = []

        self.total_ram_gb = total_ram_gb
        self.ram_power_per_gb = ram_power_per_gb

        self.idle_power = idle_power
        self.max_power = max_power


    def run(self):

        psutil.cpu_percent(interval=None)

        while not self.stopped.is_set():

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


            self.cpu_data.append(cpu_usage)
            self.ram_data.append(ram_usage)

            self.ram_gb_data.append(ram_used_gb)

            self.cpu_power_data.append(cpu_power)
            self.ram_power_data.append(ram_power)


            time.sleep(self.interval)



    def stop(self):
        self.stopped.set()



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


        # Energia CPU
        execution_time = (
            len(self.cpu_power_data)
            *
            self.interval
        )


        cpu_energy = (
            avg_cpu_power
            *
            execution_time
        )


        # Energia RAM
        ram_energy = (
            avg_ram_power
            *
            execution_time
        )


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