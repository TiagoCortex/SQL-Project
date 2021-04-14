import sqlite3
import requests
from matplotlib.pyplot import *


# Primeira parte-----------------------------------------------------------------------------------------
# Criar a base de dados e as tabelas que nela vao existir

def criar_tabela_ensaios(nomeBD):
    """Funcao auxiliar da funcao fCriarTabelas. Dada uma base de dados cujo nome e nomeBD
       cria nesta uma tabela, de nome 'Ensaios',  onde sera armazenada informacao sobre os ensaios
       realizados as vigas do armazem."""
    bd = sqlite3.connect(nomeBD)
    c = bd.cursor()
    command = "CREATE TABLE Ensaios (identificador_viga VARCHAR(5), carga INTEGER, deflexao REAL, \
    PRIMARY KEY (identificador_viga, carga, deflexao))"
    try:
        c.execute(command)
        bd.commit()
    except sqlite3.Error as error:
        print('Could not create table: {}'.format(error))
    bd.close()


def criar_tabela_vigas(nomeBD):
    """Funcao auxiliar da funcao fCriarTabelas. Dada uma base de dados cujo nome e nomeBD
       cria nesta uma tabela, de nome 'Vigas', onde sera armazenada informacao sobre
       as vigas do armazem."""
    bd = sqlite3.connect(nomeBD)
    c = bd.cursor()
    command = "CREATE TABLE Vigas (identificador_viga VARCHAR(5), identificador_material TEXT, quantidade INTEGER, \
    comprimento REAL, seccao_a INTEGER, seccao_b INTEGER, PRIMARY KEY (identificador_viga))"
    try:
        c.execute(command)
        bd.commit()
    except sqlite3.Error as error:
        print('Could not create table: {}'.format(error))
    bd.close()


def fCriarTabelas(nomeBD):
    """Dada uma base de dados cujo nome e nomeBD a funcao cria nesta duas tabelas, a tabela ensaios e a
       tabela vigas anteriormente referidas."""
    criar_tabela_ensaios(nomeBD)
    criar_tabela_vigas(nomeBD)





# Segunda parte------------------------------------------------------------------------
# Extrair informacao de sites e colocar a mesma nas tabelas da base de dados

def request_data(URL):
    """Funcao auxiliar da funcao obter_informacao. Esta funcao tem como objetivo extrair
       a informacao presente no site com o URL dado e guarda-la numa string."""
    data = requests.get(URL)
    if data.ok:
        return data.text


def obter_informacao_url(URL):
    """Funcao auxiliar da funcao das funcoes carregar_tabelas_*. Esta funcao pretende extrair a informacao
       do site do URL dado e tratar a mesma de modo a que possa ser inserida nas tabelas anteriormente criadas."""
    data = request_data(URL)
    linhas = data.split("\n")
    linhas.remove(linhas[-1])       # Remover a linha em branco
    linhas.remove(linhas[4])        # Remover a linha que nao tem dados

    informacao_viga = []                # Informacao da viga, ou seja, o que é constante para todos os ensaios
    for linha in linhas[0:3]:           # Obter a informacao para colocar na lista informacao_viga
        informacao_viga.append(linha)
    dimensoes = linhas[3].split(",")
    for valor in dimensoes:
        informacao_viga.append(valor)

    informacao_ensaios = []    # Informacao_ensaios tem os dados obtidos dos ensaios realizados as vigas
    informacao_ensaios.append(linhas[0])           # Obter a informacao para colocar na lista informacao_ensaios
    for linha in linhas[4:]:
        data = linha.split(":")
        informacao_ensaios.append(data)
    return informacao_viga, informacao_ensaios


def carregar_tabela_ensaios(nomeBD, n, URL_DIR):
    """Funcao auxiliar da funcao fCarregarTabelas. Esta funcao tem como objetivo inserir informacao vinda de
       varios sites (n) da diretoria URL_DIR na tabela 'Ensaios'. Essa informacao e extraida e tratada atraves
       da funcao obter_informacao_url e posteriormente a parte da informacao correspondente aos ensaios e
       colocada nas respetivas colunas da tabela 'Ensaios'."""
    bd = sqlite3.connect(nomeBD)
    c = bd.cursor()
    num = int(n)
    for numero in range(1, num + 1):
        URL = str(URL_DIR) + 'ensaio_' + str(numero) + '.txt'
        ensaios = (obter_informacao_url(URL))[1]
        command = "INSERT INTO Ensaios VALUES (?, ?, ?);"
        for i in range(len(ensaios) - 1):
            try:
                c.execute(command, [ensaios[0], ensaios[i + 1][0], ensaios[i + 1][1]])
                                  # [codigo_viga, carga de cada ensaio, deflexao de cada ensaio]
            except sqlite3.Error as error:
                print('Could not insert into table: {}'.format(error))
    bd.commit()
    bd.close()


def carregar_tabela_vigas(nomeBD, n, URL_DIR):
    """Funcao auxiliar da funcao fCarregarTabelas. Esta funcao tem como objetivo inserir informacao vinda de
       varios sites (n) da diretoria URL_DIR na tabela 'Vigas'. Essa informacao e extraida e tratada atraves
       da funcao obter_informacao_url e posteriormente a parte da informacao correspondente aos ensaios e
       colocada nas respetivas colunas da tabela 'Vigas'."""
    bd = sqlite3.connect(nomeBD)
    c = bd.cursor()
    num = int(n)
    for numero in range(1, num + 1):
        URL = str(URL_DIR) + 'ensaio_' + str(numero) + '.txt'
        inf_viga = (obter_informacao_url(URL))[0]
        command = "INSERT INTO Vigas VALUES (?, ?, ?, ?, ?, ?);"
        try:
            c.execute(command, [inf_viga[0], inf_viga[1], inf_viga[2], inf_viga[3], inf_viga[4], inf_viga[5]])
                            # [cod viga, cod material, quantidade, comprimento, seccao_a, seccao_b]
        except sqlite3.Error as error:
            print('Could not insert into table: {}'.format(error))
    bd.commit()
    bd.close


def fCarregarTabelas(nomeBD, n, URL_DIR):
    """Esta funcao tem como objetivo inserir informacao vinda de varios sites (n) da diretoria URL_DIR nas tabelas,
    tal como descrito anteriormente"""
    carregar_tabela_ensaios(nomeBD, n, URL_DIR)
    carregar_tabela_vigas(nomeBD, n, URL_DIR)





# Terceira parte -------------------------------------------------------------------------------------
# Conseguir a aceder/manipular a informacao presente nas tabelas com as funcionalidades do sqlite

def query(nomeBD, command):
    """Esta funcao tem como objetivo tornar a utilizacao das funcionalidades da biblioteca sqlite mais
       pratica. Dada uma base de dados cujo nome e nomeBD, a funcao executa o comando expresso na string
       command, retornando as informacoes das tabelas que desejamos."""
    bd = sqlite3.connect(nomeBD)
    c = bd.cursor()
    try:
        c.execute(command)
        records = c.fetchall()
    except sqlite3.Error as error:
        print('Could not execute query: {}'.format(error))
        records = None
    bd.close()
    return records


def min_campo_tabela(nomeBD, nome_tabela, nome_campo):
    """Funcao auxiliar da funcao resumoaux. Dada uma base de dados cujo nome e nomeBD, a funcao procura o
       minimo do campo desejado, nome_campo, na tabela em questao, nome_tabela."""
    command = 'SELECT min ({}) FROM {};'.format(nome_campo, nome_tabela)
    return query(nomeBD, command)[0][0]


def max_campo_tabela(nomeBD, nome_tabela, nome_campo):
    """Funcao auxiliar da funcao resumoaux. Dada uma base de dados cujo nome e nomeBD, a funcao procura o
       maximo do campo desejado, nome_campo, na tabela em questao, nome_tabela."""
    command = 'SELECT max ({}) FROM {};'.format(nome_campo, nome_tabela)
    return query(nomeBD, command)[0][0]


def resumoaux(nomeBD, Qmin, Qmax, comp):
    """Funcao auxiliar da funcao fResumo. Procura e devolve as informacoes sao pedidas.
       A informacao e procurada nas tabelas da base de dados nomeBD e devolve as linhas com quantidades entre Qmin
       e Qmax e com um comprimento = comp. No caso de nao se querer especificar uma das condicoes utiliza-se o '*'."""
    qtd_min_abs = min_campo_tabela(nomeBD, 'Vigas', 'quantidade')
    qtd_max_abs = max_campo_tabela(nomeBD, 'Vigas', 'quantidade')
    if Qmin == '*':
        Qmin = qtd_min_abs
    if Qmax == '*':
        Qmax = qtd_max_abs
    condicao1 = ' quantidade >= ' + str(Qmin)
    condicao2 = ' quantidade <= ' + str(Qmax)
    condicao3 = ' comprimento = ' + str(comp)

    if comp == '*':
        command = 'SELECT identificador_viga, identificador_material, quantidade FROM Vigas WHERE' \
            + condicao1 + ' AND ' + condicao2 + ';'
    else:
        command = 'SELECT identificador_viga, identificador_material, quantidade FROM Vigas WHERE' \
            + condicao1 + ' AND ' + condicao2 + ' AND ' + condicao3 + ';'

    return query(nomeBD, command)


def fResumo(nomeBD, fout, resto):
    """Esta funcao tem como objetivo procurar a informacao desejada, tal como foi descrito na funcao resumoaux
       e posteriormente escrever a mesma num ficheiro cujo nome e fout"""
    parametros = resto.split(';')
    info = resumoaux(nomeBD, parametros[0], parametros[1], parametros[2])
    num_vigas = len(info)
    cabecalho = (str(num_vigas) + ' vigas em quantidades entre ' + str(parametros[0]) + ' e ' + str(parametros[1]) \
                + ' com comprimento ' + str(parametros[2]) + ':' + '\n')
    fout.write(cabecalho)
    for linha in info:
        fout.write(str(linha) + '\n')
    fout.write('\n')





# Quarta parte-------------------------------------------------------------------------------
# Utilizar a informacao das tabelas para produzir graficos


def mesmo_material(nomeBD, codigo_material):
    """Funcao auxiliar da funcao pontos_grafico. Esta funcao pretende recolher toda a informacao da tabela vigas e
       tabela ensaios, presentes na base de dados nomeBD, das vigas cujo material tem o identificador codigo_material."""
    command = 'SELECT Ensaios.identificador_viga, Ensaios.deflexao, Ensaios.carga, Vigas.comprimento, \
        Vigas.seccao_a, Vigas.seccao_b FROM Ensaios, Vigas WHERE Ensaios.identificador_viga = Vigas.identificador_viga \
        AND Vigas.identificador_material = "{}" ;'.format(codigo_material)
    return query(nomeBD, command)


def calcular_young(parametros):
    """Funcao auxiliar da funcao pontos_grafico. Esta funcao tem como objetivo fazer o calculo do modulo de
       elasticidade de young obtido experimentalmente em cada ensaio."""
    deflexao = parametros[1]      # Parametros com as respetivas conversoes
    carga = parametros[2]
    comprimento = parametros[3] * 1000  # Converter m em mm
    seccao_a = parametros[4] * 10  # Converter cm em mm
    seccao_b = parametros[5] * 10  # Converter cm em mm
    momento_inercia = (seccao_a * seccao_b**3) / 12
    modulo_elasticidade_young = ((carga * comprimento**3) / (momento_inercia * deflexao * 48))  # Em kN/mm**2
    return modulo_elasticidade_young


def pontos_grafico(nomeBD, codigo_material):
    """Funcao auxiliar da funcao fGrafico. Esta funcao tem como objetivo fazer uma lista de listas com os pontos
       a utilizar nos graficos. Cada sublista da lista contem os pontos dos ensaios feitos na mesma viga. Todas
       as vigas sao feitas do mesmo material, cujo identificador e codigo_material. Os pontos de cada sublista
       sao dados na forma (modolo_young, carga). Cria tambem uma lista com os codigos identificadores das vigas."""
    lista_pontos = [[]]
    lista_ensaios = mesmo_material(nomeBD, codigo_material)
    viga_atual = lista_ensaios[0][0]
    counter_vigas = 0
    for ensaio in lista_ensaios:
        modulo_elasticidade_young = calcular_young(ensaio)
        if ensaio[0] == viga_atual:
            lista_pontos[counter_vigas].append((modulo_elasticidade_young, ensaio[2]))
        else:
            lista_pontos.append([])
            viga_atual = ensaio[0]
            counter_vigas += 1
            lista_pontos[counter_vigas].append((modulo_elasticidade_young, ensaio[2]))
    # Lista de listas onde cada lista contem os pontos a colocar no grafico provenientes de ensaios feitos a mesma viga

    viga_atual = lista_ensaios[0][0]
    lista_vigas = []
    lista_vigas.append(viga_atual)
    for ensaio in lista_ensaios:
        if ensaio[0] != viga_atual:
            lista_vigas.append(ensaio[0])
            viga_atual = ensaio[0]
    # Lista com os codigos das vigas utilizadas
    return lista_pontos, lista_vigas


def media_young(lista_pontos):
    """Funcao auxiliar da funcao fGrafico. Apos calculados todos os valores dos modulos de elasticidade de young
       obtidos experimentalmente nos ensaios feitos para vigas do mesmo material, esta funcao obtem a media destes
       valores. Esta media sera posteriormente utilizada para fazer uma reta no grafico correspondente ao valor da media."""
    counter = 0
    sum_young = 0
    for viga in (lista_pontos):
        for ponto in viga:
            counter += 1
            sum_young += ponto[0]
        media = round(sum_young/counter, 2)
    return media


def calc_x_min(lista_pontos):
    """Funcao auxiliar da funcao fGrafico. Esta funcao pretende descobrir qual e o valor minimo de carga utilizada
       nos ensaios das vigas do mesmo material. Uma vez que a carga corresponde ao eixo das abcissas do grafico,
       calculando este minimo conseguimos saber onde devemos comecar a tracar a reta da media."""
    x_min = lista_pontos[0][0][1]
    for viga in lista_pontos:
        for ponto in viga:
            if ponto[1] <= x_min:
                x_min = ponto[1]
    return x_min


def calc_x_max(lista_pontos):
    """Funcao auxiliar da funcao fGrafico. Esta funcao pretende descobrir qual e o valor maximo de carga utilizada
       nos ensaios das vigas do mesmo material. Uma vez que a carga corresponde ao eixo das abcissas do grafico,
       calculando este maximo conseguimos saber onde devemos acabar a tracar a reta da media."""
    x_max = lista_pontos[0][0][1]
    for viga in lista_pontos:
        for ponto in viga:
            if ponto[1] >= x_max:
                x_max = ponto[1]
    return x_max


def fGrafico (nomeBD, codigo_material):
    """Esta funcao tem como objetivo produzir um grafico com todos os ensaios feitos em vigas do mesmo material,
       cujo o indicador e codigo_material. Neste grafico, nas abcissas estarao os valores das cargas utilizadas
       nos ensaios e nas ordenadas os valores dos respetivos modulos de young calculados. Os pontos terao uma cor
       disinta para cada viga. Este grafico contem tambem uma reta que corresponde a media dos valores dos modulos
       de elasticidade de young destes ensaios."""
    try:
        lista_vigas = (pontos_grafico(nomeBD, codigo_material))[1]
        lista_pontos = (pontos_grafico(nomeBD, codigo_material))[0]
        media = media_young(lista_pontos)
    except:
        print("Este material nao se encontra nas tabelas.")
        return None
    for viga in lista_pontos:
        lista_x = []
        lista_y = []
        for ponto in viga:
            lista_x.append(ponto[1])
            lista_y.append(ponto[0])
        plot(lista_x, lista_y, 'o')
    x_min = calc_x_min(lista_pontos)
    x_max = calc_x_max(lista_pontos)
    y_media = [media] * len(range(x_min, x_max))
    plot(range(x_min, x_max), y_media, '-')
    title("Módulo de Young de " + str(codigo_material) + "=" + str(media) + "kN/mm2")
    ylabel("Valores experimentais do módulo de Young (kN/mm2)")
    xlabel("Cargas usadas (kN)")
    legenda = lista_vigas
    legenda.append('média')
    legend(legenda)
    show()



#---------------------------------------------------------------------------------------------

def young( nomeBD, nomeFichComandos, nomeFichResultados):
    """Esta funcao permite ler os comando presentes num ficheiro de nome nomeFichComandos e interpretar esses mesmos
       comandos de modo a poderem ser executados pelo programa anterior. Os comandos estarao relacionados com a
       manipulacao de dados presentes nas tabelas duma base de dados de nome nomeBD. Apos executados os comandos,
       algumas informacoes serao escritas num ficheiro de nome nomeFichResultados."""
    f = open(nomeFichComandos, 'r')
    fout = open(nomeFichResultados, 'w')
    comandos = f.readlines()
    f.close()
    for linha in comandos:
        aux = linha.strip()
        info = aux.split(' ')

        if info[0] == 'CRIAR_TABELAS':
            fCriarTabelas(nomeBD)
        elif info[0] == 'CARREGAR_ENSAIOS':
            fCarregarTabelas(nomeBD, info[1], info[2])
        elif info[0] == 'RESUMO':
            fResumo(nomeBD, fout, info[1])
        elif info[0] == 'GRAFICO':
            fGrafico(nomeBD, info[1])
        elif linha == '\n' or info[0] == '':
            print('Esta linha esta vazia')
        else:
            print("Comando '" + info[0] + "' desconhecido")
    fout.close()
