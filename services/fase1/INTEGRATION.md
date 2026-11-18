# Fase 1 — notas de integração

## Como iniciar

No PowerShell, a partir da raiz do repositório:

```powershell
python .\services\fase1\main.py
```

Ou dentro desta pasta:

```powershell
python .\main.py
```

O módulo usa apenas a biblioteca padrão do Python; não precisa instalar dependências.

## Análises em R

Depois de exportar os CSVs no menu Python (opção 10), rode a análise de culturas e manejos na raiz do projeto integrado:

```powershell
Rscript services\fase1\estatistica.R
```

`clima_estatistica.R` consulta dados públicos do Open-Meteo e requer R, o pacote `jsonlite` e acesso à internet. R não está disponível no ambiente local verificado.

## O que oferece

- Cadastro, listagem, busca, atualização e remoção de culturas.
- Cálculo de área retangular para cana-de-açúcar e circular para café.
- Cadastro e atualização de manejo de insumos.
- Exportação de culturas e manejos para `dados_culturas.csv` e `dados_manejos.csv`.

## Entrada e saída para a integração

O menu é interativo e lê respostas do terminal. As funções de domínio ficam em `culturas.py`.
Os registros vivem em listas na memória enquanto o processo está aberto. Os CSVs existentes
são dados de exemplo/saída: o programa não os carrega automaticamente ao iniciar, e a opção
de exportação os sobrescreve.

Para a entrega integrada, a opção mais direta é disponibilizar o comando acima no README
principal e acioná-lo em um terminal separado pela dashboard. Se a dashboard precisar ler os
dados, deve consumir os CSVs após a exportação; um processo separado não compartilha as listas
em memória.

## Limitação conhecida

Nesta pasta integrada, a área é exportada como `area_m2`, correspondente ao cálculo
comprimento × largura ou π × raio². O CSV de exemplo e a análise em R foram atualizados com
esse nome. A conversão de m² para hectares é divisão por 10.000. Os arquivos legados originais
permanecem inalterados na pasta anterior.
