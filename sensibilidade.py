"""E se as premissas mudarem? Roda a mesma PL com conexão, preço, clientes e semana diferentes.

Também responde: sem cliente, o que corta menos energia, mais bateria ou mais conexão?

Uso: importado por rodar.py e testes.py. Rodar sozinho (python sensibilidade.py) grava
sensibilidade.md e figuras/corte_por_bateria_e_conexao.png e mostra as tabelas na tela.
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


# Segunda pergunta: no cenário sem cliente, o que corta menos energia,
# mais bateria ou mais conexão?
BATERIAS_MWH = [0.0, 100.0, 200.0, 400.0, 800.0]
DURACAO_BATERIA_H = 4.0   # bateria_mw = bateria_mwh / 4


def _sem_cliente(conexao_mw, bateria_mw, bateria_mwh):
    return otimizar(dados.geracao(), np.zeros(dados.HORAS), 0.0, dados.preco_rede(),
                    conexao_mw=conexao_mw, bateria_mw=bateria_mw, bateria_mwh=bateria_mwh,
                    rendimento=dados.RENDIMENTO_CARGA)


def varredura_bateria():
    """(A) Sem cliente e com a conexão padrão: muda o tamanho da bateria (sempre 4 horas)."""
    linhas = []
    for mwh in BATERIAS_MWH:
        r = _sem_cliente(dados.CONEXAO_MW, mwh / DURACAO_BATERIA_H, mwh)
        linha = {"bateria_mwh": mwh, "receita": r["receita"], "cortada": r["energia_cortada"],
                 "aproveitada": r["energia_aproveitada"], "ganho_por_mwh": None}
        if linhas:
            ant = linhas[-1]
            linha["ganho_por_mwh"] = (r["receita"] - ant["receita"]) / (mwh - ant["bateria_mwh"])
        linhas.append(linha)
    return linhas


def varredura_conexao():
    """(B) Sem cliente e com a bateria padrão: muda o tamanho da conexão."""
    linhas = []
    for mw in CONEXOES_MW:
        r = _sem_cliente(mw, dados.BATERIA_MW, dados.BATERIA_MWH)
        linhas.append({"conexao_mw": mw, "receita": r["receita"], "cortada": r["energia_cortada"],
                       "aproveitada": r["energia_aproveitada"],
                       "preco_sombra": r["preco_sombra_conexao"]})
    return linhas


def escrever_tabelas(bat, con):
    """Grava sensibilidade.md no mesmo formato de resultados.md."""
    from rodar import PASTA, num
    L = ["# Mais bateria ou mais conexão? (dados fictícios)", "",
         "Gerado por `python sensibilidade.py`. Dinheiro em u.m. (unidade monetária fictícia). "
         "Período: 1 semana. Cenário: sem cliente (só rede).", "",
         f"## A. Tamanho da bateria (conexão de {num(dados.CONEXAO_MW)} MW)", "",
         f"Duração fixa de {num(DURACAO_BATERIA_H)} horas: potência = energia / {num(DURACAO_BATERIA_H)}.", "",
         "| Bateria (MWh) | Potência (MW) | Receita (u.m.) | Energia cortada (MWh) | Energia aproveitada "
         "| Ganho por MWh a mais de bateria (u.m./semana) |",
         "|---:|---:|---:|---:|---:|---:|"]
    for r in bat:
        ganho = "-" if r["ganho_por_mwh"] is None else num(r["ganho_por_mwh"])
        padrao = " (padrão)" if r["bateria_mwh"] == dados.BATERIA_MWH else ""
        L.append(f"| {num(r['bateria_mwh'])}{padrao} | {num(r['bateria_mwh'] / DURACAO_BATERIA_H)} | "
                 f"{num(r['receita'])} | {num(r['cortada'])} | {num(r['aproveitada'], 1)}% | {ganho} |")
    L += ["", "Ganho por MWh = receita a mais dividida pelos MWh de bateria a mais, "
          "em relação à linha de cima.", "",
          f"## B. Tamanho da conexão (bateria de {num(dados.BATERIA_MWH)} MWh e "
          f"{num(dados.BATERIA_MW)} MW)", "",
          "| Conexão (MW) | Receita (u.m.) | Energia cortada (MWh) | Energia aproveitada "
          "| 1 MW a mais de conexão vale (u.m./semana) |",
          "|---:|---:|---:|---:|---:|"]
    for r in con:
        padrao = " (padrão)" if r["conexao_mw"] == dados.CONEXAO_MW else ""
        L.append(f"| {num(r['conexao_mw'])}{padrao} | {num(r['receita'])} | {num(r['cortada'])} | "
                 f"{num(r['aproveitada'], 1)}% | {num(r['preco_sombra'])} |")
    (PASTA / "sensibilidade.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def grafico_corte(bat, con):
    """Um gráfico: energia cortada nas duas varreduras, com o tamanho em múltiplos do padrão."""
    import matplotlib.pyplot as plt
    from rodar import AZUL, FUNDO, LARANJA, PASTA, TINTA, TINTA_2, estilo, num

    fig, ax = plt.subplots(figsize=(9, 4.6), facecolor=FUNDO)
    # (nome, cor, x, y, rótulos, deslocamento dos rótulos, onde fica o nome da linha)
    series = [
        ("Mais bateria", AZUL, [r["bateria_mwh"] / dados.BATERIA_MWH for r in bat],
         [r["cortada"] for r in bat], [f"{num(r['bateria_mwh'])} MWh" for r in bat],
         (0, 9), "center", 3.0, (0, 14)),
        ("Mais conexão", LARANJA, [r["conexao_mw"] / dados.CONEXAO_MW for r in con],
         [r["cortada"] for r in con], [f"{num(r['conexao_mw'])} MW" for r in con],
         (9, 3), "left", 1.25, (10, 0)),
    ]
    for nome, cor, x, y, rotulos, desloc, alinha, x_nome, desloc_nome in series:
        ax.plot(x, y, color=cor, linewidth=2.2, marker="o", markersize=6, zorder=3)
        for xi, yi, rot in zip(x, y, rotulos):
            if xi == 1:  # ponto padrão, comum às duas linhas: rotulado uma vez só, abaixo
                continue
            ax.annotate(rot, (xi, yi), textcoords="offset points", xytext=desloc,
                        ha=alinha, fontsize=8.5, color=cor)
        ax.annotate(nome, (x_nome, np.interp(x_nome, x, y)), textcoords="offset points",
                    xytext=desloc_nome, ha="left" if alinha == "left" else "center",
                    va="center", fontsize=10, color=cor, fontweight="bold")
    padrao = bat[BATERIAS_MWH.index(dados.BATERIA_MWH)]["cortada"]
    ax.annotate(f"padrão: {num(dados.BATERIA_MWH)} MWh e {num(dados.CONEXAO_MW)} MW",
                (1, padrao), textcoords="offset points", xytext=(-8, -4), ha="right", va="top",
                fontsize=8.5, color=TINTA_2)
    estilo(ax)
    ax.set_xlim(-0.15, 4.4)
    ax.set_ylim(0, max(r["cortada"] for r in bat) * 1.15)
    ax.set_xticks([0, 1, 2, 3, 4], labels=["0x", "1x\n(padrão)", "2x", "3x", "4x"])
    ax.set_xlabel("Tamanho em relação ao padrão (bateria 200 MWh, conexão 100 MW)",
                  color=TINTA_2, fontsize=9)
    ax.set_ylabel("Energia cortada na semana (MWh)", color=TINTA_2, fontsize=9)
    ax.yaxis.set_major_formatter(lambda v, _: num(v))
    ax.set_title("Sem cliente: energia cortada com mais bateria ou mais conexão (dados fictícios)",
                 loc="left", fontsize=12.5, color=TINTA)
    fig.tight_layout()
    fig.savefig(PASTA / "figuras" / "corte_por_bateria_e_conexao.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    from rodar import PASTA

    bat, con = varredura_bateria(), varredura_conexao()
    escrever_tabelas(bat, con)
    grafico_corte(bat, con)
    print((PASTA / "sensibilidade.md").read_text(encoding="utf-8"))
