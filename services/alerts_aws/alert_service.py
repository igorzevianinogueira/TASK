"""Detecta baixa umidade no CSV integrado e, opcionalmente, publica no SNS."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV = PROJECT_ROOT / "dashboard" / "data" / "leituras_sensores.csv"
THRESHOLD_PERCENT = 35.0
REQUIRED_COLUMNS = {"data_hora", "talhao_id", "umidade_solo"}
RECOMMENDED_ACTION = "Aumentar a irrigação nas próximas 24 horas."


def load_records(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        columns = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_COLUMNS - columns)
        if missing:
            raise ValueError(f"CSV sem as colunas obrigatórias: {', '.join(missing)}")
        records = list(reader)
    if not records:
        raise ValueError("O CSV não contém leituras.")
    return records


def make_alert(record: dict[str, str], csv_path: Path) -> dict[str, Any] | None:
    try:
        moisture = float(record["umidade_solo"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Umidade inválida na leitura selecionada.") from exc
    if not math.isfinite(moisture) or not 0 <= moisture <= 100:
        raise ValueError("Umidade deve ser um número entre 0 e 100.")

    if moisture >= THRESHOLD_PERCENT:
        return None

    timestamp = (record.get("data_hora") or "").strip()
    plot_id = (record.get("talhao_id") or "").strip()
    if not timestamp or not plot_id:
        raise ValueError("A leitura precisa informar data_hora e talhao_id.")

    try:
        source = csv_path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        source = csv_path.name

    return {
        "event_type": "farmtech.low_soil_moisture",
        "timestamp": timestamp,
        "talhao_id": plot_id,
        "umidade_solo_pct": round(moisture, 2),
        "limite_umidade_pct": THRESHOLD_PERCENT,
        "acao_recomendada": RECOMMENDED_ACTION,
        "fonte": source,
    }


def select_record(
    records: list[dict[str, str]], row_number: int, first_alert: bool, csv_path: Path
) -> tuple[int, dict[str, str]]:
    if first_alert:
        for index, record in enumerate(records, start=1):
            if make_alert(record, csv_path) is not None:
                return index, record
        raise ValueError(
            f"Nenhuma leitura abaixo do limite de {THRESHOLD_PERCENT:g}% foi encontrada."
        )

    if row_number == 0:
        return len(records), records[-1]
    if not 1 <= row_number <= len(records):
        raise ValueError(f"A linha deve estar entre 1 e {len(records)}; use 0 para a última.")
    return row_number, records[row_number - 1]


def publish_to_sns(message: dict[str, Any]) -> str:
    topic_arn = os.getenv("SNS_TOPIC_ARN", "").strip()
    if not topic_arn:
        raise ValueError("Configure SNS_TOPIC_ARN no ambiente antes do envio.")

    import boto3

    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    client = boto3.client("sns", region_name=region)
    response = client.publish(
        TopicArn=topic_arn,
        Subject="FarmTech: baixa umidade no solo",
        Message=json.dumps(message, ensure_ascii=False),
    )
    return str(response["MessageId"])


def run(args: argparse.Namespace) -> dict[str, Any]:
    csv_path = args.csv.expanduser().resolve()
    records = load_records(csv_path)
    if args.first_alert and args.row != 0:
        raise ValueError("Use --first-alert sozinho ou informe --row, não ambos.")
    selected_row, record = select_record(records, args.row, args.first_alert, csv_path)
    alert = make_alert(record, csv_path)

    result: dict[str, Any] = {
        "alert_triggered": alert is not None,
        "mode": "publish_requested" if args.publish else "dry_run",
        "csv_row": selected_row,
        "reading": {
            "timestamp": record["data_hora"],
            "talhao_id": record["talhao_id"],
            "umidade_solo_pct": float(record["umidade_solo"]),
        },
        "threshold_pct": THRESHOLD_PERCENT,
    }
    if alert is not None:
        result["alert"] = alert
        if args.publish:
            result["sns_message_id"] = publish_to_sns(alert)
            result["mode"] = "published"
    elif args.publish:
        result["mode"] = "not_published_no_alert"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="CSV de leituras")
    parser.add_argument(
        "--row",
        type=int,
        default=0,
        help="linha de dados (1-based); 0 seleciona a última linha (padrão)",
    )
    parser.add_argument(
        "--first-alert",
        action="store_true",
        help="seleciona a primeira leitura do CSV abaixo do limite",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="envia a mensagem ao tópico SNS configurado; por padrão não há envio",
    )
    args = parser.parse_args()

    try:
        result = run(args)
    except Exception as exc:
        print(f"Erro no serviço de alertas: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
