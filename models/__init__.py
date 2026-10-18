import torch.nn as nn
from torchvision.models import resnet18

from .lenet5 import LeNet5


class MLP(nn.Module):
    def __init__(self, in_features, hidden=(512, 256), num_classes=10):
        super().__init__()
        layers = [nn.Flatten()]
        for h in hidden:
            layers += [nn.Linear(in_features, h), nn.ReLU()]
            in_features = h
        layers.append(nn.Linear(in_features, num_classes))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


class SmallCNN(nn.Module):
    def __init__(self, in_channels=1, img_size=28, num_classes=10):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_channels, 32, 3, padding=1), nn.ReLU(),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Linear(128 * (img_size // 4) ** 2, 128), nn.ReLU(),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        return self.net(x)


def _resnet18(in_channels, num_classes):
    model = resnet18(num_classes=num_classes)
    if in_channels != 3:
        model.conv1 = nn.Conv2d(in_channels, 64, kernel_size=7, stride=2, padding=3, bias=False)
    return model


MODELS = ["mlp", "lenet5", "cnn_small", "resnet18"]


def build_model(name, in_shape, num_classes=10):
    c, h, w = in_shape
    if name == "mlp":
        return MLP(c * h * w, num_classes=num_classes)
    if name == "lenet5":
        return LeNet5(c, h, num_classes)
    if name == "cnn_small":
        return SmallCNN(c, h, num_classes)
    if name == "resnet18":
        return _resnet18(c, num_classes)
    raise ValueError(f"Modelo desconhecido: {name}. Opções: {MODELS}")
