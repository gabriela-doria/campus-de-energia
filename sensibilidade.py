"""E se as premissas mudarem? Roda a mesma PL com conexão, preço, clientes e semana diferentes.

Uso: importado por rodar.py e testes.py. Rodar sozinho mostra os números na tela.
"""
import numpy as np

import dados
from modelo import otimizar

CONEXOES_MW = [100.0, 150.0, 200.0, 300.0]
PRECOS_DATA_CENTER = [130.0, 100.0, 80.0]
SEMENTES = [1, 2, 3, 7, 11, 42]


def _rodar(ger, consumo, preco, conexao_mw):
    return otimizar(ger, consumo, preco, dados.preco_rede(), conexao_mw=conexao_mw,
                    bateria_mw=dados.BATERIA_MW, bateria_mwh=dados.BATERIA_MWH,
                    rendimento=dados.RENDIMENTO_CARGA)


def ganho_data_center(ger=None, conexao_mw=dados.CONEXAO_MW, preco=None):
    """Ganho de receita (%) com o data center, comparado a não ter cliente na mesma conexão.

    Devolve (ganho em %, resultado sem cliente).
    """
    ger = dados.geracao() if ger is None else ger
    dc = dados.clientes()["Data center"]
    preco = dc["preco"] if preco is None else preco
    sem = _rodar(ger, np.zeros(dados.HORAS), 0.0, conexao_mw)
    com = _rodar(ger, dc["consumo"], preco, conexao_mw)
    return 100 * (com["receita"] / sem["receita"] - 1), sem


def por_conexao():
    """(a) Para cada conexão: energia aproveitada sem cliente e ganho com o data center."""
    linhas = []
    for mw in CONEXOES_MW:
        ganho, sem = ganho_data_center(conexao_mw=mw)
        linhas.append({"conexao_mw": mw, "aproveitada_sem_cliente": sem["energia_aproveitada"],
                       "ganho": ganho})
    return linhas


def por_preco():
    """(b) Para cada preço do contrato do data center, com a conexão padrão: ganho de receita."""
    return [{"preco": p, "ganho": ganho_data_center(preco=p)[0]} for p in PRECOS_DATA_CENTER]


def atendimento():
    """(c) Para cada cliente: parte do consumo atendida pelo parque e horas com 100% atendido."""
    ger = dados.geracao()
    linhas = []
    for nome, c in dados.clientes().items():
        p = _rodar(ger, c["consumo"], c["preco"], dados.CONEXAO_MW)["plano"]
        recebido = p["cliente"] + p["bat_cli"]
        linhas.append({"cliente": nome,
                       "atendido": 100 * recebido.sum() / c["consumo"].sum(),
                       "horas_100": int((recebido >= c["consumo"] - 1e-6).sum())})
    return linhas


def por_semente():
    """(d) Para cada semente (outra semana de vento e sol): ganho com o data center."""
    return [{"semente": s, "ganho": ganho_data_center(ger=dados.geracao(s))[0]} for s in SEMENTES]


def tudo():
    return {"conexao": por_conexao(), "preco": por_preco(),
            "atendimento": atendimento(), "semente": por_semente()}


if __name__ == "__main__":
    for nome, linhas in tudo().items():
        print(nome)
        for linha in linhas:
            print("  ", linha)
