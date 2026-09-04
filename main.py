<<<<<<< Updated upstream
<<<<<<< Updated upstream
import logging
import os

import pandas as pd
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
import torch
from datetime import datetime

from datasets.mnist import get_mnist_dataloaders
from models.lenet5 import LeNet5
from monitoring.logging_config import setup_logging
from monitoring.monitor import SystemMonitor
from stages.inference import run_inference
from stages.train import run_train

<<<<<<< Updated upstream
setup_logging()
logger = logging.getLogger(__name__)

<<<<<<< Updated upstream
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

=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
def main():

    device = "cuda" if torch.cuda.is_available() else "cpu"

    logger.info(f"Dispositivo selecionado: {device.upper()}")

    logger.info("Carregando dataset MNIST...")

    train_loader, test_loader = get_mnist_dataloaders(
        batch_size_train=64,
        batch_size_test=64
    )

    model = LeNet5()
<<<<<<< Updated upstream
<<<<<<< Updated upstream

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
=======
=======
>>>>>>> Stashed changes
    
    timestamp_run = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_directory = f"output/run_{timestamp_run}"
    
    print(f"Resultados desta execução serão salvos em: {output_directory}\n")
    
    print("=== INICIANDO ETAPA: TREINAMENTO ===")
    monitor_train = SystemMonitor(
        interval=0.2, 
        chunk_size=500, 
        stage="train", 
        output_dir=output_directory
    )
    
    monitor_train.start() 
    run_train(model, train_loader, epochs=5, device=device) 
    monitor_train.stop() 
    
    print("-" * 50)
    
    print("\n=== INICIANDO ETAPA: INFERÊNCIA ===")
    monitor_inf = SystemMonitor(
        interval=0.2, 
        chunk_size=500, 
        stage="inference", 
        output_dir=output_directory
    )
    
    monitor_inf.start() 
    run_inference(model, test_loader, device=device)
    monitor_inf.stop() 
    
    print(f"\n=== Todos os experimentos foram concluídos e registrados em: {output_directory} ===")
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

if __name__ == "__main__":
    main()