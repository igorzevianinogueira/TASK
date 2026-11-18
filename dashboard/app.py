"""Dashboard integrada FarmTech — Fase 7, Capítulo 1."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_ROOT = Path(__file__).resolve().parent
SERVICES_ROOT = PROJECT_ROOT / "services"
FASE1_ROOT = SERVICES_ROOT / "fase1"
FASE1_MAIN = FASE1_ROOT / "main.py"
FASE2_ROOT = SERVICES_ROOT / "fase2" / "opcional1_openweather"
FASE2_CLIMA = FASE2_ROOT / "clima.py"
FASE3_ROOT = SERVICES_ROOT / "fase3"
FASE3_APP = FASE3_ROOT / "dashboard" / "app.py"
FASE6_ROOT = SERVICES_ROOT / "fase6"
FASE6_NOTEBOOK_BUILDER = FASE6_ROOT / "build_parte_humberto_redes_neurais.py"
FASE6_DEMO = FASE6_ROOT / "run_demo.py"
ALERT_SCRIPT = SERVICES_ROOT / "alerts_aws" / "alert_service.py"

sys.path.insert(0, str(DASHBOARD_ROOT))
from ml.predict import FEATURES, MODEL_PATH, predict_yield  # noqa: E402

DATA_CSV = DASHBOARD_ROOT / "data" / "leituras_sensores.csv"
METRICS_JSON = DASHBOARD_ROOT / "models" / "regression_metrics.json"
PIPELINE_SCRIPT = DASHBOARD_ROOT / "scripts" / "run_pipeline.py"


@st.cache_data
def load_data() -> pd.DataFrame:
    if not DATA_CSV.is_file():
        raise FileNotFoundError("Dataset da dashboard não encontrado.")
    return pd.read_csv(DATA_CSV)


def _process_options(cwd: Path) -> dict:
    options = {"cwd": str(cwd)}
    if os.name == "nt":
        options["creationflags"] = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
    else:
        options["start_new_session"] = True
    return options


def _launch(command: list[str], cwd: Path) -> None:
    subprocess.Popen(command, **_process_options(cwd))


def launch_fase1() -> None:
    if not FASE1_MAIN.is_file():
        raise FileNotFoundError(f"Entrada da Fase 1 não encontrada: {FASE1_MAIN}")
    _launch([sys.executable, str(FASE1_MAIN)], FASE1_ROOT)


def launch_fase3() -> None:
    if not FASE3_APP.is_file():
        raise FileNotFoundError(f"Dashboard da Fase 3 não encontrada: {FASE3_APP}")
    _launch(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(FASE3_APP),
            "--server.port",
            "8502",
            "--server.headless",
            "true",
        ],
        FASE3_ROOT,
    )


def run_local_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)


def main() -> None:
    st.set_page_config(page_title="FarmTech integrada — Fase 7", layout="wide")
    st.title("FarmTech — Sistema Integrado")
    st.caption("Dashboard de entrada para os módulos disponíveis das Fases 1, 2, 3 e 6.")

    with st.sidebar:
        st.header("Serviços integrados")

        if st.button("Iniciar menu da Fase 1", use_container_width=True):
            try:
                launch_fase1()
                st.success("Menu da Fase 1 aberto em outro terminal.")
            except OSError as exc:
                st.error(f"Não foi possível iniciar a Fase 1: {exc}")

        if st.button("Abrir dashboard da Fase 3", use_container_width=True):
            try:
                launch_fase3()
                st.success("Dashboard da Fase 3 iniciada em http://localhost:8502.")
            except OSError as exc:
                st.error(f"Não foi possível iniciar a Fase 3: {exc}")

        st.divider()
        st.subheader("Fase 2 — comando para o Wokwi")
        chuva = st.selectbox(
            "Cenário de chuva",
            options=[("Previsão de chuva", "1"), ("Sem chuva", "0")],
            format_func=lambda item: item[0],
        )
        if st.button("Gerar comando CHUVA", use_container_width=True):
            try:
                result = run_local_command(
                    [sys.executable, str(FASE2_CLIMA), "--simular-chuva", chuva[1]],
                    FASE2_ROOT,
                )
                if result.returncode == 0:
                    st.code(result.stdout.strip(), language="text")
                    st.caption("Copie o comando para o Serial Monitor do Wokwi.")
                else:
                    st.error(result.stderr.strip() or "Falha ao gerar comando da Fase 2.")
            except OSError as exc:
                st.error(f"Não foi possível gerar o comando da Fase 2: {exc}")

        st.divider()
        st.subheader("Alertas por e-mail — AWS SNS")
        alert_source = st.selectbox(
            "Leitura para verificar",
            options=["Primeira leitura abaixo de 35%", "Última leitura do CSV"],
        )
        alert_args = [sys.executable, str(ALERT_SCRIPT)]
        if alert_source == "Primeira leitura abaixo de 35%":
            alert_args.append("--first-alert")
        else:
            alert_args.extend(["--row", "0"])

        if st.button("Visualizar alerta sem enviar", use_container_width=True):
            result = run_local_command(alert_args, PROJECT_ROOT)
            if result.returncode == 0:
                st.json(json.loads(result.stdout))
            else:
                st.error(result.stderr.strip() or "Falha ao verificar a leitura.")

        st.caption(
            "O envio real publica no tópico SNS e alcança os inscritos confirmados. "
            "Configure AWS_REGION, SNS_TOPIC_ARN e credenciais AWS localmente."
        )
        confirm_alert_send = st.checkbox(
            "Confirmo o envio real para os inscritos do tópico SNS.",
            key="confirm_alert_send",
        )
        if st.button(
            "Enviar alerta pelo SNS",
            use_container_width=True,
            disabled=not confirm_alert_send,
        ):
            result = run_local_command(alert_args + ["--publish"], PROJECT_ROOT)
            if result.returncode == 0:
                try:
                    published = json.loads(result.stdout)
                except json.JSONDecodeError:
                    st.code(result.stdout, language="text")
                else:
                    st.json(published)
                    if published.get("mode") == "published":
                        st.success("Alerta enviado; confira o MessageId e os e-mails inscritos.")
                    elif not published.get("alert_triggered"):
                        st.info("A leitura selecionada não atingiu o limite; nada foi enviado.")
            else:
                st.error(result.stderr.strip() or "Falha ao publicar o alerta no SNS.")

        st.divider()
        st.subheader("Fase 6 — notebook demonstrativo")
        if st.button("Executar demo de classificação", use_container_width=True):
            try:
                result = run_local_command([sys.executable, str(FASE6_DEMO)], PROJECT_ROOT)
                if result.returncode == 0:
                    try:
                        st.json(json.loads(result.stdout))
                    except json.JSONDecodeError:
                        st.code(result.stdout, language="text")
                else:
                    st.error(result.stderr.strip() or "Falha na demo de classificação.")
            except OSError as exc:
                st.error(f"Não foi possível executar a demo da Fase 6: {exc}")
        if st.button("Atualizar notebook da Fase 6", use_container_width=True):
            try:
                result = run_local_command(
                    [sys.executable, str(FASE6_NOTEBOOK_BUILDER)], FASE6_ROOT
                )
                if result.returncode == 0:
                    st.success(result.stdout.strip() or "Notebook atualizado.")
                else:
                    st.error(result.stderr.strip() or "Falha ao gerar notebook.")
            except OSError as exc:
                st.error(f"Não foi possível atualizar o notebook: {exc}")
        st.caption(
            "A demo treina e avalia nas imagens sintéticas locais. Ela não representa inferência "
            "em imagens reais da lavoura."
        )

        st.divider()
        if st.button("Preparar modelo da dashboard", use_container_width=True):
            with st.spinner("Gerando dados e treinando o modelo da dashboard…"):
                result = run_local_command(
                    [sys.executable, str(PIPELINE_SCRIPT)], DASHBOARD_ROOT
                )
            if result.returncode == 0:
                st.success("Pipeline da dashboard concluído.")
                st.rerun()
            else:
                st.error(result.stderr.strip() or "Falha no pipeline da dashboard.")

    try:
        df = load_data()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    if MODEL_PATH.is_file() and METRICS_JSON.is_file():
        metrics = json.loads(METRICS_JSON.read_text(encoding="utf-8"))
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("MAE", metrics.get("mae", "-"))
        c2.metric("RMSE", metrics.get("rmse", "-"))
        c3.metric("R²", metrics.get("r2", "-"))
        c4.metric("Leituras", len(df))
    else:
        st.info("Use ‘Preparar modelo da dashboard’ na barra lateral para ativar a previsão da Fase 4.")

    tab_prev, tab_corr, tab_raw = st.tabs(["Previsão", "Correlação", "Dados"])

    with tab_prev:
        st.subheader("Simulador de previsão")
        if not MODEL_PATH.is_file():
            st.info("A previsão será habilitada após o treino do modelo.")
        else:
            row = {}
            cols = st.columns(3)
            for i, feat in enumerate(FEATURES):
                default = float(df[feat].median())
                row[feat] = cols[i % 3].number_input(feat, value=default)
            if st.button("Prever rendimento"):
                result = predict_yield(row)
                st.success(
                    f"Rendimento previsto: **{result['rendimento_previsto_t_ha']} t/ha**"
                )
                st.info(f"Ação: {result['acao_manejo']} ({result['irrigacao_recomendada']})")

    with tab_corr:
        st.subheader("Correlação entre variáveis")
        corr = df[FEATURES + ["rendimento_t_ha"]].corr()
        st.markdown(
            corr.to_html(classes="dataframe", border=0, float_format=lambda value: f"{value:.3f}"),
            unsafe_allow_html=True,
        )
        st.caption("A tabela mostra as correlações calculadas a partir do CSV local.")

    with tab_raw:
        st.markdown(df.head(100).to_html(index=False, classes="dataframe", border=0), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
