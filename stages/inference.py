import torch

def run_inference(model, test_loader, device="cpu"):
    """
    Executa apenas a etapa de predição (forward pass) no conjunto de testes do MNIST.
    Utiliza dados reais para mapear o consumo de recursos na etapa de produção do modelo.
    """
    model = model.to(device)
    model.eval()
    
    correct = 0
    total = 0
    
    print(f"-> Iniciando inferência no dispositivo: {device.upper()}...")
    
    # torch.no_grad garante que o PyTorch não calculará gradientes (economiza VRAM e CPU/GPU)
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            
            # Cálculo simples de acurácia apenas para fins de monitoramento
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
            
    acc = 100. * correct / total
    print(f"-> Inferência concluída! Acurácia final no teste: {acc:.2f}%")