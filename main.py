import os
import argparse
import pandas as pd
import torch

from models.lenet5 import LeNet5
from datasets.mnist import get_mnist_dataloaders
from monitoring.monitor import SystemMonitor
from stages.train import run_train
from stages.inference import run_inference
SEED = 42
BATCH_SIZE = 64
EPOCHS = 1
MONITOR_INTERVAL = 0.2

def parse_args():
    parser = argparse.ArgumentParser(
        description="Executa o experimento de estimativa energética."
    )
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--epochs", type=int, default=EPOCHS)
    return parser.parse_args()


def save_results_to_csv(results, stage):
    """
    Cria 'train_metrics_database.csv' ou 'inference_metrics_database.csv' na pasta output.
    """
    filepath = f"output/{stage}_metrics_database.csv"

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    df_new = pd.DataFrame([results])

    if os.path.exists(filepath):
        df_existing = pd.read_csv(filepath)
        df_final = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_final = df_new

    df_final.to_csv(filepath, index=False)
    print(f"[OK] Métricas salvas com sucesso em: {filepath}")

def main():

    args = parse_args()
    torch.manual_seed(SEED)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("=== CARREGANDO DATASET MNIST ===")
    train_loader, test_loader = get_mnist_dataloaders(batch_size_train=args.batch_size, batch_size_test=args.batch_size)

    model = LeNet5()

    monitor = SystemMonitor(interval=MONITOR_INTERVAL) # a cada 200 ms

    monitor.start()
    train_accuracy=run_train(model, train_loader, epochs=args.epochs, device=device)
    metrics = monitor.stop()

    metrics["model_name"] = "LeNet5_D2L"
    metrics["stage"] = "train"
    metrics["device_used"] = device
    metrics["seed"] = SEED
    metrics["batch_size"] = args.batch_size
    metrics["epochs"] = args.epochs
    metrics["monitor_interval_s"] = MONITOR_INTERVAL
    metrics["train_accuracy_percent"] = train_accuracy


    save_results_to_csv(metrics, stage="train")

    print("-" * 50)

    monitor_inf = SystemMonitor(interval=MONITOR_INTERVAL)

    monitor_inf.start()
    inference_accuracy=run_inference(model, test_loader, device=device)
    metrics_inf = monitor_inf.stop()

    metrics_inf["model_name"] = "LeNet5_D2L"
    metrics_inf["stage"] = "inference"
    metrics_inf["device_used"] = device
    metrics_inf["seed"] = SEED
    metrics_inf["batch_size"] = args.batch_size
    metrics_inf["epochs"] = args.epochs
    metrics_inf["monitor_interval_s"] = MONITOR_INTERVAL
    metrics_inf["inference_accuracy_percent"] = inference_accuracy

    save_results_to_csv(metrics_inf, stage="inference")



if __name__ == "__main__":
    main()
