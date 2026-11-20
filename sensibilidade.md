# Mais bateria ou mais conexão? (dados fictícios)

Gerado por `python sensibilidade.py`. Dinheiro em u.m. (unidade monetária fictícia). Período: 1 semana. Cenário: sem cliente (só rede).

## A. Tamanho da bateria (conexão de 100 MW)

Duração fixa de 4 horas: potência = energia / 4.

| Bateria (MWh) | Potência (MW) | Receita (u.m.) | Energia cortada (MWh) | Energia aproveitada | Ganho por MWh a mais de bateria (u.m./semana) |
|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 1.603.415 | 10.902 | 59,6% | - |
| 100 | 25 | 1.653.722 | 10.213 | 62,1% | 503 |
| 200 (padrão) | 50 | 1.678.892 | 9.674 | 64,1% | 252 |
| 400 | 100 | 1.702.818 | 8.709 | 67,7% | 120 |
| 800 | 200 | 1.708.000 | 8.294 | 69,2% | 13 |

Ganho por MWh = receita a mais dividida pelos MWh de bateria a mais, em relação à linha de cima.

## B. Tamanho da conexão (bateria de 200 MWh e 50 MW)

| Conexão (MW) | Receita (u.m.) | Energia cortada (MWh) | Energia aproveitada | 1 MW a mais de conexão vale (u.m./semana) |
|---:|---:|---:|---:|---:|
| 100 (padrão) | 1.678.892 | 9.674 | 64,1% | 15.450 |
| 150 | 2.345.490 | 3.159 | 88,3% | 9.400 |
| 200 | 2.641.029 | 261 | 99,0% | 1.950 |
| 300 | 2.674.441 | 0 | 100,0% | 0 |
