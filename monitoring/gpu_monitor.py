import threading
import time

try:
    from pynvml import *
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

class GPUMonitor(threading.Thread):
    def __init__(self, interval=0.5):
        super().__init__()
        self.interval = interval
        self.stopped = threading.Event()
        self.gpu_data = []
        self.vram_data = []
        self.power_data = [] # Em Watts
        self.has_gpu = False
        self.power_supported = True

        if PYNVML_AVAILABLE:
            try:
                nvmlInit()

                self.handle = nvmlDeviceGetHandleByIndex(0)
                self.has_gpu = True

                # Verifica se a GPU suporta leitura de potência
                try:
                    nvmlDeviceGetPowerUsage(self.handle)
                except NVMLError_NotSupported:
                    self.power_supported = False
                    print("[Aviso] Esta GPU não suporta leitura de potência.")
                except Exception:
                    self.power_supported = False

            except Exception:
                self.has_gpu = False
                print("[Aviso] GPU NVIDIA não detectada fisicamente. Monitoramento de GPU desativado.")
        else:
            print("[Aviso] Biblioteca 'pynvml' não instalada. Monitoramento de GPU desativado.")

    def run(self):

        if not self.has_gpu:
            return

        while not self.stopped.is_set():
            try:
                util = nvmlDeviceGetUtilizationRates(self.handle)
                gpu_usage = util.gpu
            except Exception:
                gpu_usage = 0

            try:
                mem = nvmlDeviceGetMemoryInfo(self.handle)
                vram_usage = (mem.used / mem.total) * 100
            except Exception:
                vram_usage = 0

            power = None

            if self.power_supported:
                try:
                    power = nvmlDeviceGetPowerUsage(self.handle) / 1000.0
                except NVMLError_NotSupported:
                    self.power_supported = False
                    print("[Aviso] Leitura de potência não suportada por esta GPU.")
                except Exception:
                    power = None

            self.gpu_data.append(gpu_usage)
            self.vram_data.append(vram_usage)

            if power is not None:
                self.power_data.append(power)

            time.sleep(self.interval)

    def stop(self):
        self.stopped.set()

        if self.has_gpu and PYNVML_AVAILABLE:
            try:
                nvmlShutdown()
            except Exception:
                pass

    def get_results(self):

        if not self.has_gpu:
            return {
                "avg_gpu_%": 0.0,
                "max_gpu_%": 0.0,
                "avg_vram_%": 0.0,
                "avg_power_W": None,
                "gpu_energy_J": None,
                "power_supported": False,
            }

        avg_gpu = sum(self.gpu_data) / len(self.gpu_data) if self.gpu_data else 0.0
        max_gpu = max(self.gpu_data) if self.gpu_data else 0.0
        avg_vram = sum(self.vram_data) / len(self.vram_data) if self.vram_data else 0.0

        if self.power_data:
            avg_power = sum(self.power_data) / len(self.power_data)
            total_time = len(self.power_data) * self.interval
            gpu_energy = avg_power * total_time
        else:
            avg_power = None
            gpu_energy = None

        return {
            "avg_gpu_%": avg_gpu,
            "max_gpu_%": max_gpu,
            "avg_vram_%": avg_vram,
            "avg_power_W": avg_power,
            "gpu_energy_J": gpu_energy,
            "power_supported": self.power_supported,
        }