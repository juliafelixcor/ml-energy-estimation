<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======
=======
>>>>>>> Stashed changes
import os
import time
import threading
import pandas as pd
from datetime import datetime, timezone

from .timer import Timer
>>>>>>> Stashed changes
from .cpu_monitor import CPUMonitor
from .gpu_monitor import GPUMonitor
from .timer import Timer

class SystemMonitor:
<<<<<<< Updated upstream
<<<<<<< Updated upstream

    def __init__(self, interval=0.5):

        self.timer = Timer()

        self.cpu_mon = CPUMonitor(interval)
        self.gpu_mon = GPUMonitor(interval)
=======
    def __init__(self, interval=0.2, chunk_size=500, stage="experiment", output_dir="output"):
        """
        :param interval: Intervalo em segundos entre cada amostragem.
        :param chunk_size: Número máximo de amostras por arquivo CSV bruto parcial.
        :param stage: Estágio da execução ('train', 'inference', etc.).
        :param output_dir: Diretório para salvar os logs e resumos.
        """
        self.interval = interval
        self.chunk_size = chunk_size
        self.stage = stage
        self.output_dir = output_dir

        self.timer = Timer()
=======
    def __init__(self, interval=0.2, chunk_size=500, stage="experiment", output_dir="output"):
        """
        :param interval: Intervalo em segundos entre cada amostragem.
        :param chunk_size: Número máximo de amostras por arquivo CSV bruto parcial.
        :param stage: Estágio da execução ('train', 'inference', etc.).
        :param output_dir: Diretório para salvar os logs e resumos.
        """
        self.interval = interval
        self.chunk_size = chunk_size
        self.stage = stage
        self.output_dir = output_dir

        self.timer = Timer()
>>>>>>> Stashed changes
        self.cpu_mon = CPUMonitor(interval=interval)
        self.gpu_mon = GPUMonitor(interval=interval)

        self._samples = []
        self._all_samples_summary = []
        self._running = False
        self._collector_thread = None
        self._part_index = 1
        self._total_samples = 0

        os.makedirs(self.output_dir, exist_ok=True)

    def _flush_chunk(self):
        """Salva o lote atual de amostras brutas em um arquivo CSV fragmentado."""
        if not self._samples:
            return

        filename = f"{self.stage}_raw_samples_part_{self._part_index:04d}.csv"
        filepath = os.path.join(self.output_dir, filename)

        df = pd.DataFrame(self._samples)
        df.to_csv(filepath, index=False)

        print(f"[OK] Chunk parcial salvo: {filepath} ({len(self._samples)} registros)")

        self._part_index += 1
        self._samples.clear()

    def _collect_loop(self):
        """Coleta contínua sem agregação com timestamp sincronizado."""
        while self._running:
            now = datetime.now(timezone.utc)
            
            sample = {
                "timestamp_iso": now.isoformat(),
                "timestamp_epoch": time.time(),
                "stage": self.stage
            }

            sample.update(self.cpu_mon.get_sample())
            sample.update(self.gpu_mon.get_sample())

            self._samples.append(sample)
            self._all_samples_summary.append(sample)
            self._total_samples += 1

            if len(self._samples) >= self.chunk_size:
                self._flush_chunk()

            time.sleep(self.interval)

    def _save_summary_database(self, execution_time):
        """Gera o arquivo de resumo consolidado acumulando energia total em Joules (J)."""
        if not self._all_samples_summary:
            return

        df = pd.DataFrame(self._all_samples_summary)

        df["dt"] = df["timestamp_epoch"].diff().fillna(self.interval)
        
        cpu_energy_j = (df["cpu_power_w"] * df["dt"]).sum()
        ram_energy_j = (df["ram_power_w"] * df["dt"]).sum()
        
        gpu_energy_j = None
        if "gpu_power_w" in df.columns and df["gpu_power_w"].notna().any():
            gpu_energy_j = (df["gpu_power_w"].fillna(0) * df["dt"]).sum()

        summary_data = {
            "execution_time_s": execution_time,
            "total_samples": len(df),
            "stage": self.stage,
            "avg_cpu_%": df["cpu_usage_%"].mean(),
            "max_cpu_%": df["cpu_usage_%"].max(),
            "avg_ram_%": df["ram_usage_%"].mean(),
            "avg_ram_used_GB": df["ram_used_gb"].mean(),
            "avg_cpu_power_W": df["cpu_power_w"].mean(),
            "cpu_energy_J": cpu_energy_j,
            "avg_ram_power_W": df["ram_power_w"].mean(),
            "ram_energy_J": ram_energy_j,
            "avg_gpu_%": df["gpu_usage_%"].mean() if "gpu_usage_%" in df.columns else 0.0,
            "max_gpu_%": df["gpu_usage_%"].max() if "gpu_usage_%" in df.columns else 0.0,
            "avg_vram_%": df["vram_usage_%"].mean() if "vram_usage_%" in df.columns else 0.0,
            "avg_gpu_power_W": df["gpu_power_w"].mean() if "gpu_power_w" in df.columns else None,
            "gpu_energy_J": gpu_energy_j
        }

        summary_filepath = os.path.join(self.output_dir, f"{self.stage}_metrics_database.csv")
        df_summary = pd.DataFrame([summary_data])

        if os.path.exists(summary_filepath):
            df_existing = pd.read_csv(summary_filepath)
            df_final = pd.concat([df_existing, df_summary], ignore_index=True)
        else:
            df_final = df_summary

        df_final.to_csv(summary_filepath, index=False)
        print(f"[OK] Resumo consolidado salvo em: {summary_filepath}")
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

    def start(self):

        self.timer.start()

        self.cpu_mon.start()
        self.gpu_mon.start()

        self._running = True
        self._samples = []
        self._all_samples_summary = []
        self._collector_thread = threading.Thread(target=self._collect_loop, daemon=True)
        self._collector_thread.start()

    def stop(self):

        execution_time = self.timer.stop()

<<<<<<< Updated upstream
<<<<<<< Updated upstream
        self.cpu_mon.stop()
        self.gpu_mon.stop()

        self.cpu_mon.join()
        self.gpu_mon.join()

        results = {
            "execution_time_s": execution_time
        }

        results.update(self.cpu_mon.get_results())
        results.update(self.gpu_mon.get_results())

        return results
=======
        self._running = False
        if self._collector_thread:
            self._collector_thread.join()

        self.cpu_mon.stop()
        self.gpu_mon.stop()

=======
        self._running = False
        if self._collector_thread:
            self._collector_thread.join()

        self.cpu_mon.stop()
        self.gpu_mon.stop()

>>>>>>> Stashed changes
        if self._samples:
            self._flush_chunk()

        self._save_summary_database(execution_time)

        print(f"[OK] Coleta de '{self.stage}' finalizada. Total de amostras gravadas: {self._total_samples}")

        return {
            "execution_time_s": execution_time,
            "total_samples": self._total_samples
<<<<<<< Updated upstream
        }
>>>>>>> Stashed changes
=======
        }
>>>>>>> Stashed changes
