import torch
import torch.nn as nn
import torch.optim as optim

def run_train(model, train_loader, epochs=5, device="cpu"):
    """
    Executa o loop de treinamento da LeNet-5 com o dataset MNIST real.
    """
    model = model.to(device)
    model.train()
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print(f"-> Iniciando treinamento no dispositivo: {device.upper()}...")
    
    for epoch in range(epochs):
        running_loss = 0.0
        correct = 0
        total = 0
        
        # Iterando sobre o dataset real vindo do train_loader
        for batch_idx, (inputs, targets) in enumerate(train_loader):
            inputs, targets = inputs.to(device), targets.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
            # Cálculo rápido de acurácia para acompanhar o aprendizado
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
            
        acc = 100. * correct / total
        print(f"   Época {epoch+1}/{epochs} finalizada. Loss Médio: {running_loss/(batch_idx+1):.4f} | Acc: {acc:.2f}%")
    
    print("-> Treinamento concluído!")