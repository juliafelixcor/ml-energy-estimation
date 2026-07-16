from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# Baixa o dataset mnist

def get_mnist_dataloaders(batch_size_train=64, batch_size_test=1000):
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    train_dataset = datasets.MNIST(
        root='./datasets', 
        train=True, 
        download=True, 
        transform=transform
    )

    test_dataset = datasets.MNIST(
        root='./datasets', 
        train=False, 
        download=True, 
        transform=transform
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size_train, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size_test, shuffle=False)

    return train_loader, test_loader