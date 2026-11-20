"""Conferências do modelo. Rode com: python testes.py

Cada teste responde a uma pergunta simples. Se algum falhar, o resultado não é confiável.
"""
import numpy as np

import dados
import sensibilidade
from modelo import nota_multicriterio, otimizar, pesos_com_foco, sem_bateria_na_mao

GER = dados.geracao()
REDE = dados.preco_rede()
CLIENTES = dados.clientes()
PARQUE = dict(conexao_mw=dados.CONEXAO_MW, bateria_mw=dados.BATERIA_MW,
              bateria_mwh=dados.BATERIA_MWH, rendimento=dados.RENDIMENTO_CARGA)


def rodar(cliente, **mudancas):
    c = CLIENTES[cliente]
    return otimizar(GER, c["consumo"], c["preco"], REDE, **{**PARQUE, **mudancas})


def teste_energia_fecha():
    """Toda a energia gerada aparece em algum destino, em todas as horas?"""
    for nome in CLIENTES:
        p = rodar(nome)["plano"]
        soma = p["cliente"] + p["rede"] + p["carga"] + p["corte"]
        assert np.allclose(soma, GER, atol=1e-6), nome


def teste_limites_respeitados():
    """Nenhuma hora passa da conexão, do consumo do cliente ou da bateria?"""
    for nome, c in CLIENTES.items():
        p = rodar(nome)["plano"]
        assert (p["rede"] + p["bat_rede"] <= dados.CONEXAO_MW + 1e-6).all()
        assert (p["cliente"] + p["bat_cli"] <= c["consumo"] + 1e-6).all()
        assert (p["nivel"] <= dados.BATERIA_MWH + 1e-6).all() and (p["nivel"] >= -1e-6).all()
        assert all((p[k] >= -1e-6).all() for k in p)


def teste_pl_igual_conta_na_mao():
    """Sem bateria, a PL dá a mesma receita que a conta feita hora a hora?"""
    for nome, c in CLIENTES.items():
        pl = rodar(nome, bateria_mw=0.0, bateria_mwh=0.0)["receita"]
        mao = sem_bateria_na_mao(GER, c["consumo"], c["preco"], REDE, dados.CONEXAO_MW)
        assert abs(pl - mao) < 1e-3 * mao, (nome, pl, mao)


def teste_preco_sombra_confere():
    """O preço-sombra bate com rodar de novo com 1 MW a mais e 1 MW a menos?

    O ganho de +1 MW nunca é maior que o preço-sombra, e a perda de -1 MW nunca é menor.
    """
    for nome in CLIENTES:
        base = rodar(nome)
        ganho = rodar(nome, conexao_mw=dados.CONEXAO_MW + 1)["receita"] - base["receita"]
        perda = base["receita"] - rodar(nome, conexao_mw=dados.CONEXAO_MW - 1)["receita"]
        sombra = base["preco_sombra_conexao"]
        assert ganho - 1e-3 <= sombra <= perda + 1e-3, (nome, ganho, sombra, perda)


def teste_bateria_nunca_piora():
    """Ter bateria nunca dá menos receita do que não ter?"""
    for nome in CLIENTES:
        assert rodar(nome)["receita"] >= rodar(nome, bateria_mw=0.0, bateria_mwh=0.0)["receita"] - 1e-6


def teste_multicriterio():
    """Pesos somam 1, notas ficam entre 0 e 1, e um exemplo simples dá o esperado?"""
    assert abs(sum(dados.PESOS.values()) - 1) < 1e-9
    for c in dados.PESOS:
        assert abs(sum(pesos_com_foco(dados.PESOS, c).values()) - 1) < 1e-9
    tabela = {"A": {"x": 10, "y": 5}, "B": {"x": 0, "y": 1}}
    notas = nota_multicriterio(tabela, {"x": 0.7, "y": 0.3}, {"y"})
    assert abs(notas["A"] - 0.7) < 1e-9 and abs(notas["B"] - 0.3) < 1e-9


def teste_ganho_cai_com_conexao():
    """O ganho com o data center não aumenta quando a conexão aumenta?"""
    ganhos = [r["ganho"] for r in sensibilidade.por_conexao()]
    assert all(b <= a + 1e-6 for a, b in zip(ganhos, ganhos[1:])), ganhos


def teste_atendimento_entre_0_e_100():
    """O atendimento de cada cliente fica entre 0% e 100%?"""
    for r in sensibilidade.atendimento():
        assert -1e-6 <= r["atendido"] <= 100 + 1e-6, r
        assert 0 <= r["horas_100"] <= dados.HORAS, r


def teste_corte_cai_com_bateria():
    """Sem cliente, a energia cortada nunca aumenta quando a bateria cresce?"""
    cortes = [r["cortada"] for r in sensibilidade.varredura_bateria()]
    assert all(b <= a + 1e-3 for a, b in zip(cortes, cortes[1:])), cortes


def teste_bateria_retorno_decrescente():
    """Cada MWh a mais de bateria rende no máximo o que rendeu o MWh anterior?"""
    ganhos = [r["ganho_por_mwh"] for r in sensibilidade.varredura_bateria()[1:]]
    assert all(b <= a + 1e-3 for a, b in zip(ganhos, ganhos[1:])), ganhos


if __name__ == "__main__":
    testes = [f for nome, f in sorted(globals().items()) if nome.startswith("teste_")]
    for t in testes:
        t()
        print("ok  ", t.__doc__.strip().splitlines()[0])
    print(f"\n{len(testes)} conferências passaram.")
