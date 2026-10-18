import torch
from torch.utils.data import DataLoader, TensorDataset
from torchvision import datasets

# (classe torchvision, formato da entrada, média, desvio padrão)
DATASETS = {
    "mnist": (datasets.MNIST, (1, 28, 28), (0.1307,), (0.3081,)),
    "fashion_mnist": (datasets.FashionMNIST, (1, 28, 28), (0.2860,), (0.3530,)),
    "cifar10": (datasets.CIFAR10, (3, 32, 32), (0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
}

_cache = {}


def _load_tensors(name, train, root):
    """
    Carrega o dataset inteiro já normalizado na memória.
    Assim o custo de decodificar imagens (PIL) não entra na medição de cada
    execução, e o consumo medido reflete o modelo, não o carregamento de arquivos.
    """
    key = (name, train)
    if key in _cache:
        return _cache[key]

    cls, shape, mean, std = DATASETS[name]
    ds = cls(root=root, train=train, download=True)

    x = torch.as_tensor(ds.data)
    if x.ndim == 3:            # MNIST: N x H x W
        x = x.unsqueeze(1)
    else:                      # CIFAR: N x H x W x C
        x = x.permute(0, 3, 1, 2)
    x = x.float().div_(255)
    x = (x - torch.tensor(mean).view(1, -1, 1, 1)) / torch.tensor(std).view(1, -1, 1, 1)
    y = torch.as_tensor(ds.targets, dtype=torch.long)

    _cache[key] = (x, y)
    return x, y


def input_shape(name):
    return DATASETS[name][1]


def get_dataloaders(name, batch_size, data_fraction=1.0, seed=0, root="./datasets"):
    """
    Retorna (train_loader, test_loader). `data_fraction` define a fração do
    conjunto de treino usada — é a variável "tamanho do dataset" da proposta.
    """
    x_train, y_train = _load_tensors(name, True, root)
    x_test, y_test = _load_tensors(name, False, root)

    gen = torch.Generator().manual_seed(seed)
    n_train = max(batch_size, int(len(x_train) * data_fraction))
    idx = torch.randperm(len(x_train), generator=gen)[:n_train]

    train_loader = DataLoader(
        TensorDataset(x_train[idx], y_train[idx]),
        batch_size=batch_size,
        shuffle=True,
        generator=torch.Generator().manual_seed(seed),
    )
    test_loader = DataLoader(TensorDataset(x_test, y_test), batch_size=batch_size, shuffle=False)

    return train_loader, test_loader
