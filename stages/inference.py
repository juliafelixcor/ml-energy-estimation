import torch

def run_inference(model, test_loader, n_samples=None, device="cpu"):
    """
    Executa apenas a etapa de predição (forward pass) no conjunto de teste.
    `n_samples` define a carga de trabalho: o conjunto de teste é percorrido
    repetidas vezes até processar essa quantidade de amostras (simula um
    serviço atendendo requisições). Retorna a acurácia (%).
    """
    model = model.to(device)
    model.eval()

    if n_samples is None:
        n_samples = len(test_loader.dataset)

    correct = 0
    total = 0

    # torch.no_grad garante que o PyTorch não calculará gradientes (economiza VRAM e CPU/GPU)
    with torch.no_grad():
        while total < n_samples:
            for inputs, targets in test_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs)

                _, predicted = outputs.max(1)
                total += targets.size(0)
                correct += predicted.eq(targets).sum().item()

                if total >= n_samples:
                    break

    return 100. * correct / total
