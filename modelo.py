"""Modelo: para onde vai a energia de cada hora, e qual cliente combina mais com o parque.

Parte 1 - programação linear (PL): escolhe, hora a hora, quanto da geração vai
para o cliente vizinho, para a rede e para a bateria, para a receita ser máxima.
Parte 2 - preço-sombra: quanto a receita subiria com 1 MW a mais de conexão.
Parte 3 - decisão multicritério: nota final de cada cliente, com pesos.
"""
import numpy as np
from scipy.optimize import linprog


def otimizar(geracao, consumo, preco_cliente, preco_rede,
             conexao_mw, bateria_mw, bateria_mwh, rendimento):
    """Resolve a PL de uma semana. Devolve um dicionário com o plano e os totais.

    Variáveis em cada hora t (todas em MW, e passo de 1 hora):
      cliente[t]   geração que vai direto para o cliente
      rede[t]      geração que vai direto para a rede
      carga[t]     geração que entra na bateria
      bat_cli[t]   bateria que descarrega para o cliente
      bat_rede[t]  bateria que descarrega para a rede
      corte[t]     geração que não cabe em lugar nenhum (desperdiçada)
      nivel[t]     energia guardada na bateria no fim da hora (MWh)
    """
    T = len(geracao)
    nomes = ["cliente", "rede", "carga", "bat_cli", "bat_rede", "corte", "nivel"]
    pos = {n: slice(i * T, (i + 1) * T) for i, n in enumerate(nomes)}
    n_var = len(nomes) * T
    I = np.eye(T)

    def bloco(**partes):
        """Monta uma linha de matriz com um pedaço para cada variável citada."""
        m = np.zeros((T, n_var))
        for nome, matriz in partes.items():
            m[:, pos[nome]] = matriz
        return m

    # Objetivo: o linprog minimiza, então usamos a receita com sinal trocado.
    custo = np.zeros(n_var)
    custo[pos["cliente"]] = -preco_cliente
    custo[pos["bat_cli"]] = -preco_cliente
    custo[pos["rede"]] = -preco_rede
    custo[pos["bat_rede"]] = -preco_rede

    # Igualdade 1: toda a geração da hora tem um destino.
    A_ger = bloco(cliente=I, rede=I, carga=I, corte=I)

    # Igualdade 2: nível da bateria = nível da hora anterior + o que entrou - o que saiu.
    # A semana fecha em ciclo: o nível antes da hora 0 é o da última hora.
    anterior = np.roll(I, -1, axis=0).T  # linha t pega o nível de t-1
    A_bat = bloco(nivel=I - anterior, carga=-rendimento * I, bat_cli=I, bat_rede=I)

    A_eq = np.vstack([A_ger, A_bat])
    b_eq = np.concatenate([geracao, np.zeros(T)])

    # Desigualdades (<=), nesta ordem: conexão, consumo do cliente, potência da bateria.
    A_ub = np.vstack([
        bloco(rede=I, bat_rede=I),        # o que vai para a rede cabe na conexão
        bloco(cliente=I, bat_cli=I),      # o cliente não recebe mais do que consome
        bloco(bat_cli=I, bat_rede=I),     # descarga limitada pela potência
    ])
    b_ub = np.concatenate([np.full(T, conexao_mw), consumo, np.full(T, bateria_mw)])

    limites = [(0, None)] * n_var
    for i in range(T):
        limites[pos["carga"].start + i] = (0, bateria_mw)
        limites[pos["nivel"].start + i] = (0, bateria_mwh)

    sol = linprog(custo, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=limites, method="highs")
    if not sol.success:
        raise RuntimeError("A otimização não fechou: " + sol.message)

    plano = {n: sol.x[pos[n]] for n in nomes}
    entregue = plano["cliente"] + plano["bat_cli"] + plano["rede"] + plano["bat_rede"]

    # Preço-sombra da conexão: o solver devolve, para cada hora, quanto o objetivo
    # mudaria se o limite daquela hora subisse 1 MW. Somamos as horas da semana.
    sombra_por_hora = -sol.ineqlin.marginals[:T]

    return {
        "plano": plano,
        "receita": -sol.fun,
        "energia_gerada": geracao.sum(),
        "energia_entregue": entregue.sum(),
        "energia_cortada": plano["corte"].sum(),
        "energia_aproveitada": 100 * (1 - plano["corte"].sum() / geracao.sum()),
        "preco_sombra_conexao": sombra_por_hora.sum(),
        "horas_conexao_cheia": int((sombra_por_hora > 1e-6).sum()),
    }


def sem_bateria_na_mao(geracao, consumo, preco_cliente, preco_rede, conexao_mw):
    """Conferência independente: sem bateria, cada hora se resolve sozinha.

    Basta mandar a energia primeiro para quem paga mais. Serve para checar a PL.
    """
    receita = 0.0
    for g, c, pr in zip(geracao, consumo, preco_rede):
        destinos = sorted([(preco_cliente, c), (pr, conexao_mw)], reverse=True)
        for preco, limite in destinos:
            usado = min(g, limite)
            receita += preco * usado
            g -= usado
    return receita


def nota_multicriterio(tabela, pesos, menor_e_melhor):
    """Soma ponderada. Cada critério vira uma nota de 0 (pior) a 1 (melhor).

    tabela: {alternativa: {criterio: valor}}. Devolve {alternativa: nota final}.
    """
    notas = {a: 0.0 for a in tabela}
    for criterio, peso in pesos.items():
        valores = np.array([tabela[a][criterio] for a in tabela], dtype=float)
        faixa = valores.max() - valores.min()
        normal = np.zeros_like(valores) if faixa == 0 else (valores - valores.min()) / faixa
        if criterio in menor_e_melhor:
            normal = 1 - normal
        for a, n in zip(tabela, normal):
            notas[a] += peso * n
    return notas


def pesos_com_foco(pesos, criterio, valor=0.55):
    """Dá mais peso a um critério e divide o resto na mesma proporção de antes."""
    resto = 1 - pesos[criterio]
    return {c: (valor if c == criterio else p * (1 - valor) / resto) for c, p in pesos.items()}
