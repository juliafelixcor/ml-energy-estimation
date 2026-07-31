import logging
import os

import pandas as pd
import torch

from datasets.mnist import get_mnist_dataloaders
from models.lenet5 import LeNet5
from monitoring.logging_config import setup_logging
from monitoring.monitor import SystemMonitor
from stages.inference import run_inference
from stages.train import run_train

setup_logging()
logger = logging.getLogger(__name__)

def save_results_to_csv(results, stage):

    filepath = f"output/{stage}_metrics_database.csv"

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    df_new = pd.DataFrame([results])

    if os.path.exists(filepath):
        df_existing = pd.read_csv(filepath)
        df_final = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_final = df_new

    df_final.to_csv(filepath, index=False)

    logger.info(f"Métricas salvas em: {filepath}")

def main():

    device = "cuda" if torch.cuda.is_available() else "cpu"

    logger.info(f"Dispositivo selecionado: {device.upper()}")

    logger.info("Carregando dataset MNIST...")

    train_loader, test_loader = get_mnist_dataloaders(
        batch_size_train=64,
        batch_size_test=64
    )

    model = LeNet5()

    logger.info("Iniciando etapa de treinamento.")

    monitor = SystemMonitor(interval=0.2)

    monitor.start()

    run_train(
        model,
        train_loader,
        epochs=5,
        device=device
    )

    metrics = monitor.stop()

    metrics["model_name"] = "LeNet5_D2L"
    metrics["stage"] = "train"
    metrics["device_used"] = device

    save_results_to_csv(metrics, "train")

    logger.info("Iniciando etapa de inferência.")

    monitor = SystemMonitor(interval=0.2)

    monitor.start()

    run_inference(
        model,
        test_loader,
        device=device
    )

    metrics = monitor.stop()

    metrics["model_name"] = "LeNet5_D2L"
    metrics["stage"] = "inference"
    metrics["device_used"] = device

    save_results_to_csv(metrics, "inference")

    logger.info("Todos os experimentos foram concluídos com sucesso.")

if __name__ == "__main__":
    main()