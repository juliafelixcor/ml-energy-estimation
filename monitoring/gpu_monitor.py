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

        # (timestamp, power)
        self.power_data = []

        self.has_gpu = False

        if PYNVML_AVAILABLE:
            try:
                nvmlInit()
                self.handle = nvmlDeviceGetHandleByIndex(0)
                self.has_gpu = True
                logger.info("GPU NVIDIA detectada.")
            except Exception:
                logger.warning("GPU NVIDIA não detectada.")

        else:
            logger.warning("Biblioteca pynvml não instalada.")

    def run(self):

        if not self.has_gpu:
            return

        logger.info("GPU monitor iniciado.")

        while not self.stopped.is_set():

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

            time.sleep(self.interval)

        logger.info("GPU monitor finalizado.")

    def stop(self):

        self.stopped.set()

        if self.has_gpu:

            try:
                nvmlShutdown()
            except Exception:
                pass

    def get_results(self):

        if not self.has_gpu or len(self.gpu_data) == 0:
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