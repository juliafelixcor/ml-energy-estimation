import os
import pandas as pd
import torch

# Importações dos seus módulos locais
from models.lenet5 import LeNet5
from datasets.mnist import get_mnist_dataloaders
from monitoring.monitor import SystemMonitor
from stages.train import run_train
from stages.inference import run_inference

def save_results_to_csv(results, stage):
    """
    Salva os resultados obtidos em arquivos CSV separados de acordo com o estágio.
    Cria 'train_metrics_database.csv' ou 'inference_metrics_database.csv' na pasta output.
    """
    # Define o nome do arquivo baseado no estágio (train ou inference)
    filepath = f"output/{stage}_metrics_database.csv"
    
    # Garante que a pasta output existe
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    df_new = pd.DataFrame([results])
    
    if os.path.exists(filepath):
        # Se já existir o arquivo, lê e adiciona a nova linha
        df_existing = pd.read_csv(filepath)
        df_final = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_final = df_new
        
    df_final.to_csv(filepath, index=False)
    print(f"[OK] Métricas salvas com sucesso em: {filepath}")

def main():
    # Detecta se há GPU NVIDIA disponível para o PyTorch usar
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Dispositivo selecionado para o PyTorch: {device.upper()}\n")
    
    # 1. Carregar o Dataset real MNIST (D2L)
    print("=== CARREGANDO DATASET MNIST ===")
    train_loader, test_loader = get_mnist_dataloaders(batch_size_train=64, batch_size_test=64)
    
    # 2. Instanciar o Modelo baseado no D2L
    model = LeNet5()
    
    # --- EXPERIMENTO 1: TREINAMENTO ---
    print("\n=== INICIANDO ETAPA: TREINAMENTO ===")
    monitor = SystemMonitor(interval=0.2) # Medição a cada 200ms
    
    monitor.start() # <-- Começa a gravar CPU/GPU/RAM/VRAM/Potência
    run_train(model, train_loader, epochs=5, device=device) # Executa o treino
    metrics = monitor.stop() # <-- Para o monitoramento e calcula as médias
    
    # Adiciona metadados cruciais para a sua futura análise preditiva
    metrics["model_name"] = "LeNet5_D2L"
    metrics["stage"] = "train"
    metrics["device_used"] = device
    
    # Salva na planilha específica de TREINO
    save_results_to_csv(metrics, stage="train")
    
    print("-" * 50)
    
    # --- EXPERIMENTO 2: INFERÊNCIA ---
    print("\n=== INICIANDO ETAPA: INFERÊNCIA ===")
    monitor_inf = SystemMonitor(interval=0.2)
    
    monitor_inf.start() # <-- Começa a gravar
    run_inference(model, test_loader, device=device) # Executa inferência
    metrics_inf = monitor_inf.stop() # <-- Para e extrai os dados
    
    # Adiciona metadados cruciais
    metrics_inf["model_name"] = "LeNet5_D2L"
    metrics_inf["stage"] = "inference"
    metrics_inf["device_used"] = device
    
    # Salva na planilha específica de INFERÊNCIA
    save_results_to_csv(metrics_inf, stage="inference")
    
    print("\n=== Todos os experimentos foram concluídos e registrados com sucesso! ===")

if __name__ == "__main__":
    main()