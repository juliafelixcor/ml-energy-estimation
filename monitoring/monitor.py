from .timer import Timer
from .cpu_monitor import CPUMonitor
from .gpu_monitor import GPUMonitor


class SystemMonitor:

    def __init__(self, interval=0.5):
        self.timer = Timer()
        self.cpu_mon = CPUMonitor(interval)
        self.gpu_mon = GPUMonitor(interval)

    def _sum_valid_values(self, *values):
        """
        Soma apenas valores válidos (ignora None).

        Retorna None caso nenhum valor seja válido.
        """

        valid_values = [v for v in values if v is not None]

        if not valid_values:
            return None

        return sum(valid_values)

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

        # Potência média total dos componentes monitorados
        results["avg_power_W"] = self._sum_valid_values(
            results.get("avg_cpu_power_W"),
            results.get("avg_ram_power_W"),
            results.get("avg_gpu_power_W")
        )

        # Energia total dos componentes monitorados
        results["total_energy_J"] = self._sum_valid_values(
            results.get("cpu_energy_J"),
            results.get("ram_energy_J"),
            results.get("gpu_energy_J")
        )

        return results