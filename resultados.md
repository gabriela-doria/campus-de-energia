# Resultados (dados fictícios)

Gerado por `python rodar.py`. Dinheiro em u.m. (unidade monetária fictícia). Período: 1 semana.

## Simulação hora a hora

| Cenário | Receita (u.m.) | Energia aproveitada | Energia cortada (MWh) | 1 MW a mais de conexão vale (u.m./semana) | Horas com a conexão cheia |
|---|---:|---:|---:|---:|---:|
| Sem cliente (só rede) | 1.678.892 | 64,1% | 9.674 | 15.450 | 155 de 168 |
| Data center | 3.284.602 | 100,0% | 7 | 1.350 | 35 de 168 |
| Indústria de turno diurno | 2.781.119 | 93,2% | 1.827 | 7.800 | 97 de 168 |
| Eletrolisador de hidrogênio | 2.767.045 | 100,0% | 0 | 1.977 | 118 de 168 |

## Matriz de decisão

| Cliente | Receita (u.m.) | Energia aproveitada | Prazo (meses) | Empregos locais | Nota final (0 a 1) |
|---|---:|---:|---:|---:|---:|
| Data center | 3.284.602 | 100,0% | 30 | 60 | 0,72 |
| Indústria de turno diurno | 2.781.119 | 93,2% | 18 | 400 | 0,36 |
| Eletrolisador de hidrogênio | 2.767.045 | 100,0% | 42 | 120 | 0,29 |

Pesos: receita 40%, energia aproveitada 25%, prazo meses 15%, empregos locais 20%.

## E se os pesos mudarem?

Cada linha dá 55% do peso a um critério e divide o resto na proporção original.

| Critério com mais peso | Quem ganha |
|---|---|
| receita | Data center |
| energia aproveitada | Data center |
| prazo meses | Indústria de turno diurno |
| empregos locais | Indústria de turno diurno |
