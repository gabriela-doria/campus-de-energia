"""Roda tudo: otimiza cada cenário, compara os clientes e salva tabela e gráficos.

Uso: python rodar.py
Saídas: resultados.md e a pasta figuras/
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import dados
from modelo import nota_multicriterio, otimizar, pesos_com_foco

PASTA = Path(__file__).parent
AZUL, LARANJA, VERDE, CINZA = "#2a78d6", "#eb6834", "#1baf7a", "#c3c2b7"
FUNDO, TINTA, TINTA_2 = "#fcfcfb", "#0b0b0b", "#52514e"


def num(x, casas=0):
    """Número no formato brasileiro: 1.234,5"""
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def simular():
    ger, rede = dados.geracao(), dados.preco_rede()
    parque = dict(conexao_mw=dados.CONEXAO_MW, bateria_mw=dados.BATERIA_MW,
                  bateria_mwh=dados.BATERIA_MWH, rendimento=dados.RENDIMENTO_CARGA)
    cenarios = {"Sem cliente (só rede)": {"consumo": np.zeros(dados.HORAS), "preco": 0.0}}
    cenarios.update(dados.clientes())
    return ger, {nome: {**c, **otimizar(ger, c["consumo"], c["preco"], rede, **parque)}
                 for nome, c in cenarios.items()}


def comparar(resultados):
    """Monta a matriz de decisão só com os clientes (o cenário sem cliente é a referência)."""
    tabela = {nome: {c: r[c] for c in dados.PESOS}
              for nome, r in resultados.items() if nome in dados.clientes()}
    notas = nota_multicriterio(tabela, dados.PESOS, dados.MENOR_E_MELHOR)
    focos = {}
    for criterio in dados.PESOS:
        n = nota_multicriterio(tabela, pesos_com_foco(dados.PESOS, criterio), dados.MENOR_E_MELHOR)
        focos[criterio] = max(n, key=n.get)
    return tabela, notas, focos


def escrever_tabelas(resultados, tabela, notas, focos):
    L = ["# Resultados (dados fictícios)", "",
         "Gerado por `python rodar.py`. Dinheiro em u.m. (unidade monetária fictícia). Período: 1 semana.", "",
         "## Simulação hora a hora", "",
         "| Cenário | Receita (u.m.) | Energia aproveitada | Energia cortada (MWh) | 1 MW a mais de conexão vale (u.m./semana) | Horas com a conexão cheia |",
         "|---|---:|---:|---:|---:|---:|"]
    for nome, r in resultados.items():
        L.append(f"| {nome} | {num(r['receita'])} | {num(r['energia_aproveitada'], 1)}% | "
                 f"{num(r['energia_cortada'])} | {num(r['preco_sombra_conexao'])} | {r['horas_conexao_cheia']} de {dados.HORAS} |")
    L += ["", "## Matriz de decisão", "",
          "| Cliente | Receita (u.m.) | Energia aproveitada | Prazo (meses) | Empregos locais | Nota final (0 a 1) |",
          "|---|---:|---:|---:|---:|---:|"]
    for nome in sorted(notas, key=notas.get, reverse=True):
        t = tabela[nome]
        L.append(f"| {nome} | {num(t['receita'])} | {num(t['energia_aproveitada'], 1)}% | "
                 f"{t['prazo_meses']} | {t['empregos_locais']} | {num(notas[nome], 2)} |")
    L += ["", "Pesos: " + ", ".join(f"{c.replace('_', ' ')} {int(round(p * 100))}%" for c, p in dados.PESOS.items()) + ".",
          "", "## E se os pesos mudarem?", "",
          "Cada linha dá 55% do peso a um critério e divide o resto na proporção original.", "",
          "| Critério com mais peso | Quem ganha |", "|---|---|"]
    L += [f"| {c.replace('_', ' ')} | {v} |" for c, v in focos.items()]
    (PASTA / "resultados.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def estilo(ax):
    ax.set_facecolor(FUNDO)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(CINZA)
    ax.tick_params(colors=TINTA_2, length=0, labelsize=9)
    ax.grid(axis="y", color="#e8e7e2", linewidth=0.8)
    ax.set_axisbelow(True)


def grafico_destino(ger, resultados, cliente="Data center", horas=72):
    """Dois painéis com a mesma escala: para onde vai a geração, sem e com o cliente."""
    fig, eixos = plt.subplots(2, 1, figsize=(9, 6.2), sharex=True, sharey=True, facecolor=FUNDO)
    h = np.arange(horas)
    for ax, nome in zip(eixos, ["Sem cliente (só rede)", cliente]):
        p = resultados[nome]["plano"]
        camadas = [("Cliente vizinho", p["cliente"], AZUL), ("Rede", p["rede"], LARANJA),
                   ("Carga da bateria", p["carga"], VERDE), ("Cortada (desperdiçada)", p["corte"], CINZA)]
        camadas = [c for c in camadas if c[1].sum() > 0]
        ax.stackplot(h, [c[1][:horas] for c in camadas], colors=[c[2] for c in camadas],
                     labels=[c[0] for c in camadas], edgecolor=FUNDO, linewidth=0.6)
        estilo(ax)
        ax.set_title(f"{nome}: {num(resultados[nome]['energia_aproveitada'], 1)}% da energia aproveitada",
                     loc="left", fontsize=11, color=TINTA, fontweight="bold")
        ax.set_ylabel("MW", color=TINTA_2, fontsize=9)
        ax.legend(loc="upper right", ncols=4, frameon=False, fontsize=8.5, labelcolor=TINTA_2)
    eixos[0].set_ylim(0, ger[:horas].max() * 1.22)
    eixos[1].set_xticks(np.arange(0, horas + 1, 12))
    eixos[1].set_xticklabels([f"dia {t // 24 + 1}\n{t % 24}h" for t in np.arange(0, horas + 1, 12)])
    eixos[1].set_xlim(0, horas - 1)
    fig.suptitle("Para onde vai a energia de cada hora (3 primeiros dias, dados fictícios)",
                 x=0.01, ha="left", fontsize=12.5, color=TINTA)
    fig.tight_layout()
    fig.savefig(PASTA / "figuras" / "destino_da_energia.png", dpi=160)
    plt.close(fig)


def grafico_notas(notas):
    fig, ax = plt.subplots(figsize=(9, 2.6), facecolor=FUNDO)
    ordem = sorted(notas, key=notas.get)
    barras = ax.barh(ordem, [notas[n] for n in ordem], color=AZUL, height=0.55)
    ax.bar_label(barras, labels=[num(notas[n], 2) for n in ordem], padding=5, color=TINTA, fontsize=10)
    estilo(ax)
    ax.grid(False)
    ax.set_xlim(0, 1)
    ax.set_xticks([0, 0.5, 1], labels=["0", "0,5", "1"])
    ax.tick_params(axis="y", labelsize=10, colors=TINTA)
    ax.set_title("Nota final de cada cliente (0 a 1, dados fictícios)", loc="left", fontsize=12.5, color=TINTA)
    fig.tight_layout()
    fig.savefig(PASTA / "figuras" / "nota_dos_clientes.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    (PASTA / "figuras").mkdir(exist_ok=True)
    ger, resultados = simular()
    tabela, notas, focos = comparar(resultados)
    escrever_tabelas(resultados, tabela, notas, focos)
    grafico_destino(ger, resultados)
    grafico_notas(notas)
    print((PASTA / "resultados.md").read_text(encoding="utf-8"))
