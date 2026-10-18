import argparse
import os
import time

import torch

from datasets.loaders import get_dataloaders
from experiments.grids import get_grid
from experiments.runner import append_rows, completed_run_ids, run_config, run_id
from monitoring.battery_monitor import BatterySensor
from monitoring.gpu_monitor import GPUSensor
from monitoring.monitor import measure_idle


def parse_args():
    p = argparse.ArgumentParser(description="Coleta de consumo energético em treino e inferência")
    p.add_argument("--grid", default="smoke", choices=["smoke", "cpu", "gpu"],
                   help="smoke = teste rápido; cpu = notebook na bateria; gpu = Colab/Kaggle")
    p.add_argument("--n-configs", type=int, default=48, help="quantas combinações sortear da grade")
    p.add_argument("--repeats", type=int, default=1, help="repetições de cada configuração")
    p.add_argument("--seed", type=int, default=42, help="semente do sorteio das configurações")
    p.add_argument("--device", default=None, help="cpu ou cuda (padrão: automático)")
    p.add_argument("--output", default="output/runs.csv")
    p.add_argument("--interval", type=float, default=0.5, help="intervalo de amostragem (s)")
    p.add_argument("--min-measure-s", type=float, default=60,
                   help="duração mínima de cada janela de medição (s)")
    p.add_argument("--idle-s", type=float, default=60, help="duração da medição em repouso (0 = pular)")
    p.add_argument("--cooldown-s", type=float, default=10, help="pausa entre configurações (s)")
    p.add_argument("--min-battery", type=float, default=25, help="para a coleta abaixo deste % de bateria")
    p.add_argument("--allow-unmeasured", action="store_true",
                   help="roda mesmo sem medição real de energia (só estimativas)")
    return p.parse_args()


def measurement_source(device):
    battery = BatterySensor()
    gpu = GPUSensor()
    if device == "cuda" and gpu.power_supported:
        return "nvml_gpu", battery
    if battery.available and battery.read()["on_battery"]:
        return "battery_system", battery
    return None, battery


def main():
    args = parse_args()
    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Dispositivo selecionado para o PyTorch: {device.upper()}")

    source, battery = measurement_source(device)
    if source is None:
        print("\n[!] Nenhuma medição REAL de energia disponível:")
        if battery.available:
            print("    - O notebook está na tomada. Desconecte o carregador para medir pela bateria.")
        if device == "cpu":
            print("    - Não há GPU com sensor de potência em uso (use Colab/Kaggle para a grade 'gpu').")
        if not args.allow_unmeasured:
            print("    Use --allow-unmeasured para rodar mesmo assim (apenas estimativas).")
            return
    else:
        print(f"Fonte de medição de energia: {source}")

    configs = get_grid(args.grid, args.n_configs, args.seed, args.repeats)
    done = completed_run_ids(args.output)
    pending = [c for c in configs if run_id(c, device) not in done]
    print(f"Configurações: {len(configs)} no total, {len(configs) - len(pending)} já concluídas, {len(pending)} pendentes")
    if not pending:
        return

    print("\n=== Baixando/carregando datasets ===")
    for name in sorted({c["dataset"] for c in pending}):
        get_dataloaders(name, batch_size=64)

    idle = {}
    if args.idle_s > 0:
        print(f"\n=== Medindo consumo em repouso por {args.idle_s:.0f}s (não use o computador) ===")
        idle = measure_idle(args.idle_s, args.interval)
        print("   " + " | ".join(f"{k}={v:.2f}" for k, v in idle.items()))

    for i, cfg in enumerate(pending, 1):
        if source == "battery_system":
            state = battery.read()
            if not state["on_battery"]:
                print("\n[!] Carregador conectado. Coleta interrompida — rode de novo para continuar de onde parou.")
                break
            if state["battery_%"] < args.min_battery:
                print(f"\n[!] Bateria em {state['battery_%']:.0f}%. Coleta interrompida — "
                      "carregue e rode de novo para continuar de onde parou.")
                break

        desc = ", ".join(f"{k}={v}" for k, v in cfg.items())
        print(f"\n[{i}/{len(pending)}] {desc}")
        rows = run_config(cfg, device, idle, args.interval, args.min_measure_s,
                          timeseries_dir=os.path.join(os.path.dirname(args.output) or ".", "timeseries"))
        append_rows(rows, args.output)

        if i < len(pending):
            time.sleep(args.cooldown_s)

    print(f"\n=== Coleta finalizada. Base de dados: {args.output} ===")


if __name__ == "__main__":
    main()
