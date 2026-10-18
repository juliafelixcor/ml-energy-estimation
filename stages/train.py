import torch.nn as nn
import torch.optim as optim

def run_train(model, train_loader, epochs=5, device="cpu", verbose=True):
    """
    Executa o loop de treinamento e retorna a acurácia (%) da última época.
    """
    model = model.to(device)
    model.train()

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    acc = 0.0
    for epoch in range(epochs):
        running_loss = 0.0
        correct = 0
        total = 0

        for batch_idx, (inputs, targets) in enumerate(train_loader):
            inputs, targets = inputs.to(device), targets.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

        acc = 100. * correct / total
        if verbose:
            print(f"   Época {epoch+1}/{epochs} finalizada. Loss Médio: {running_loss/(batch_idx+1):.4f} | Acc: {acc:.2f}%")

    return acc
