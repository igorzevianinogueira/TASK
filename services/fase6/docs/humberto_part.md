# Parte do Humberto — Visão Computacional & Redes Neurais (Task 18)

> **Responsável:** Humberto (RM 570536)  
> **Grupo:** Grupo 29 (Fase 6 — 1TIAOA)  
> **Frentes:** Entrega 2 (CNN do Zero & Benchmarking Multidimensional YOLO vs CNN) e Estrutura de Dataset (F1/F2).

---

## 1. O que esta parte entrega

1. **Loader e Validação de Dataset (`dataset_loader.py`):**
   * Estruturação padronizada nas pastas `train/` (64 imagens), `val/` (8 imagens), `test/` (8 imagens).
   * Verificação da proporção estrita da FIAP (32 treino / 4 val / 4 teste por classe; total de 80 imagens).
   * Gerador sintético/demo integrado para garantir que qualquer pessoa do grupo rode os testes e o notebook imediatamente, mesmo antes de baixar as imagens finais do Google Drive.

2. **Arquitetura da CNN do Zero (`cnn_model.py`):**
   * Rede convolucional desenvolvida do zero para classificação binária:
     * **Entrada:** Imagens RGB 64x64x3.
     * **Convoluções:** Blocos Conv2D com ReLU e MaxPooling.
     * **Classificador:** Flatten + Dropout (regularização) + Densa Softmax.
   * Motor determinístico de execução local (permite rodar 100% dos testes em ~1 segundo sem necessidade de GPU ou downloads pesados) e template PyTorch para execução em nuvem no Google Colab.

3. **Benchmarking Multidimensional das 3 Abordagens (`benchmark.py`):**
   * Comparação estruturada cobrindo as 4 dimensões obrigatórias do barema da FIAP:
     1. **Facilidade de uso e integração:** Complexidade de anotação de bounding boxes no Make Sense AI vs rotulação por diretórios.
     2. **Precisão e métricas:** mAP50 (YOLO) vs Acurácia/F1-Score (CNN).
     3. **Tempo de treinamento:** Duração estimada por época em GPU e CPU.
     4. **Tempo de inferência:** Latência média por imagem em milissegundos (ms).

4. **Notebook Compilado (`parte_humberto_redes_neurais.ipynb`):**
   * Compilado via `build_parte_humberto_redes_neurais.py`, contendo introdução ao problema agrícola da FarmTech, visualização das amostras, treinamento com gráficos de perda/acurácia, matriz de confusão e gráficos comparativos de barras.

5. **Testes Unitários Automatizados (`tests/test_cnn_pipeline.py`):**
   * 4 testes cobrindo proporções do dataset, forward pass e probabilidades da CNN, histórico de treinamento e cobertura de todas as dimensões do barema.

---

## 2. Como Reproduzir

```bash
# 1. Executar suíte de testes unitários
python -m unittest discover -s services/fase6/tests

# 2. Gerar ou atualizar o notebook
python services/fase6/build_parte_humberto_redes_neurais.py
```

---

## 3. Instruções de Integração para os Colegas

* **Para quem for fazer o treinamento no Colab (F4/F5):**
  * As imagens rotuladas no Make Sense AI no formato YOLO (.txt) alimentam a YOLO customizada.
  * O mesmo conjunto de imagens organizado nas pastas `healthy_crop` e `weed_pest` é consumido diretamente pela CNN do zero via `load_dataset_splits()`.
* **Para a consolidação no repositório público de entrega (F9):**
  * O notebook `parte_humberto_redes_neurais.ipynb` já segue a estrutura necessária para ser renomeado para `Humberto_rm570536_pbl_fase6.ipynb` ou integrado na narrativa única do grupo.
