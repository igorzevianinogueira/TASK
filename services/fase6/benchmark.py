from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


@dataclass
class ApproachBenchmark:
    abordagem: str
    tarefa_primaria: str
    facilidade_uso_integracao: str
    precisao_metrica_principal: str
    valor_metrica_principal: float
    tempo_treinamento_estimado: str
    latencia_inferencia_ms: float
    complexidade_anotacao: str
    tamanho_artefato_mb: float
    recomendacao_farmtech: str


def get_default_benchmarks(cnn_accuracy: float = 0.875, cnn_latency_ms: float = 8.5) -> List[ApproachBenchmark]:
    """Retorna os dados consolidados do benchmark das 3 abordagens conforme barema."""
    return [
        ApproachBenchmark(
            abordagem="YOLO Customizada (v8n - 60 épocas)",
            tarefa_primaria="Detecção de Objetos (Bounding Boxes)",
            facilidade_uso_integracao="Média: requer formato YOLO (.txt com x_center, y_center, w, h) gerado via Make Sense AI, mas a API Ultralytics é simples (model.train()).",
            precisao_metrica_principal="mAP50",
            valor_metrica_principal=0.0,
            tempo_treinamento_estimado="Pendente de medição experimental",
            latencia_inferencia_ms=0.0,
            tamanho_artefato_mb=0.0,
            complexidade_anotacao="Alta (anotações de bounding boxes pendentes de validação)",
            recomendacao_farmtech="Recomendado para pulverização localizada, onde a localização espacial (coordenadas x,y) da praga ou cultura é estritamente necessária.",
        ),
        ApproachBenchmark(
            abordagem="YOLO Padrão (COCO pré-treinada)",
            tarefa_primaria="Detecção Geral (80 classes COCO)",
            facilidade_uso_integracao="Alta: zero necessidade de anotação de dados ou treinamento; inferência imediata 'out-of-the-box'.",
            precisao_metrica_principal="mAP50 (Classes Agrícolas Específicas)",
            valor_metrica_principal=0.0,
            tempo_treinamento_estimado="Não aplicável ao uso zero-shot; inferência pendente de medição",
            latencia_inferencia_ms=0.0,
            tamanho_artefato_mb=0.0,
            complexidade_anotacao="Nenhuma para inferência zero-shot; avaliação pendente",
            recomendacao_farmtech="Inadequado para a operação de campo, pois detecta apenas objetos genéricos (pessoa, carro, vaso de planta) sem diferenciar espécies ou fitopatologias.",
        ),
        ApproachBenchmark(
            abordagem="CNN do Zero (Humberto - P3)",
            tarefa_primaria="Classificação de Imagens (Healthy vs. Weed/Pest)",
            facilidade_uso_integracao="Alta para pipeline e dados: separação simples por pastas de classes; código 100% sob controle e sem dependências pesadas de terceiros.",
            precisao_metrica_principal="Acurácia / F1-Score",
            valor_metrica_principal=round(cnn_accuracy, 3),
            tempo_treinamento_estimado="~1.1 min (em GPU) / ~12s (em CPU local para 15-30 épocas)",
            latencia_inferencia_ms=round(cnn_latency_ms, 2),
            complexidade_anotacao="Baixa (basta colocar cada foto na pasta da respectiva classe, sem bounding boxes)",
            tamanho_artefato_mb=1.4,
            recomendacao_farmtech="Excelente custo-benefício para triagem em drones ou câmeras embarcadas de baixo custo (ESP32/Raspberry Pi) onde basta saber se a planta está doente ou saudável.",
        ),
    ]


def build_comparison_dataframe(benchmarks: List[ApproachBenchmark] | None = None) -> pd.DataFrame:
    """Monta a tabela comparativa estruturada em DataFrame."""
    items = benchmarks or get_default_benchmarks()
    rows = [asdict(item) for item in items]
    df = pd.DataFrame(rows)
    return df


def export_benchmark_summary(output_dir: Path | str, benchmarks: List[ApproachBenchmark] | None = None) -> Path:
    """Salva resumo do benchmark em JSON e CSV na pasta de outputs."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    items = benchmarks or get_default_benchmarks()
    df = build_comparison_dataframe(items)

    csv_file = out_path / "benchmark_comparison.csv"
    json_file = out_path / "benchmark_comparison.json"

    df.to_csv(csv_file, index=False, encoding="utf-8")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump([asdict(x) for x in items], f, indent=2, ensure_ascii=False)

    return csv_file
