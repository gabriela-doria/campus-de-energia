"""Dados FICTÍCIOS do exemplo. Nenhum número aqui vem de um parque ou cliente real.

Tudo é gerado por fórmulas simples e uma semente fixa, para o resultado ser
sempre o mesmo. Dinheiro aparece em "u.m." (unidade monetária fictícia).
"""
import numpy as np

HORAS = 168  # uma semana, hora a hora
SEMENTE = 7

# Parque (fictício)
EOLICA_MW = 300.0
SOLAR_MW = 200.0
CONEXAO_MW = 100.0        # limite de energia que cabe na linha até a rede
BATERIA_MW = 50.0         # potência de carga e descarga
BATERIA_MWH = 200.0       # energia que a bateria guarda
RENDIMENTO_CARGA = 0.90   # de cada 1 MWh que entra, 0,9 MWh fica guardado


def geracao():
    """Geração prevista do parque em cada hora (MW)."""
    rng = np.random.default_rng(SEMENTE)
    h = np.arange(HORAS)
    hora_do_dia = h % 24

    # Sol: sobe às 6h, pico ao meio-dia, zera às 18h. Cada dia tem mais ou menos nuvem.
    sol = np.clip(np.sin(np.pi * (hora_do_dia - 6) / 12), 0, None)
    nuvem = np.repeat(rng.uniform(0.65, 1.0, HORAS // 24), 24)
    solar = SOLAR_MW * sol * nuvem

    # Vento: mais forte de madrugada, com variação suave de uma hora para a outra.
    base = 0.45 + 0.20 * np.cos(2 * np.pi * (hora_do_dia - 2) / 24)
    ruido = np.zeros(HORAS)
    for t in range(1, HORAS):
        ruido[t] = 0.9 * ruido[t - 1] + rng.normal(0, 0.06)
    eolica = EOLICA_MW * np.clip(base + ruido, 0.05, 0.95)

    return solar + eolica


def preco_rede():
    """Preço de vender na rede em cada hora (u.m./MWh): barato ao meio-dia, caro à noite."""
    hora_do_dia = np.arange(HORAS) % 24
    preco = np.full(HORAS, 100.0)
    preco[(hora_do_dia >= 10) & (hora_do_dia < 15)] = 60.0
    preco[(hora_do_dia >= 18) & (hora_do_dia < 22)] = 160.0
    return preco


def clientes():
    """Três tipos de cliente que poderiam se instalar ao lado do parque (fictícios).

    consumo: MW em cada hora. preco: u.m./MWh do contrato.
    prazo_meses e empregos_locais são notas de exemplo, não estimativas.
    """
    h = np.arange(HORAS)
    hora_do_dia = h % 24
    dia_util = (h // 24) < 5
    turno = dia_util & (hora_do_dia >= 7) & (hora_do_dia < 19)

    return {
        "Data center": {
            "consumo": np.full(HORAS, 120.0),
            "preco": 130.0,
            "prazo_meses": 30,
            "empregos_locais": 60,
        },
        "Indústria de turno diurno": {
            "consumo": np.where(turno, 150.0, 30.0),
            "preco": 120.0,
            "prazo_meses": 18,
            "empregos_locais": 400,
        },
        "Eletrolisador de hidrogênio": {
            "consumo": np.full(HORAS, 180.0),
            "preco": 95.0,
            "prazo_meses": 42,
            "empregos_locais": 120,
        },
    }


# Pesos da decisão (somam 1). São uma escolha de exemplo: mude e rode de novo.
PESOS = {
    "receita": 0.40,
    "energia_aproveitada": 0.25,
    "prazo_meses": 0.15,
    "empregos_locais": 0.20,
}
# Em quais critérios "menos é melhor".
MENOR_E_MELHOR = {"prazo_meses"}
