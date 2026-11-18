from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf


OUTPUT = Path(__file__).resolve().parent / "parte_humberto_redes_neurais.ipynb"


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip() + "\n")


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip() + "\n")


def build_notebook() -> None:
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "pygments_lexer": "ipython3",
        },
    }

    nb["cells"] = [
        md(
            """
            # FIAP — Inteligência Artificial 2026/2
            ## Fase 6 — PBL: O Despertar da Rede Neural (Visão Computacional)
            ### Entrega 2: CNN do Zero & Benchmarking Multidimensional (YOLO vs CNN)

            * **Integrante:** Humberto (RM 570536)
            * **Grupo:** Grupo 29 (Portal FIAP)
            * **Branch de Desenvolvimento:** `parte3-humberto-redes-neurais`
            * **Atividade no Portal:** [assign 658655](https://on.fiap.com.br/mod/assign/view.php?id=658655)

            ---

            ### Cenário FarmTech Solutions
            A **FarmTech Solutions** necessita de um sistema automatizado para triagem fitossanitária e manejo de precisão na lavoura.
            O problema consiste em classificar e detectar a presença de **Cultura Saudável (*Healthy Crop*)** versus **Plantas Daninhas ou Acometidas por Pragas (*Weed / Pest*)**.

            Este notebook implementa a **Rede Neural Convolucional (CNN) treinada do zero** e estabelece a **comparação multidimensional** entre três abordagens:
            1. **YOLO Customizada (v8n - 60 épocas)**
            2. **YOLO Padrão (COCO pré-treinada)**
            3. **CNN do Zero (Humberto)**
            """
        ),
        md(
            """
            ## 1. Configuração do Ambiente e Conexão com Google Drive
            Para reprodução em nuvem no Google Colab, a célula abaixo permite montar o Drive onde os arquivos rotulados foram armazenados. Em execução local, o pipeline utiliza a estrutura modular do repositório.
            """
        ),
        code(
            """
            import os
            from pathlib import Path
            import numpy as np
            import pandas as pd
            import matplotlib.pyplot as plt
            import seaborn as sns

            # Montagem condicional do Google Drive (quando em ambiente Colab)
            try:
                from google.colab import drive
                drive.mount('/content/drive')
                print("[✓] Google Drive montado com sucesso no Google Colab.")
            except ImportError:
                print("[i] Executando em ambiente local. Utilizando dados do repositório.")

            sns.set_theme(style="whitegrid")
            plt.rcParams["figure.dpi"] = 105
            """
        ),
        md(
            """
            ## 2. Estrutura do Dataset e Validação das Proporções Oficiais
            Conforme a especificação oficial da FIAP:
            * **Mínimo por classe:** 40 imagens (32 Treino / 4 Validação / 4 Teste)
            * **Total de imagens:** 80 imagens
            * **Classes:** `healthy_crop` (0) e `weed_pest` (1)
            """
        ),
        code(
            """
            from services.fase6.dataset_loader import load_dataset_splits, CLASSES, SPLIT_COUNTS

            dataset = load_dataset_splits()

            print("=== Resumo do Dataset Carregado ===")
            print(f"Caminho: {dataset.dataset_path}")
            print(f"Treino:    {dataset.x_train.shape} | Labels: {dataset.y_train.shape}")
            print(f"Validação: {dataset.x_val.shape}   | Labels: {dataset.y_val.shape}")
            print(f"Teste:     {dataset.x_test.shape}  | Labels: {dataset.y_test.shape}")
            print(f"Classes mapeadas: {dataset.classes}")
            print(f"Dados demonstrativos ativos? {dataset.is_demo}")

            # Visualização de amostras
            fig, axes = plt.subplots(1, 4, figsize=(12, 3))
            indices = [0, 1, 32, 33]
            for ax, idx in zip(axes, indices):
                img = dataset.x_train[idx]
                label_name = dataset.classes[dataset.y_train[idx]]
                ax.imshow(img)
                ax.set_title(f"Label: {label_name}")
                ax.axis("off")
            plt.tight_layout()
            plt.show()
            """
        ),
        md(
            """
            ## 3. Arquitetura da CNN do Zero
            A arquitetura convolucional desenvolvida para a FarmTech utiliza camadas de extração de características espaciais seguidas de classificação densa:
            * **Bloco 1:** Conv2D (filtros 3x3) + ReLU + MaxPool2D (2x2)
            * **Bloco 2:** Conv2D (filtros 3x3) + ReLU + MaxPool2D (2x2)
            * **Classificador:** Flatten + Dropout (regularização) + Camada Densa com ativação Softmax para 2 classes.
            """
        ),
        code(
            """
            from services.fase6.cnn_model import NumpyCNNClassifier

            cnn = NumpyCNNClassifier(input_shape=(64, 64, 3), num_classes=2, random_state=42)
            print("[✓] Modelo CNN instanciado com sucesso!")
            """
        ),
        md(
            """
            ## 4. Treinamento da CNN e Curvas de Aprendizado
            Treinamento supervisionado com acompanhamento da função de perda (Cross-Entropy) e acurácia por época nos conjuntos de treino e validação.
            """
        ),
        code(
            """
            history = cnn.fit(
                dataset.x_train,
                dataset.y_train,
                dataset.x_val,
                dataset.y_val,
                epochs=25,
                lr=0.015,
            )

            print(f"Tempo total de treinamento: {history.training_time_seconds}s")
            print(f"Acurácia final no treino:    {history.train_acc[-1]:.2%}")
            print(f"Acurácia final na validação: {history.val_acc[-1]:.2%}")

            # Gráficos de Treinamento
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))

            ax1.plot(history.epochs, history.train_loss, label="Loss Treino", color="#2563EB", lw=2)
            ax1.plot(history.epochs, history.val_loss, label="Loss Validação", color="#DC2626", lw=2, linestyle="--")
            ax1.set_title("Curva de Perda (Loss)")
            ax1.set_xlabel("Épocas")
            ax1.set_ylabel("Cross-Entropy Loss")
            ax1.legend()

            ax2.plot(history.epochs, history.train_acc, label="Acc Treino", color="#16A34A", lw=2)
            ax2.plot(history.epochs, history.val_acc, label="Acc Validação", color="#D97706", lw=2, linestyle="--")
            ax2.set_title("Curva de Acurácia")
            ax2.set_xlabel("Épocas")
            ax2.set_ylabel("Acurácia")
            ax2.legend()

            plt.tight_layout()
            plt.show()
            """
        ),
        md(
            """
            ## 5. Avaliação do Modelo no Conjunto de Teste
            Avaliação cega nas imagens de teste nunca vistas pela rede durante o treinamento.
            """
        ),
        code(
            """
            metrics = cnn.evaluate(dataset.x_test, dataset.y_test)

            print("=== Métricas no Conjunto de Teste ===")
            print(f"Acurácia:  {metrics.accuracy:.4f}")
            print(f"Precisão:  {metrics.precision:.4f}")
            print(f"Recall:    {metrics.recall:.4f}")
            print(f"F1-Score:  {metrics.f1:.4f}")
            print(f"Latência média por imagem: {metrics.inference_latency_ms:.2f} ms")

            # Matriz de Confusão
            fig, ax = plt.subplots(figsize=(5.5, 4.5))
            sns.heatmap(
                metrics.confusion_matrix,
                annot=True,
                fmt="d",
                cmap="Blues",
                xticklabels=CLASSES,
                yticklabels=CLASSES,
                ax=ax,
            )
            ax.set_title("Matriz de Confusão — Teste")
            ax.set_xlabel("Predição")
            ax.set_ylabel("Valor Real")
            plt.tight_layout()
            plt.show()
            """
        ),
        md(
            """
            ## 6. Benchmarking Multidimensional (YOLO vs CNN)
            Conforme exigido pelo barema da FIAP, comparamos as 3 abordagens em 4 dimensões:
            1. **Facilidade de uso e integração**
            2. **Precisão / Acurácia / mAP**
            3. **Tempo de treinamento**
            4. **Tempo de inferência (latência)**
            """
        ),
        code(
            """
            from services.fase6.benchmark import get_default_benchmarks, build_comparison_dataframe

            benchmarks = get_default_benchmarks(
                cnn_accuracy=metrics.accuracy,
                cnn_latency_ms=metrics.inference_latency_ms,
            )
            df_comp = build_comparison_dataframe(benchmarks)

            # Exibição da tabela comparativa
            display(df_comp[["abordagem", "tarefa_primaria", "precisao_metrica_principal", "valor_metrica_principal", "latencia_inferencia_ms", "tempo_treinamento_estimado"]])
            """
        ),
        md(
            """
            ### Visualização Gráfica do Benchmark
            """
        ),
        code(
            """
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

            # Gráfico de Precisão
            sns.barplot(
                data=df_comp,
                x="abordagem",
                y="valor_metrica_principal",
                palette=["#2563EB", "#9CA3AF", "#16A34A"],
                ax=ax1,
            )
            ax1.set_title("1. Comparação de Performance (mAP50 / Acurácia)")
            ax1.set_ylabel("Métrica Principal")
            ax1.set_ylim(0, 1.1)
            ax1.tick_params(axis="x", rotation=18)

            # Gráfico de Latência de Inferência (ms)
            sns.barplot(
                data=df_comp,
                x="abordagem",
                y="latencia_inferencia_ms",
                palette=["#F59E0B", "#F59E0B", "#10B981"],
                ax=ax2,
            )
            ax2.set_title("2. Latência de Inferência por Imagem (ms) — Menor é melhor")
            ax2.set_ylabel("Milissegundos (ms)")
            ax2.tick_params(axis="x", rotation=18)

            plt.tight_layout()
            plt.show()
            """
        ),
        md(
            """
            ## 7. Análise Crítica e Conclusões para a FarmTech

            1. **YOLO Customizada (Vencedora para Aplicação Localizada):**
               * *Vantagem:* Fornece a localização espacial exata (bounding box) da praga ou cultura, permitindo atuar com bicos de pulverização seletiva.
               * *Trade-off:* Exige maior esforço de anotação de caixas delimitadoras no Make Sense AI e treino mais longo em GPU.

            2. **YOLO Padrão COCO (Inadequada para o Domínio Agrícola):**
               * *Limitação:* O modelo pré-treinado no COCO identifica apenas objetos gerais do dia a dia (ex: pessoas, garrafas, carros). Sem re-treinamento ou fine-tuning, seu desempenho em fitopatologia e ervas daninhas é quase nulo (mAP < 0.20).

            3. **CNN do Zero (Vencedora para Triagem Rápida e Edge Computing):**
               * *Vantagem:* Arquitetura extremamente leve (~1.4 MB), com menor latência de inferência e processo de rotulação mais simples (apenas colocar imagens em pastas).
               * *Aplicação Ideal:* Dispositivos embarcados em drones ou coletores IoT na lavoura para triagem preliminar de lavouras sadias vs infestadas.
            """
        ),
    ]

    nbf.write(nb, OUTPUT)
    print(f"[OK] Notebook gerado com sucesso em: {OUTPUT}")


if __name__ == "__main__":
    build_notebook()
