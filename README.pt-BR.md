# doc-analyzer-evals: extração com eval gold-standard

*[English](README.md)*

Extração estruturada de campos de documentos como faturas e recibos, com uma avaliação mensurável junto. "Quão boa é a extração?" ganha uma resposta numérica aqui, que é justamente a parte que costuma ser pulada.

## O que faz

Dado o texto de um documento, devolve um objeto tipado com fornecedor, número do documento, data de emissão, total e moeda. O harness de avaliação então pontua essas previsões contra um conjunto gold-standard, reportando precision, recall e F1 por campo. Um gate de limiar transforma a eval em algo que um build pode reprovar.

## Por que é construído assim

- **Extração tipada via tool use.** O alvo é um modelo Pydantic; o JSON schema dele é passado ao modelo como contrato da tool, então a resposta é um objeto estruturado, não prosa para parsear. A validação é papel do schema.
- **Uma avaliação de verdade.** Um conjunto gold-standard de documentos com campos esperados alimenta precision/recall/F1 por campo e micro-averaged, mais acurácia de exact-match. Extrações que faltam aparecem como perda de recall; extrações a mais, como perda de precision.
- **Comparação justa por normalização.** Gold e previsão passam pelo mesmo normalizador antes de comparar, então `R$ 1.234,56` e `1234.56`, ou `12/03/2026` e `2026-03-12`, contam como iguais. Diferença de formatação não custa nada na nota; dado errado continua custando.
- **Um gate, como em produção.** O `run_eval.py` sai com código não-zero quando o F1 geral fica abaixo do limiar, a mesma disciplina que você usaria para gatear um release pela qualidade de recuperação.
- **Testável offline.** O extrator é injetado no harness, então métricas, normalização e o resto do loop de pontuação rodam sob teste com um extrator fake e sem API key.

## Rodar a eval

```bash
pip install -r requirements.txt
cp .env.example .env        # coloque sua ANTHROPIC_API_KEY
python eval/run_eval.py --min-f1 0.8
```

A saída é uma tabela por campo, o F1 micro-averaged, a acurácia de exact-match e uma linha PASS/FAIL (com código de saída correspondente).

## Testes

Métricas, normalização, o schema e o harness (com extrator fake) rodam sem API key:

```bash
python -m pytest -q
```

## Estrutura

```
docanalyzer/
├── schema.py       # ExtractedDocument (Pydantic): alvo da extração + contrato da tool
├── extractor.py    # chamada Claude por tool use (import preguiçoso)
├── normalize.py    # normalização de dinheiro / data / texto para comparação justa
├── metrics.py      # precision / recall / F1 + o gate
└── harness.py      # amarra gold set + extrator + métricas
eval/
├── gold_standard.jsonl   # documentos fictícios + campos esperados
└── run_eval.py           # CLI: relatório + gate de limiar
```

## Stack

Python · Anthropic (Claude, tool use) · Pydantic · pytest.

> Os documentos do gold-standard são fictícios.
