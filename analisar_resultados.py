from pathlib import Path

import pandas as pd


ARQUIVOS = {
    "train": Path("output/train_metrics_database.csv"),
    "inference": Path("output/inference_metrics_database.csv"),
}


def resumir_etapa(nome, caminho):
    dados = pd.read_csv(caminho)

    resumo = {
        "etapa": nome,
        "execucoes": len(dados),
        "tempo_medio_s": dados["execution_time_s"].mean(),
        "energia_media_J": dados["total_energy_J"].mean(),
        "energia_minima_J": dados["total_energy_J"].min(),
        "energia_maxima_J": dados["total_energy_J"].max(),
        "energia_desvio_padrao_J": dados["total_energy_J"].std(),
        "tempo_desvio_padrao_s": dados["execution_time_s"].std(),
	"energia_cv_percentual": (
   		 dados["total_energy_J"].std()
  		  / dados["total_energy_J"].mean()
   		 * 100
	),

    }

    return resumo


def main():
    resumos = []

    for nome, caminho in ARQUIVOS.items():
        if not caminho.exists():
            print(f"Arquivo não encontrado: {caminho}")
            continue
        resumos.append(resumir_etapa(nome, caminho))

    if not resumos:
        print("Nenhum arquivo de resultados foi encontrado.")
        return

    tabela = pd.DataFrame(resumos)
    print(tabela.to_string(index=False, float_format=lambda valor: f"{valor:.2f}"))


if __name__ == "__main__":
    main()
