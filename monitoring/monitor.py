import threading
import time

import numpy as np
import pandas as pd

from .battery_monitor import BatterySensor
from .cpu_monitor import CPUSensor
from .gpu_monitor import GPUSensor


def _integrate(t, values):
    """Integra uma série de potência (W) no tempo (s) pela regra do trapézio -> Joules."""
    mask = ~np.isnan(values)
    if mask.sum() < 2:
        return float("nan")
    return float(np.trapezoid(values[mask], t[mask]))


class SystemMonitor(threading.Thread):
    """
    Amostra todos os sensores na mesma thread e com o mesmo timestamp.

    A energia é obtida integrando a potência pelos timestamps reais das amostras,
    em vez de assumir que cada amostra dura exatamente `interval` segundos.
    """

    def __init__(self, interval=0.5, gpu_index=0, verbose=False):
        super().__init__(daemon=True)
        self.interval = interval
        self.stopped = threading.Event()

        self.cpu = CPUSensor()
        self.gpu = GPUSensor(gpu_index, verbose=verbose)
        self.battery = BatterySensor()
        self.sensors = [s for s in (self.cpu, self.gpu, self.battery) if s.available]

        self.samples = []

    def _sample(self):
        row = {"t_s": time.perf_counter() - self.t0}
        for sensor in self.sensors:
            try:
                row.update(sensor.read())
            except Exception:
                pass
        self.samples.append(row)

    def start(self):
        self.gpu_energy_start = self.gpu.energy_counter_J() if self.gpu.available else None
        self.t0 = time.perf_counter()
        super().start()

    def run(self):
        while not self.stopped.is_set():
            self._sample()
            self.stopped.wait(self.interval)

    def stop(self):
        """Encerra a coleta e retorna (resumo, série temporal)."""
        self.stopped.set()
        self.join()
        self._sample()  # amostra final exatamente no fim da execução
        gpu_energy_end = self.gpu.energy_counter_J() if self.gpu.available else None

        ts = pd.DataFrame(self.samples)
        t = ts["t_s"].to_numpy()

        results = {"execution_time_s": float(t[-1]), "n_samples": len(ts)}

        for col in ("cpu_%", "proc_cpu_%", "ram_%", "ram_used_GB", "proc_rss_GB", "gpu_%", "vram_%", "vram_used_GB"):
            if col in ts:
                results[f"avg_{col}"] = ts[col].mean()
                results[f"max_{col}"] = ts[col].max()

        # Estimativas (modelo linear) — NÃO são medições
        results["cpu_energy_est_J"] = _integrate(t, ts["cpu_power_est_W"].to_numpy())
        results["ram_energy_est_J"] = _integrate(t, ts["ram_power_est_W"].to_numpy())

        # GPU (medição real, se a placa suportar)
        results["gpu_name"] = self.gpu.gpu_name
        results["gpu_power_supported"] = self.gpu.power_supported
        if self.gpu.power_supported:
            results["avg_gpu_power_W"] = ts["gpu_power_W"].mean()
            results["max_gpu_power_W"] = ts["gpu_power_W"].max()
            if self.gpu_energy_start is not None and gpu_energy_end is not None:
                results["gpu_energy_J"] = gpu_energy_end - self.gpu_energy_start
            else:
                results["gpu_energy_J"] = _integrate(t, ts["gpu_power_W"].to_numpy())

        # Bateria (medição real do sistema inteiro, só vale fora da tomada)
        if self.battery.available:
            on_battery = bool(ts["on_battery"].all())
            results["on_battery"] = on_battery
            results["battery_%_start"] = ts["battery_%"].iloc[0]
            if on_battery:
                results["avg_battery_power_W"] = ts["battery_power_W"].mean()
                results["battery_energy_J"] = _integrate(t, ts["battery_power_W"].to_numpy())
                # Verificação independente (resolução grosseira): queda da capacidade restante
                results["battery_capacity_drop_J"] = 3.6 * float(
                    ts["battery_remaining_mWh"].iloc[0] - ts["battery_remaining_mWh"].iloc[-1]
                )

        return results, ts


def measure_idle(seconds=60, interval=0.5):
    """
    Mede a potência com a máquina parada (baseline). É subtraída depois da energia
    de cada execução para obter a energia atribuível ao modelo (net_energy_J).
    """
    monitor = SystemMonitor(interval)
    monitor.start()
    time.sleep(seconds)
    results, _ = monitor.stop()

    return {
        "idle_battery_power_W": results.get("avg_battery_power_W", float("nan")),
        "idle_gpu_power_W": results.get("avg_gpu_power_W", float("nan")),
        "idle_cpu_%": results.get("avg_cpu_%", float("nan")),
    }
