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

## E se as premissas mudarem?

Ganho com o data center = receita com o data center comparada à receita sem cliente, na mesma conexão e na mesma semana.

### Tamanho da conexão

| Conexão (MW) | Energia aproveitada sem cliente | Ganho com o data center |
|---:|---:|---:|
| 100 | 64,1% | +95,6% |
| 150 | 88,3% | +41,5% |
| 200 | 99,0% | +26,0% |
| 300 | 100,0% | +24,5% |

### Preço do contrato do data center (conexão de 100 MW)

| Preço (u.m./MWh) | Ganho com o data center |
|---:|---:|
| 130 | +95,6% |
| 100 | +64,4% |
| 80 | +50,5% |

### Quanto do consumo de cada cliente o parque atende

| Cliente | Parte do consumo atendida | Horas com 100% de atendimento |
|---|---:|---:|
| Data center | 86,8% | 123 de 168 |
| Indústria de turno diurno | 92,6% | 152 de 168 |
| Eletrolisador de hidrogênio | 44,6% | 30 de 168 |

### Outras semanas de vento e sol (semente aleatória)

| Semente | Ganho com o data center |
|---:|---:|
| 1 | +107,2% |
| 2 | +116,6% |
| 3 | +119,8% |
| 7 (padrão) | +95,6% |
| 11 | +118,4% |
| 42 | +113,1% |
