from pathlib import Path

import pandas as pd


CONFIGURACOES_VALIDAS = {
    "batch_size": [32, 64],
    "epochs": [1, 2],
}


def carregar(caminho):
    dados = pd.read_csv(caminho)
    dados = dados[
        dados["batch_size"].isin(CONFIGURACOES_VALIDAS["batch_size"])
        & dados["epochs"].isin(CONFIGURACOES_VALIDAS["epochs"])
    ].copy()
    return dados


def resumir(dados):
    return (
        dados.groupby(["stage", "batch_size", "epochs"], as_index=False)
        .agg(
            execucoes=("total_energy_J", "count"),
            tempo_medio_s=("execution_time_s", "mean"),
            energia_media_J=("total_energy_J", "mean"),
            energia_desvio_padrao_J=("total_energy_J", "std"),
            acuracia_treino_media=("train_accuracy_percent", "mean"),
            acuracia_inferencia_media=("inference_accuracy_percent", "mean"),
        )
        .sort_values(["stage", "batch_size", "epochs"])
    )


def main():
    arquivos = [
        Path("output/train_metrics_database.csv"),
        Path("output/inference_metrics_database.csv"),
    ]
    dados = pd.concat([carregar(caminho) for caminho in arquivos], ignore_index=True)
    tabela = resumir(dados)
    tabela["acuracia_media"] = tabela["acuracia_treino_media"].combine_first(tabela["acuracia_inferencia_media"])
    tabela = tabela.drop(columns=["acuracia_treino_media", "acuracia_inferencia_media"])
    print(tabela.to_string(index=False, float_format=lambda valor: f"{valor:.2f}"))


if __name__ == "__main__":
    main()
