-- FarmTech Cap 1 - 5 queries analiticas (Humberto)
-- Rodar apos: python scripts/ingest_iot.py
-- Banco esperado: data/farmtech_iot.db

-- Q1: Volume de leituras por talhao.
-- Uso: confirmar se todos os talhoes foram monitorados de forma equilibrada.
SELECT
    talhao_id,
    COUNT(*) AS total_leituras,
    MIN(data_hora) AS primeira_leitura,
    MAX(data_hora) AS ultima_leitura
FROM leituras_sensores
GROUP BY talhao_id
ORDER BY talhao_id;

-- Q2: Perfil medio de solo por talhao.
-- Uso: comparar umidade, pH e NPK para priorizar manejo por area.
SELECT
    talhao_id,
    ROUND(AVG(umidade_solo), 2) AS media_umidade,
    ROUND(AVG(ph_solo), 2) AS media_ph,
    ROUND(AVG(nitrogenio), 2) AS media_nitrogenio,
    ROUND(AVG(fosforo), 2) AS media_fosforo,
    ROUND(AVG(potassio), 2) AS media_potassio,
    ROUND(AVG(rendimento_t_ha), 2) AS rendimento_medio
FROM leituras_sensores
GROUP BY talhao_id
ORDER BY rendimento_medio DESC;

-- Q3: Alertas de umidade baixa.
-- Uso: localizar leituras que pedem avaliacao rapida de irrigacao.
SELECT
    data_hora,
    talhao_id,
    umidade_solo,
    ph_solo,
    temperatura_c,
    irrigacao_sugerida_l
FROM leituras_sensores
WHERE umidade_solo < 35
ORDER BY data_hora DESC
LIMIT 20;

-- Q4: Top 10 maiores rendimentos registrados.
-- Uso: observar condicoes associadas aos melhores cenarios do dataset.
SELECT
    data_hora,
    talhao_id,
    rendimento_t_ha,
    umidade_solo,
    ph_solo,
    nitrogenio,
    fosforo,
    potassio,
    temperatura_c
FROM leituras_sensores
ORDER BY rendimento_t_ha DESC
LIMIT 10;

-- Q5: Media diaria de rendimento e irrigacao.
-- Uso: acompanhar tendencia temporal de produtividade e necessidade hidrica.
SELECT
    DATE(data_hora) AS dia,
    ROUND(AVG(rendimento_t_ha), 2) AS rendimento_medio,
    ROUND(AVG(umidade_solo), 2) AS umidade_media,
    ROUND(AVG(irrigacao_sugerida_l), 2) AS irrigacao_media_l,
    COUNT(*) AS leituras
FROM leituras_sensores
GROUP BY DATE(data_hora)
ORDER BY dia
LIMIT 30;
