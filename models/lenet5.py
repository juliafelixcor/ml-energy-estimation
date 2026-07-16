import torch.nn as nn

class LeNet5(nn.Module):
    def __init__(self, num_classes=10):
        super(LeNet5, self).__init__()
        # Conforme a arquitetura descrita na Seção 6.6.1 do D2L (pt.d2l.ai)
        self.net = nn.Sequential(
            # Bloco Convolucional 1
            nn.Conv2d(1, 6, kernel_size=5, padding=2), # Entrada 1x28x28 (com padding)
            nn.Sigmoid(),
            nn.AvgPool2d(kernel_size=2, stride=2),
            
            # Bloco Convolucional 2
            nn.Conv2d(6, 16, kernel_size=5),
            nn.Sigmoid(),
            nn.AvgPool2d(kernel_size=2, stride=2),
            
            # Achatar o tensor para as camadas densas
            nn.Flatten(),
            
            # Bloco Totalmente Conectado (Denso)
            nn.Linear(16 * 5 * 5, 120),
            nn.Sigmoid(),
            nn.Linear(120, 84),
            nn.Sigmoid(),
            nn.Linear(84, num_classes)
        )

    def forward(self, x):
        return self.net(x)