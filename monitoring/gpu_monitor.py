try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False


class GPUSensor:
    """
    Utilização, VRAM e potência da GPU via NVML.

    Nem toda GPU expõe potência (ex.: GeForce MX110 retorna "Not Supported").
    Quando disponível, o contador acumulado de energia (GPUs Volta ou mais novas,
    como a T4 do Colab/Kaggle) é preferido à integração da potência instantânea.
    """

    name = "gpu"

    def __init__(self, index=0, verbose=True):
        self.available = False
        self.power_supported = False
        self.energy_counter_supported = False
        self.gpu_name = None

        if not PYNVML_AVAILABLE:
            if verbose:
                print("[Aviso] Biblioteca 'pynvml' não instalada. Monitoramento de GPU desativado.")
            return

        try:
            pynvml.nvmlInit()
            self.handle = pynvml.nvmlDeviceGetHandleByIndex(index)
            self.gpu_name = pynvml.nvmlDeviceGetName(self.handle)
            if isinstance(self.gpu_name, bytes):
                self.gpu_name = self.gpu_name.decode()
            self.available = True
        except Exception:
            if verbose:
                print("[Aviso] GPU NVIDIA não detectada. Monitoramento de GPU desativado.")
            return

        try:
            pynvml.nvmlDeviceGetPowerUsage(self.handle)
            self.power_supported = True
        except Exception:
            if verbose:
                print(f"[Aviso] A GPU {self.gpu_name} não suporta leitura de potência.")

        try:
            pynvml.nvmlDeviceGetTotalEnergyConsumption(self.handle)
            self.energy_counter_supported = True
        except Exception:
            pass

    def energy_counter_J(self):
        if not self.energy_counter_supported:
            return None
        return pynvml.nvmlDeviceGetTotalEnergyConsumption(self.handle) / 1000.0  # mJ -> J

    def read(self):
        util = pynvml.nvmlDeviceGetUtilizationRates(self.handle)
        mem = pynvml.nvmlDeviceGetMemoryInfo(self.handle)

        power = float("nan")
        if self.power_supported:
            try:
                power = pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000.0  # mW -> W
            except Exception:
                pass

        return {
            "gpu_%": util.gpu,
            "vram_%": 100.0 * mem.used / mem.total,
            "vram_used_GB": mem.used / (1024 ** 3),
            "gpu_power_W": power,
        }
