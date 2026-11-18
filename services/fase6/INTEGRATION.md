# Fase 6 — estado da integração

O módulo incluído contém o loader do dataset, a CNN NumPy/PyTorch, os notebooks, o benchmark e quatro testes. A demo executável treina e avalia o classificador nas imagens sintéticas de exemplo. Rode a partir da raiz de `task19_fase7_cap1_integracao`:

```powershell
python services\fase6\build_parte_humberto_redes_neurais.py
python services\fase6\run_demo.py
python -m unittest discover -s services\fase6\tests -v
```

Os notebooks usam o namespace `services.fase6` nesta pasta integrada. O dataset pequeno presente em `data/dataset` é sintético e serve para demonstração e validação técnica. A demo não representa inferência em imagens reais; métricas de YOLO precisam ser reproduzidas antes de serem tratadas como resultado final.
