import math
import random

nome_arquivo = "Circuito1"

with open(f"./entradas/{nome_arquivo}.txt", "r") as entrada:
    linhas = entrada.readlines()

PONTOS_A_CONTECTAR = int(linhas[0].strip())
CONEXOES = int(linhas[1].strip())
MAX_COMP = int(linhas[2].strip())
X_POS = list(map(float, linhas[3].replace(",", ".").split()))
Y_POS = list(map(float, linhas[4].replace(",", ".").split()))

# aqui temos uma lista com cada componente e sua coordenada X e Y
COMPONENTES_X_Y = list(zip(X_POS, Y_POS))


def calcula_distancia(p1, p2):
    # raiz( (x_p1 - x_p2)^2 + (y_p1 - y_p2)^2 )
    distancia = math.sqrt(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2))
    return distancia


def gerar_pares(componentes):
    n = len(componentes)
    pares = []

    for i in range(n - 1):
        for j in range(i + 1, n):
            pares.append((i, j))

    return pares


# conecta todos e gera conexões aleatórias até fechar a quantidade de conexões
def cria_circuito():
    n = len(COMPONENTES_X_Y)
    pares_possiveis = gerar_pares(COMPONENTES_X_Y)

    if not (CONEXOES >= math.ceil(n / 2)):
        raise ValueError("Erro.")

    if not (CONEXOES <= math.floor(n * MAX_COMP / 2)):
        raise ValueError("Erro.")

    if not (CONEXOES <= len(pares_possiveis)):
        raise ValueError("Erro.")

    componentes = [i for i in range(n)]
    random.shuffle(componentes)
    graus_componentes = [0 for _ in range(n)]

    circuito = []

    # aqui conecta todos uma vez
    for i in range(0, len(componentes) - 1, 2):
        primeiro = componentes[i]
        segundo = componentes[i + 1]
        par_novo = tuple(sorted((primeiro, segundo)))
        circuito.append(par_novo)
        graus_componentes[primeiro] += 1
        graus_componentes[segundo] += 1

    conexoes_existentes = {tuple(sorted(conexao)) for conexao in circuito}

    if len(componentes) % 2 != 0:
        achou = False
        sobrou = componentes[len(componentes) - 1]  # ultimo
        while achou == False:
            candidatos = componentes[: len(componentes) - 1]
            if (not candidatos):
                achou = True
                raise ValueError("Não há candidatos válidos!")
            candidato = random.choice(candidatos)
            par_restante = tuple(sorted((sobrou, candidato)))

            if (
                graus_componentes[sobrou] < MAX_COMP
                and graus_componentes[candidato] < MAX_COMP
                and sobrou != candidato
                and par_restante not in conexoes_existentes
            ):
                achou = True

        circuito.append(par_restante)
        conexoes_existentes.add(par_restante)
        graus_componentes[sobrou] += 1
        graus_componentes[candidato] += 1
        
    while len(circuito) != CONEXOES:
        
        pares_validos = []
        
        for par in pares_possiveis:
            if(par not in conexoes_existentes
                and graus_componentes[par[0]] < MAX_COMP
                and graus_componentes[par[1]] < MAX_COMP
            ):
                pares_validos.append(par)
        
        # se ta vazio
        if(not pares_validos):
            raise ValueError("Não foi possível completar o circuito")
        
        par_escolhido = random.choice(pares_validos)
        
        circuito.append(par_escolhido)
        conexoes_existentes.add(par_escolhido)
        graus_componentes[par_escolhido[0]] += 1
        graus_componentes[par_escolhido[1]] += 1

    if(len(circuito) != CONEXOES):
        raise ValueError(f"Não foi possível fazer um circuito com {CONEXOES} conexões!")

    for i, grau in enumerate(graus_componentes):
        if(grau < 1):
            raise ValueError(f"O componente {i} está sem conexão")
        if(grau > MAX_COMP):
            raise ValueError(f"O componente {i} estourou o número de conexões")

    if(len(circuito) != len(conexoes_existentes)):
        raise ValueError("Erro. Há alguma duplicata!")
    
    return circuito, graus_componentes


# recebe circuito e faz um somatório de todas as distâncias
def calcula_circuito(circuito):
    tamanho_fio = 0
    for primeiro, segundo in circuito:
        p1 = COMPONENTES_X_Y[primeiro]
        p2 = COMPONENTES_X_Y[segundo]
        tamanho_fio += calcula_distancia(p1, p2)

    return tamanho_fio

def vizinhanca(circuito, graus):
    novo_circuito = circuito.copy()
    novos_graus = graus.copy()
    
    conexoes_removiveis = [conexao for conexao in novo_circuito if novos_graus[conexao[0]] > 1 and novos_graus[conexao[1]] > 1]
    if not conexoes_removiveis:
        raise ValueError("A vizinhança não pode ser criada. Nenhuma conexão pode ser removida.")

    removida = random.choice(conexoes_removiveis)
    
    novos_graus[removida[0]] -= 1
    novos_graus[removida[1]] -= 1
    
    novo_circuito.remove(removida)
    conexoes_restantes = set(novo_circuito)
    
    pares_possiveis = gerar_pares(COMPONENTES_X_Y)
    
    if removida in pares_possiveis:
        pares_possiveis.remove(removida)
        
    candidatos = []
    
    for par in pares_possiveis:
        if par not in conexoes_restantes:
            if novos_graus[par[0]] < MAX_COMP and novos_graus[par[1]] < MAX_COMP:
                candidatos.append(par)

    if not candidatos:
        raise ValueError("Não há candidatos para a vizinhança")
    
    escolhido = random.choice(candidatos)
    novo_circuito.append(escolhido)
    novos_graus[escolhido[0]] += 1
    novos_graus[escolhido[1]] += 1
    novo_circuito.sort()
    
    return novo_circuito, novos_graus

def atualiza_melhor(atual, novo, temperatura):
    custo_atual = calcula_circuito(atual[0])
    custo_novo = calcula_circuito(novo[0])
    
    delta_custo = custo_novo - custo_atual
    
    # se o custo é menor ele aceita diretamente
    if(delta_custo < 0):
        melhor_solucao = novo
    # se é pior (maior custo) ou igual, testa a probabilidade
    else:
        chance = math.exp(-delta_custo/temperatura)
        if(random.random() < chance):
            melhor_solucao = novo
        else:
            melhor_solucao = atual
        
    return melhor_solucao


# formatadinho powered by IA.
# eu não queria fazer a tabela na mão e queria ver logo se o algoritimo funcionou! :)
def imprime_solucao(solucao):
    circuito, graus = solucao
    custo = calcula_circuito(circuito)

    print("\n" + "=" * 48)
    print("MELHOR SOLUÇÃO ENCONTRADA")
    print("=" * 48)
    print(f"Componentes: {PONTOS_A_CONTECTAR}")
    print(f"Conexões:    {len(circuito)} de {CONEXOES}")
    print(f"Custo total: {custo:.6f}")
    print("\nConexões:")
    print("-" * 34)
    print(f"{'Conexão':<20}{'Distância':>12}")
    print("-" * 34)

    for primeiro, segundo in sorted(circuito):
        distancia = calcula_distancia(
            COMPONENTES_X_Y[primeiro],
            COMPONENTES_X_Y[segundo],
        )
        print(f"{primeiro + 1:>2} - {segundo + 1:<7}{distancia:>12.6f}")

    print("-" * 34)
    print("Grau de cada componente:")
    for componente, grau in enumerate(graus, start=1):
        print(f"  Componente {componente:>3}: {grau}")
    print("=" * 48)
    
def recozimento_simulado():    
    temperatura = 100
    fator_resfriamento = 0.999
    iteracoes = 100000
    
    solucao_incial = cria_circuito()
    solucao_atual = solucao_incial

    melhor_solucao = solucao_incial

    for _ in range(iteracoes):
        
        solucao_nova = vizinhanca(solucao_atual[0], solucao_atual[1])
                
        # aqui aceita se for melhor
        # e se for pior tem que verificar com a temperatura para ver se aceita!
        
        solucao_atual = atualiza_melhor(solucao_atual, solucao_nova, temperatura)
            # NOTA: melhor_solucao ta empacotado o circuito em [0] e os graus em [1]

        if(calcula_circuito(solucao_atual[0]) < calcula_circuito(melhor_solucao[0])):
            melhor_solucao = solucao_atual
            
        temperatura = temperatura * fator_resfriamento
        
    imprime_solucao(melhor_solucao)

recozimento_simulado()