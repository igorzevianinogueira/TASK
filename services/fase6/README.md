# Serviço da Fase 6 — FarmTech

O módulo contém loader de imagens, classificador NumPy, template PyTorch, benchmark, notebooks e testes. Ele foi integrado sob o namespace `services.fase6`.

Na raiz do projeto integrado:

```powershell
python -m unittest discover -s services\fase6\tests -v
python services\fase6\build_parte_humberto_redes_neurais.py
python services\fase6\run_demo.py
```

As 80 imagens de `data/dataset` são sintéticas e servem para demonstração e validação técnica. A dashboard executa a demo de treino e avaliação nesse conjunto; ela não classifica imagens reais enviadas pelo usuário. O notebook de benchmark contém itens pendentes de reprodução; consulte `INTEGRATION.md` e o README principal antes de usar métricas como resultados finais.

Os notebooks originais mantêm alguns metadados da entrega anterior. Atualize grupo, integrantes e referências antes de usá-los na entrega atual.
