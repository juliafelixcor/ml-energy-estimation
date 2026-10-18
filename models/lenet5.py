import torch
import torch.nn as nn

class LeNet5(nn.Module):
    def __init__(self, in_channels=1, img_size=28, num_classes=10):
        super(LeNet5, self).__init__()
        # Conforme a arquitetura descrita na Seção 6.6.1 do D2L (pt.d2l.ai)
        self.features = nn.Sequential(
            # Bloco Convolucional 1
            nn.Conv2d(in_channels, 6, kernel_size=5, padding=2),
            nn.Sigmoid(),
            nn.AvgPool2d(kernel_size=2, stride=2),

            # Bloco Convolucional 2
            nn.Conv2d(6, 16, kernel_size=5),
            nn.Sigmoid(),
            nn.AvgPool2d(kernel_size=2, stride=2),

            # Achatar o tensor para as camadas densas
            nn.Flatten(),
        )

        # 16x5x5 para entradas 28x28 (MNIST); 16x6x6 para 32x32 (CIFAR)
        with torch.no_grad():
            n_flat = self.features(torch.zeros(1, in_channels, img_size, img_size)).shape[1]

        # Bloco Totalmente Conectado (Denso)
        self.classifier = nn.Sequential(
            nn.Linear(n_flat, 120),
            nn.Sigmoid(),
            nn.Linear(120, 84),
            nn.Sigmoid(),
            nn.Linear(84, num_classes)
        )

    def forward(self, x):
        return self.classifier(self.features(x))
