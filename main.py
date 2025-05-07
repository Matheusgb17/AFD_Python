import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from collections import deque

# Estrutura do AFD
class Afd:
    # Construtor
    def __init__(self, estados, alfabeto, estado_inicial, estados_finais):
        self.estados = estados
        self.alfabeto = alfabeto
        self.func_transicao = {}
        self.estado_inicial = estado_inicial
        self.estados_finais = estados_finais

    # Permite ao usuário criar na hora o AFD
    def configurarAFD(self):
        estados = input("Informe o conjunto de estados (q0 q1 q2 ...): ").split()
        alfabeto = input("Informe o alfabeto de entrada (a b ...): ").split()
        estado_inicial = input("Informe o estado inicial: ").strip()
        estados_finais = input("Informe o conjunto de estados finais (q0 q1 ...): ").split()

        afd1 = Afd(estados, alfabeto, estado_inicial, estados_finais)

        print("\nDefina a função de transição:")
        for estado in afd1.estados:
            for simbolo in afd1.alfabeto:
                print(f"De {estado} lendo '{simbolo}': ", end="")
                proximo_estado = input().strip()
                if proximo_estado == ".":
                    afd1.func_transicao[(estado, simbolo)] = None
                else:
                    afd1.func_transicao[(estado, simbolo)] = proximo_estado

        return afd1

    # Salva afd no formato xml utilizado no jflap
    def salvarAFD(self, nome_arquivo):
        estrutura = ET.Element("structure")
        ET.SubElement(estrutura, "type").text = "fa"
        afd_element = ET.SubElement(estrutura, "automaton")

        identificadores = {estado: str(i) for i, estado in enumerate(self.estados)}

        for estado in self.estados:
            estado_element = ET.SubElement(afd_element, "state", id=identificadores[estado], name=estado)
            ET.SubElement(estado_element, "x").text = "100" # coordenadas fixas para os estados
            ET.SubElement(estado_element, "y").text = "100"

            if estado == self.estado_inicial:
                ET.SubElement(estado_element, "initial")
            if estado in self.estados_finais:
                ET.SubElement(estado_element, "final")

        for (estado, simbolo), destino in self.func_transicao.items():
            if destino is None:
                continue
            transicao_element = ET.SubElement(afd_element, "transition")
            ET.SubElement(transicao_element, "from").text = identificadores[estado]
            ET.SubElement(transicao_element, "to").text = identificadores[destino]
            ET.SubElement(transicao_element, "read").text = simbolo if simbolo != "" else ""

        xml_str = minidom.parseString(ET.tostring(estrutura, encoding='utf-8'))
        with open(f"data/{nome_arquivo}", "w", encoding="utf-8") as f:
            f.write(xml_str.toprettyxml(indent="  "))

    # Lê arquivos xml para jflap
    @classmethod
    def carregarAFD(cls, nome_arquivo):
        arvore = ET.parse(nome_arquivo)
        raiz = arvore.getroot()
        automato = raiz.find("automaton")

        estados = []
        estado_inicial = None
        estados_finais = []
        id_para_nome = {}

        # Lê os estados
        for estado in automato.findall("state"):
            nome = estado.attrib["name"]
            id_estado = estado.attrib["id"]
            id_para_nome[id_estado] = nome
            estados.append(nome)

            if estado.find("initial") is not None:
                estado_inicial = nome
            if estado.find("final") is not None:
                estados_finais.append(nome)

        # Alfabeto e função de transição
        alfabeto = set()
        func_transicao = {}

        for transicao in automato.findall("transition"):
            origem = id_para_nome[transicao.find("from").text]
            destino = id_para_nome[transicao.find("to").text]
            simbolo_elem = transicao.find("read")
            simbolo = simbolo_elem.text if simbolo_elem is not None else ""
            alfabeto.add(simbolo) # verifica simbolos usados e adiciona ao alfabeto
            func_transicao[(origem, simbolo)] = destino

        afd = cls(estados, list(alfabeto), estado_inicial, estados_finais)
        afd.func_transicao = func_transicao

        return afd

    # Printa a estrutura do AFD
    def printaAFD(self):
        print("Estados         :", self.estados)
        print("Alfabeto        :", self.alfabeto)
        print("Estado inicial  :", self.estado_inicial)
        print("Estados finais  :", self.estados_finais)

        print("Função de transição:")
        for chave, valor in self.func_transicao.items():
            print(f"{chave} -> {valor}")

    # Executa o AFD com uma cadeia
    def testarAFD(self, cadeia):
        estado_atual = self.estado_inicial

        for simbolo in cadeia:
            print(f"\nEstado atual   : {estado_atual}")
            print(f"Entrada atual  : {simbolo}")

            if (estado_atual, simbolo) not in self.func_transicao:
                print("Não há transição definida. Cadeia não reconhecida.")
                return False

            estado_atual = self.func_transicao[(estado_atual, simbolo)]

            if estado_atual is None:
                print("Transição inválida. Cadeia não reconhecida.")
                return False

        return estado_atual in self.estados_finais

    # verifica estados alcançáveis
    def buscaProfundidade(self, estado, visitados):
        if visitados[estado]:
            return
        visitados[estado] = True
        for simbolo in self.alfabeto:
            proximo = self.func_transicao.get((estado, simbolo))
            if proximo and not visitados[proximo]:
                self.buscaProfundidade(proximo, visitados)

    # Faz a verificação dos nós alcançáveis
    def verificarConexao(self):
        visitados = {estado: False for estado in self.estados}
        self.buscaProfundidade(self.estado_inicial, visitados)
        return visitados

    # Faz a remoção dos estados desconexos
    def removeDesconexos(self):
        visitados = self.verificarConexao()

        # Mantém apenas os estados visitados
        estados_acessiveis = [estado for estado, acessivel in visitados.items() if acessivel]
        func_transicao_filtrada = {
            (estado, simbolo): destino
            for (estado, simbolo), destino in self.func_transicao.items()
            if estado in estados_acessiveis and destino in estados_acessiveis
        }
        estados_finais_filtrados = [estado for estado in self.estados_finais if estado in estados_acessiveis]

        # Atualiza o AFD
        self.estados = estados_acessiveis
        self.func_transicao = func_transicao_filtrada
        self.estados_finais = estados_finais_filtrados

    # Busca em profundidade para verificação de conexao do AFD
    def buscaEstadosEquivalentes(self):
        estados = self.estados
        n = len(estados)
        tabela = {}

        # Inicializa a tabela de distinção
        for i in range(n):
            for j in range(i):
                e1, e2 = estados[i], estados[j]

                # Marca como distinguível se apenas um é final
                distinguivel = (e1 in self.estados_finais) != (e2 in self.estados_finais)
                tabela[(e1, e2)] = distinguivel

        alterado = True
        while alterado:
            alterado = False
            for i in range(n):
                for j in range(i):
                    e1, e2 = estados[i], estados[j]
                    if tabela[(e1, e2)]:
                        continue
                    for simbolo in self.alfabeto:
                        d1 = self.func_transicao.get((e1, simbolo))
                        d2 = self.func_transicao.get((e2, simbolo))
                        if d1 == d2:
                            continue
                        par = tuple(sorted((d1, d2)))
                        if d1 is None or d2 is None or tabela.get(par, False):
                            tabela[(e1, e2)] = True
                            alterado = True
                            break

        # Retorna pares equivalentes
        equivalentes = [(e1, e2) for (e1, e2), marcados in tabela.items() if not marcados]
        return equivalentes

    # Retorna um novo AFD resultado da união entre os AFDs
    def uniao(self, outro):
        if set(self.alfabeto) != set(outro.alfabeto):
            raise ValueError("Os AFDs devem ter o mesmo alfabeto.")

        novo_alfabeto = self.alfabeto
        novo_estados = []
        nova_func_transicao = {}
        novos_finais = []

        for e1 in self.estados:
            for e2 in outro.estados:
                novo_estado = (e1, e2)
                novo_estados.append(novo_estado)

                for simbolo in novo_alfabeto:
                    d1 = self.func_transicao.get((e1, simbolo))
                    d2 = outro.func_transicao.get((e2, simbolo))
                    if d1 is not None and d2 is not None:
                        nova_func_transicao[(novo_estado, simbolo)] = (d1, d2)

                # Finais se ao menos um é final
                if e1 in self.estados_finais or e2 in outro.estados_finais:
                    novos_finais.append(novo_estado)

        afd_resultado = Afd(
            estados=novo_estados,
            alfabeto=novo_alfabeto,
            estado_inicial=(self.estado_inicial, outro.estado_inicial),
            estados_finais=novos_finais
        )

        afd_resultado.func_transicao = nova_func_transicao
        return afd_resultado

    # Retorna um novo AFD resultado da intersecao entre os AFDs
    def intersecao(self, outro):
        if set(self.alfabeto) != set(outro.alfabeto):
            raise ValueError("Os AFDs devem ter o mesmo alfabeto.")

        novo_alfabeto = self.alfabeto
        novo_estados = []
        nova_func_transicao = {}
        novos_finais = []

        for e1 in self.estados:
            for e2 in outro.estados:
                novo_estado = (e1, e2)
                novo_estados.append(novo_estado)

                for simbolo in novo_alfabeto:
                    d1 = self.func_transicao.get((e1, simbolo))
                    d2 = outro.func_transicao.get((e2, simbolo))
                    if d1 is not None and d2 is not None:
                        nova_func_transicao[(novo_estado, simbolo)] = (d1, d2)

                # Estado final na interseção: ambos precisam ser finais
                if e1 in self.estados_finais and e2 in outro.estados_finais:
                    novos_finais.append(novo_estado)

        afd_resultado = Afd(
            estados=novo_estados,
            alfabeto=novo_alfabeto,
            estado_inicial=(self.estado_inicial, outro.estado_inicial),
            estados_finais=novos_finais
        )

        afd_resultado.func_transicao = nova_func_transicao
        return afd_resultado

    # Retorna um novo AFD complemento ao AFD utilizado
    def complemento(afd):
        # Verifica se o AFD é completo; se não for, completa com um estado de erro
        estado_erro = "ERRO"
        novo_func_transicao = afd.func_transicao.copy()
        novos_estados = set(afd.estados)

        # Se alguma transição estiver faltando, adiciona transição para o estado de erro
        for estado in afd.estados:
            for simbolo in afd.alfabeto:
                if (estado, simbolo) not in novo_func_transicao:
                    novo_func_transicao[(estado, simbolo)] = estado_erro

        # O estado de erro precisa ser fechado (todas as transições levam a ele mesmo)
        for simbolo in afd.alfabeto:
            novo_func_transicao[(estado_erro, simbolo)] = estado_erro
        novos_estados.add(estado_erro)

        # Inverte os estados finais
        novos_estados_finais = [estado for estado in novos_estados if estado not in afd.estados_finais]

        # Cria o novo AFD com o complemento
        complemento = Afd(
            estados = list(novos_estados),
            alfabeto = afd.alfabeto,
            estado_inicial = afd.estado_inicial,
            estados_finais = novos_estados_finais
        )
        complemento.func_transicao = novo_func_transicao

        return complemento

    # Retorna um novo AFD da diferença entre os AFDs
    def diferenca(self, outro):
        if set(self.alfabeto) != set(outro.alfabeto):
            raise ValueError("Os AFDs devem ter o mesmo alfabeto.")

        complemento_outro = outro.complemento()
        return self.intersecao(complemento_outro)

    # Remove estados desnecessários (retorna novo AFD minimizado)
    def minimizar(self):
        # Remove estados não alcançáveis
        self.removeDesconexos()

        # Encontra estados equivalentes
        equivalentes = self.buscaEstadosEquivalentes()

        # Mapeia estados para seus representantes (merge de equivalentes)
        representante = {estado: estado for estado in self.estados}
        for e1, e2 in equivalentes:
            rep = min(e1, e2)  # Pode usar heurística diferente se quiser
            representante[e1] = rep
            representante[e2] = rep

        # Reconstroi conjuntos de estados e transições
        novos_estados = set(representante.values())
        novo_estado_inicial = representante[self.estado_inicial]
        novos_estados_finais = list({representante[e] for e in self.estados_finais})

        nova_func_transicao = {}
        for (estado, simbolo), destino in self.func_transicao.items():
            r_origem = representante[estado]
            r_destino = representante[destino]
            nova_func_transicao[(r_origem, simbolo)] = r_destino

        # Atualiza AFD com os valores minimizados
        self.estados = list(novos_estados)
        self.estado_inicial = novo_estado_inicial
        self.estados_finais = novos_estados_finais
        self.func_transicao = nova_func_transicao

        return self

    # Verifica se dois AFD reconhecem as mesmas linguagens
    def verificarEquivalencia(self, outro):
        # Verifica se os alfabetos são os mesmos
        if set(self.alfabeto) != set(outro.alfabeto):
            return False

        # Verifica se os estados iniciais são os mesmos
        if self.estado_inicial != outro.estado_inicial:
            return False

        # Verifica se os estados finais são os mesmos
        if set(self.estados_finais) != set(outro.estados_finais):
            return False

        # Compara as transições
        for estado in self.estados:
            for simbolo in self.alfabeto:
                destino1 = self.func_transicao.get((estado, simbolo))
                destino2 = outro.func_transicao.get((estado, simbolo))

                # Se uma transição está definida em um AFD e não no outro, ou se as transições não coincidem
                if destino1 != destino2:
                    return False

        return True


# MAIN

afd1 = Afd(estados=[], alfabeto=[], estado_inicial=None, estados_finais=[])
afd2 = Afd(estados=[], alfabeto=[], estado_inicial=None, estados_finais=[])
afdAux = Afd(estados=[], alfabeto=[], estado_inicial=None, estados_finais=[])

nome_arquivo = "sem nome"
nome_aux = ""

# Menu inicial
while 1:
    if not afd1.estados:
        print("Sem arquivos carregados ...\n")
        choice = input(
            "0 - Sair\n"
            "1 - Configurar AFD\n"
            "2 - Importar AFD\n"
            "=> ")
    else:
        print(f"Arquivo {nome_arquivo} carregado ...\n")
        choice = input(
            "0 - Sair\n"
            "1 - Configurar AFD\n"
            "2 - Importar AFD\n"
            "3 - salvar AFD\n"
            "4 - Remover estados inacessíveis AFD\n"
            "5 - Calcular estados equivalentes AFD\n"
            "6 - Testar equivalência entre dois AFDs\n"
            "7 - Complemento do AFD\n"
            "8 - Minimizar AFD\n"
            "9 - Operações com AFDs\n"
            
            "\n10 - Testar AFDs"
            "=> ")

    # SAIR
    if choice == "0": # SAIR
        break

    # CONFIGURAR
    elif choice == "1":
        print("Configurando AFD...")
        afd2 = afd2.configurarAFD()

    # IMPORTAR
    elif choice == "2":
        nome_arquivo = input("Indique o caminho do arquivo (ex: data/arq.jff): ")
        afd1 = Afd.carregarAFD(nome_arquivo)

        print("\nAFD importado com sucesso:")
        afd1.printaAFD()

    # SALVAR
    elif choice == "3":
        nome_arquivo = input("Escolha um nome para o arquivo: ")
        afd1.salvarAFD(nome_arquivo)
        print(f"Arquivo salvo como '{nome_arquivo}'...")

    # REMOVER ESTADOS INACESSIVEIS
    elif choice == "4":
        afd1.removeDesconexos()
        afd1.printaAFD()

    # CALCULAR ESTADOS EQUIVALENTES
    elif choice == "5":
        print(f"Estados equivalentes:\n {afd1.buscaEstadosEquivalentes()}")

    # TESTAR EQUIVALENCIA ENTRE AFDs $
    elif choice == "6":
        if not afd2.estados:
            choice = input("\n1 - Importar novo AFD\n2 - Configurar novo AFD\n=> ")
            if choice == "1":
                nome_aux = input("Insira o nome do arquivo: ")
            else:
                print("Criando AFD para comparação")
                afd2 = afd2.configurarAFD()
        else:
            print("Deseja utilizar esse AFD já carregado?")
            afd2.printaAFD()

            choice = input("\n1 - Sim\n2 - Não\n=> ")
            if choice == "2":
                choice = input("\n1 - Importar novo AFD\n2 - Configurar novo AFD\n=> ")
                if choice == "1":
                    nome_aux = input("Insira o nome do arquivo: ")
                    afd2.carregarAFD(nome_aux)
                else:
                    print("Criando AFD para comparação")
                    afd2 = afd2.configurarAFD()

        print("Equivalentes..." if afd1.verificarEquivalencia(afd2) else "Não Equivalentes...")

    # Complemento do AFD
    elif choice == "7":
        print("Complemento do AFD: ")
        afdAux = afd1.complemento()
        afd1.printaAFD()

        choice = input("Deseja salvar esse AFD?\n"
                       "1 - Sim\n"
                       "2 - Não\n"
                       "=> ")
        if choice == "1":
            afdAux.salvarAFD(input("Nome ou caminho do arquivo: "))

    # Minimizar AFD
    elif choice == "8":
        afdAux = afd1.minimizar()

        print("Afd1 - Original: ")
        afd1.printaAFD()

        print("\nAfdAux - Afd1 Minimizado: ")
        afdAux.printaAFD()

    # OPERAÇÕES ENTRE AFDs
    elif choice == "9":
        if not afd2.estados:
            choice = input("\n1 - Importar novo AFD\n2 - Configurar novo AFD\n=> ")
            if choice == "1":
                nome_aux = input("Insira o nome do arquivo: ")
            else:
                print("Criando AFD para comparação")
                afd2 = afd2.configurarAFD()
        else:
            print("Deseja utilizar esse AFD já carregado?")
            afd2.printaAFD()

            choice = input("\n1 - Sim\n2 - Não\n=> ")
            if choice == "2":
                choice = input("\n1 - Importar novo AFD\n2 - Configurar novo AFD\n=> ")
                if choice == "1":
                    nome_aux = input("Insira o nome do arquivo: ")
                    afd2.carregarAFD(nome_aux)
                else:
                    print("Criando AFD para comparação")
                    afd2 = afd2.configurarAFD()

        choice = input("Escolha uma operação:"
                       "0 - Voltar\n"
                       "1 - União\n"
                       "2 - Interseção\n"
                       "3 - Diferença\n"
                       "=> ")

        if choice == "1":
            afdAux = afd1.uniao(afd2)
            print("AFD resultante: ")
            afdAux.printaAFD()

        elif choice == "2":
            afdAux = afd1.intersecao(afd2)
            print("AFD resultante: ")
            afdAux.printaAFD()

        elif choice == "3":
            afdAux = afd1.diferenca(afd2)
            print("AFD resultante: ")
            afdAux.printaAFD()

    # TESTAR AFD
    elif choice == "10":
        choice = input("Qual afd deseja testar?\n"
                       "1 - Afd1 (padrão)\n"
                       "2 - Afd2\n"
                       "3 - AfdAux\n"
                       "4 - Mostrar AFDs carregados\n"
                       "=> ")

        if choice == "1":
            print("Cadeia Reconhecida..." if afd1.testarAFD(input("Insira a cadeia que deseja verificar: ")) else "Cadeia inválida...")

        elif choice == "2":
            print("Cadeia Reconhecida..." if afd2.testarAFD(input("Insira a cadeia que deseja verificar: ")) else "Cadeia inválida...")

        elif choice == "3":
            print("Cadeia Reconhecida..." if afdAux.testarAFD(input("Insira a cadeia que deseja verificar: ")) else "Cadeia inválida...")

        elif choice == "4":
            print("\nAfd1: ")
            afd1.printaAFD()

            print("\nAfd2: ")
            afd1.printaAFD()

            print("\nAfdAux: ")
            afd1.printaAFD()

    else:
        exit(1)

    input("Pressione Enter para continuar...")

# Salvar
if afd1.estados:
    afd1.printaAFD()
    choice = input("\nDeseja salvar o arquivo Afd1? 1 - Sim / 2 - Não : ")
    if choice == "1":
        afd1.salvarAFD(input("Nome do arquivo: "))

if afd2.estados:
    afd2.printaAFD()
    choice = input("\nDeseja salvar o arquivo Afd2? 1 - Sim / 2 - Não : ")
    if choice == "1":
        afd1.salvarAFD(input("Nome do arquivo: "))

if afdAux.estados:
    afdAux.printaAFD()
    choice = input("\nDeseja salvar o arquivo AfdAux? 1 - Sim / 2 - Não : ")
    if choice == "1":
        afd1.salvarAFD(input("Nome do arquivo: "))
