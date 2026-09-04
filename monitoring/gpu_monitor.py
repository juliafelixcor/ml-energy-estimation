import logging
import threading
import time

try:
    from pynvml import *

    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

logger = logging.getLogger(__name__)

class GPUMonitor(threading.Thread):

    def __init__(self, interval=0.5):
        super().__init__()

        self.interval = interval
        self.stopped = threading.Event()

        self.gpu_data = []
        self.vram_data = []
<<<<<<< Updated upstream
<<<<<<< Updated upstream

        # (timestamp, power)
        self.power_data = []

=======
        self.power_data = []
>>>>>>> Stashed changes
=======
        self.power_data = []
>>>>>>> Stashed changes
        self.has_gpu = False

        if PYNVML_AVAILABLE:
            try:
                nvmlInit()
                self.handle = nvmlDeviceGetHandleByIndex(0)
                self.has_gpu = True
<<<<<<< Updated upstream
<<<<<<< Updated upstream
                logger.info("GPU NVIDIA detectada.")
=======
=======
>>>>>>> Stashed changes
                try:
                    nvmlDeviceGetPowerUsage(self.handle)
                except NVMLError_NotSupported:
                    self.power_supported = False
                    print("[Aviso] Esta GPU não suporta leitura de potência.")
                except Exception:
                    self.power_supported = False
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
            except Exception:
                logger.warning("GPU NVIDIA não detectada.")

        else:
            logger.warning("Biblioteca pynvml não instalada.")

    def get_sample(self):
        """Retorna uma leitura instantânea dos sensores da GPU."""
        if not self.has_gpu:
            return {
                "gpu_usage_%": 0.0,
                "vram_usage_%": 0.0,
                "gpu_power_w": None
            }

        try:
            gpu_usage = nvmlDeviceGetUtilizationRates(self.handle).gpu
        except Exception:
            gpu_usage = 0.0

        try:
            mem = nvmlDeviceGetMemoryInfo(self.handle)
            vram_usage = (mem.used / mem.total) * 100
        except Exception:
            vram_usage = 0.0

        power = None
        if self.power_supported:
            try:
                power = nvmlDeviceGetPowerUsage(self.handle) / 1000.0
            except Exception:
                power = None

        return {
            "gpu_usage_%": gpu_usage,
            "vram_usage_%": vram_usage,
            "gpu_power_w": power
        }

<<<<<<< Updated upstream
=======
    def get_sample(self):
        """Retorna uma leitura instantânea dos sensores da GPU."""
        if not self.has_gpu:
            return {
                "gpu_usage_%": 0.0,
                "vram_usage_%": 0.0,
                "gpu_power_w": None
            }

        try:
            gpu_usage = nvmlDeviceGetUtilizationRates(self.handle).gpu
        except Exception:
            gpu_usage = 0.0

        try:
            mem = nvmlDeviceGetMemoryInfo(self.handle)
            vram_usage = (mem.used / mem.total) * 100
        except Exception:
            vram_usage = 0.0

        power = None
        if self.power_supported:
            try:
                power = nvmlDeviceGetPowerUsage(self.handle) / 1000.0
            except Exception:
                power = None

        return {
            "gpu_usage_%": gpu_usage,
            "vram_usage_%": vram_usage,
            "gpu_power_w": power
        }

>>>>>>> Stashed changes
    def run(self):
        if not self.has_gpu:
            return

        logger.info("GPU monitor iniciado.")

        while not self.stopped.is_set():
<<<<<<< Updated upstream
<<<<<<< Updated upstream

            try:

                timestamp = time.perf_counter()

                util = nvmlDeviceGetUtilizationRates(self.handle)
                gpu_usage = util.gpu

                info = nvmlDeviceGetMemoryInfo(self.handle)
                vram_usage = (info.used / info.total) * 100

                power = nvmlDeviceGetPowerUsage(self.handle) / 1000.0

                self.gpu_data.append(gpu_usage)
                self.vram_data.append(vram_usage)

                self.power_data.append((timestamp, power))

            except Exception as e:
                logger.exception(e)

=======
=======
>>>>>>> Stashed changes
            sample = self.get_sample()
            self.gpu_data.append(sample["gpu_usage_%"])
            self.vram_data.append(sample["vram_usage_%"])
            if sample["gpu_power_w"] is not None:
                self.power_data.append(sample["gpu_power_w"])
<<<<<<< Updated upstream
>>>>>>> Stashed changes
            time.sleep(self.interval)

        logger.info("GPU monitor finalizado.")

    def stop(self):

        self.stopped.set()
<<<<<<< Updated upstream

        if self.has_gpu:

=======
=======
            time.sleep(self.interval)

    def stop(self):
        self.stopped.set()
>>>>>>> Stashed changes
        if self.has_gpu and PYNVML_AVAILABLE:
>>>>>>> Stashed changes
            try:
                nvmlShutdown()
            except Exception:
                pass

    def get_results(self):
<<<<<<< Updated upstream
<<<<<<< Updated upstream

        if not self.has_gpu or len(self.gpu_data) == 0:
=======
=======
>>>>>>> Stashed changes
        if not self.has_gpu:
>>>>>>> Stashed changes
            return {
                "avg_gpu_%": None,
                "max_gpu_%": None,
                "avg_vram_%": None,
                "avg_power_W": None,
                "gpu_energy_J": None,
            }

        avg_power = (
            sum(power for _, power in self.power_data)
            / len(self.power_data)
        )

        gpu_energy = None

        if len(self.power_data) >= 2:

            gpu_energy = 0.0

            for i in range(len(self.power_data) - 1):

                t1, p1 = self.power_data[i]
                t2, _ = self.power_data[i + 1]

                gpu_energy += p1 * (t2 - t1)

        return {
            "avg_gpu_%": sum(self.gpu_data) / len(self.gpu_data),
            "max_gpu_%": max(self.gpu_data),
            "avg_vram_%": sum(self.vram_data) / len(self.vram_data),
            "avg_power_W": avg_power,
            "gpu_energy_J": gpu_energy,
        }