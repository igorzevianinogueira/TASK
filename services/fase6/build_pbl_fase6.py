from pathlib import Path
import nbformat as nbf

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "parte_humberto_redes_neurais.ipynb"
OUTPUT = BASE / "pbl_fase6.ipynb"

if not SOURCE.exists():
    raise FileNotFoundError(f"Notebook-base não encontrado: {SOURCE}")

nb = nbf.read(SOURCE, as_version=4)

nb.cells.insert(0, nbf.v4.new_markdown_cell("""# FIAP — Fase 6: O despertar da Rede Neural
## FarmTech Solutions — Grupo 29

Notebook integrado da atividade. Reúne a implementação da CNN e o benchmark existentes, além do registro das etapas de detecção com YOLO.

**Integrante responsável por esta integração:** Igor.

> **Transparência dos resultados:** os valores de benchmark herdados da parte do grupo devem ser tratados como referências documentadas até que sua execução seja reproduzida. A detecção com YOLO customizada exige dataset rotulado, treinamento e avaliação verificáveis.
"""))

nb.cells.append(nbf.v4.new_markdown_cell("""## 8. Entrega integrada — checklist de validação

- [ ] Confirmar que as 80 imagens são adequadas ao cenário e documentar suas fontes.
- [ ] Exportar as anotações de caixas delimitadoras do Make Sense AI.
- [ ] Configurar e executar o treinamento da YOLO customizada.
- [ ] Comparar pelo menos duas configurações de épocas e registrar os resultados reais.
- [ ] Executar detecções nas imagens de teste e exibir as imagens resultantes.
- [ ] Executar todas as células deste notebook no ambiente final.
- [ ] Atualizar o README com os resultados reproduzidos e o link do vídeo demonstrativo.

As etapas não marcadas acima não são declaradas como concluídas por este notebook.
"""))

nb.metadata["kernelspec"] = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}

nbf.write(nb, OUTPUT)
print(f"[OK] Notebook integrado gerado: {OUTPUT}")
