import os
import psutil


class CPUSensor:
    """
    Utilização de CPU/RAM via psutil.

    A potência de CPU e RAM é ESTIMADA por um modelo linear (não é medida):
        P_cpu = P_idle + (P_max - P_idle) * utilização
        P_ram = GB usados * W/GB
    Por isso as colunas terminam em "_est". Elas servem para comparação com a
    medição real, mas não devem ser usadas como alvo do modelo preditivo.
    """

    name = "cpu"
    available = True

    def __init__(self, idle_power=3, max_power=25, ram_power_per_gb=0.372):
        self.idle_power = idle_power
        self.max_power = max_power
        self.ram_power_per_gb = ram_power_per_gb

        self.process = psutil.Process(os.getpid())
        self.n_cpus = psutil.cpu_count() or 1

        # A primeira chamada de cpu_percent sempre retorna 0; serve só para iniciar a contagem
        psutil.cpu_percent(interval=None)
        self.process.cpu_percent(interval=None)

    def read(self):
        cpu_usage = psutil.cpu_percent(interval=None)
        proc_cpu = self.process.cpu_percent(interval=None) / self.n_cpus
        mem = psutil.virtual_memory()
        ram_used_gb = mem.used / (1024 ** 3)

        return {
            "cpu_%": cpu_usage,
            "proc_cpu_%": proc_cpu,
            "ram_%": mem.percent,
            "ram_used_GB": ram_used_gb,
            "proc_rss_GB": self.process.memory_info().rss / (1024 ** 3),
            "cpu_power_est_W": self.idle_power + (self.max_power - self.idle_power) * cpu_usage / 100,
            "ram_power_est_W": ram_used_gb * self.ram_power_per_gb,
        }
