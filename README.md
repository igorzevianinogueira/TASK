# FarmTech — Fase 7, Capítulo 1

Pasta integrada de trabalho para reunir os módulos locais das Fases 1, 2, 3 e 6 e iniciá-los pela dashboard.

## Preparar e iniciar

No PowerShell, a partir desta pasta:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python dashboard\scripts\run_pipeline.py
streamlit run dashboard\app.py --server.address 127.0.0.1
```

O pipeline prepara o dataset e o modelo usados pela previsão da dashboard. Depois, a página integrada abre em `http://localhost:8501`.

## Módulos disponíveis

| Fase | Pasta | Como acionar |
|---|---|---|
| 1 — culturas e insumos | `services/fase1/` | Botão **Iniciar menu da Fase 1** ou `python services/fase1/main.py` |
| 2 — irrigação e alertas AWS | `services/fase2/` e `services/alerts_aws/` | Wokwi e comando `CHUVA=0/1`; a dashboard também verifica leituras e pode publicar alertas no SNS |
| 3 — sensores e análise | `services/fase3/` | Botão **Abrir dashboard da Fase 3** ou `python -m streamlit run services/fase3/dashboard/app.py --server.address 127.0.0.1 --server.port 8502` |
| 6 — visão computacional | `services/fase6/` | Botões **Executar demo de classificação** e **Atualizar notebook da Fase 6**, ou `python services/fase6/run_demo.py` |

```powershell
python services\fase6\build_parte_humberto_redes_neurais.py
```

## Interfaces e limitações atuais

- A Fase 1 mantém os registros em memória e exporta CSV pela opção 10. A cópia integrada usa `area_m2` para refletir corretamente a unidade; ver `services/fase1/INTEGRATION.md`.
- A Fase 2 é um sketch do Wokwi. A dashboard não controla o simulador diretamente; o comando climático precisa ser copiado no Serial Monitor. O modo OpenWeather exige uma chave em `OPENWEATHER_API_KEY`.
- A dashboard da Fase 3 usa o CSV local da entrega anterior. Ele segue o schema das leituras, mas é dado simulado e não é gravado diretamente pelo Wokwi.
- A Fase 6 tem uma demo de treino e avaliação sobre 80 imagens sintéticas. Ela não classifica fotos reais enviadas pelo usuário. Os resultados de YOLO no README de origem estão pendentes de reprodução.
- O app principal inclui a previsão da Fase 4. A primeira inicialização deve rodar o pipeline acima para gerar o modelo local.
- Alguns notebooks e READMEs importados ainda mencionam grupos e atividades anteriores. Atualize nomes, RMs, grupo e links para a entrega atual antes de publicar.

## Alertas AWS — SNS por e-mail

O serviço `services/alerts_aws/alert_service.py` lê `dashboard/data/leituras_sensores.csv`, gerado pelo pipeline local. A versão atual é simulada; não representa uma conexão ao vivo com o Wokwi ou sensores físicos.

Cada registro usa `data_hora`, `talhao_id` e `umidade_solo` (percentual). Quando a umidade fica abaixo de 35%, o serviço sugere aumentar a irrigação nas próximas 24 horas. O JSON publicado contém:

```json
{
  "timestamp": "2026-01-01T00:00:00",
  "talhao_id": 2,
  "umidade_solo": 34.9
}
```

Esse limite coincide com a regra de manejo já usada pela previsão da dashboard. O serviço processa uma leitura por execução: por padrão a última linha; `--first-alert` localiza a primeira linha que cruza o limite.

### Preparar a AWS

1. No console da AWS, crie um tópico **Standard** do Amazon SNS na região escolhida.
2. Crie uma assinatura com protocolo **Email** e o endereço que receberá os alertas. O destinatário precisa confirmar a assinatura no e-mail da AWS antes de receber notificações ([documentação oficial](https://docs.aws.amazon.com/sns/latest/dg/sns-email-notifications.html)).
3. Use uma identidade AWS local com permissão `sns:Publish` limitada ao ARN desse tópico ([exemplo de política IAM para um tópico](https://docs.aws.amazon.com/sns/latest/dg/sns-using-identity-based-policies.html)). O serviço usa a cadeia padrão de credenciais do boto3; não grave access keys neste repositório.
4. No mesmo PowerShell em que iniciará o serviço/dashboard, configure região e ARN:

```powershell
$env:AWS_REGION = "us-east-1" # substitua pela região do tópico
$env:SNS_TOPIC_ARN = "arn:aws:sns:REGION:ACCOUNT_ID:NOME_DO_TOPICO"
# Opcional: perfil local já configurado no AWS CLI
$env:AWS_PROFILE = "fiap"
```

O serviço nunca envia por padrão. Primeiro faça a simulação local:

```powershell
python services\alerts_aws\alert_service.py --first-alert
```

Para o teste real, que publica uma mensagem para todos os inscritos confirmados no tópico:

```powershell
python services\alerts_aws\alert_service.py --first-alert --publish
```

Na dashboard, **Visualizar alerta sem enviar** executa apenas a simulação. O botão **Enviar alerta pelo SNS** exige marcar a confirmação e usa a leitura selecionada. Publicações, entregas e chamadas de API podem gerar custos; consulte a [documentação de preços do SNS](https://docs.aws.amazon.com/sns/latest/dg/) antes de usar em escala. Guarde capturas do tópico, da assinatura confirmada e do e-mail de teste; oculte chaves e dados de acesso.

## Validar

```powershell
python -m unittest discover -s services\fase6\tests -v
```

O dataset externo opcional da Fase 6 é grande e não é necessário para a demonstração sintética. Ele está excluído do Git por `.gitignore`; os arquivos originais continuam na pasta da entrega anterior.
