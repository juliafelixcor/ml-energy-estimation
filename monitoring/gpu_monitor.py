import threading
import time

# Tentativa inteligente de importar a biblioteca NVML. 
# Se você não a tiver instalada no seu notebook, o código não vai quebrar!
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
        
        # Só tenta inicializar o NVML se a biblioteca estiver instalada
        if PYNVML_AVAILABLE:
            try:
                nvmlInit()
                self.has_gpu = True
                self.handle = nvmlDeviceGetHandleByIndex(0) # Pega a GPU principal
            except Exception:
                self.has_gpu = False
                print("[Aviso] GPU NVIDIA não detectada fisicamente. Monitoramento de GPU desativado.")
        else:
            print("[Aviso] Biblioteca 'pynvml' não instalada no ambiente. Monitoramento de GPU desativado.")

    def run(self):
        # Se não tem GPU ou biblioteca, a thread fecha imediatamente sem fazer nada
        if not self.has_gpu:
            return
            
        while not self.stopped.is_set():
            try:
                # Uso da GPU (%)
                util = nvmlDeviceGetUtilizationRates(self.handle)
                gpu_usage = util.gpu
                
                # Uso de VRAM (%)
                info = nvmlDeviceGetMemoryInfo(self.handle)
                vram_usage = (info.used / info.total) * 100
                
                # Potência consumida (mW -> Watts)
                power = nvmlDeviceGetPowerUsage(self.handle) / 1000.0
                
                self.gpu_data.append(gpu_usage)
                self.vram_data.append(vram_usage)
                self.power_data.append(power)
            except Exception as e:
                print(f"Erro ao ler dados da GPU: {e}")
                
            time.sleep(self.interval)

    def stop(self):
        self.stopped.set()
        if self.has_gpu and PYNVML_AVAILABLE:
            try:
                nvmlShutdown()
            except Exception:
                pass
        
    def get_results(self):
        # Se rodar no seu notebook sem GPU, ele retorna 0.0 para os dados de GPU de forma segura
        if not self.has_gpu or not self.gpu_data:
            return {
                "avg_gpu_%": 0.0, 
                "max_gpu_%": 0.0, 
                "avg_vram_%": 0.0, 
                "avg_power_W": 0.0, 
                "total_energy_J": 0.0
            }
            
        avg_power = sum(self.power_data) / len(self.power_data)
        total_time = len(self.power_data) * self.interval
        total_energy_joules = avg_power * total_time
        
        return {
            "avg_gpu_%": sum(self.gpu_data) / len(self.gpu_data),
            "max_gpu_%": max(self.gpu_data),
            "avg_vram_%": sum(self.vram_data) / len(self.vram_data),
            "avg_power_W": avg_power,
            "total_energy_J": total_energy_joules
        }