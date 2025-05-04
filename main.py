import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from collections import deque

# Estrutura do AFD
class Afd:
    def __init__(self, estados, alfabeto, estado_inicial, estados_finais):
        self.estados = estados
        self.alfabeto = alfabeto
        self.func_transicao = {}
        self.estado_inicial = estado_inicial
        self.estados_finais = estados_finais

    def salvarAFD(self, nome_arquivo):
        estrutura = ET.Element("structure")
        ET.SubElement(estrutura, "type").text = "fa"
        afd_element = ET.SubElement(estrutura, "automaton")

        identificadores = {estado: str(i) for i, estado in enumerate(self.estados)}

        for estado in self.estados:
            estado_element = ET.SubElement(afd_element, "state", id=identificadores[estado], name=estado)
            ET.SubElement(estado_element, "x").text = "100"
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

        xml_str = ET.tostring(estrutura, encoding='utf-8')
        parsed = minidom.parseString(xml_str)
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(parsed.toprettyxml(indent="  "))

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
            alfabeto.add(simbolo)
            func_transicao[(origem, simbolo)] = destino

        afd = cls(estados, list(alfabeto), estado_inicial, estados_finais)
        afd.func_transicao = func_transicao

        return afd

    def buscaProfundidade(self, estado, visitados):
        if visitados[estado]:
            return
        visitados[estado] = True
        for simbolo in self.alfabeto:
            proximo = self.func_transicao.get((estado, simbolo))
            if proximo and not visitados[proximo]:
                self.buscaProfundidade(proximo, visitados)

    def verificarConexao(self):
        visitados = {estado: False for estado in self.estados}
        self.buscaProfundidade(self.estado_inicial, visitados)
        return visitados

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

# Menu inicial
choice = input("1 - Configurar AFD / 2 - Importar AFD: ")

if choice == "1":
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

    print("\nFunção de transição definida:")
    for chave, valor in afd1.func_transicao.items():
        print(f"{chave} -> {valor}")

elif choice == "2":
    afd1 = Afd.carregarAFD("data/afd_xml.jff")
    print("\nAFD importado com sucesso:")
    print("Estados         :", afd1.estados)
    print("Alfabeto        :", afd1.alfabeto)
    print("Estado inicial  :", afd1.estado_inicial)
    print("Estados finais  :", afd1.estados_finais)
    print("Função de transição:")
    for chave, valor in afd1.func_transicao.items():
        print(f"{chave} -> {valor}")
else:
    exit(1)


# Reconhecimento de entrada
entrada = input("\nInforme a cadeia a ser reconhecida: ")
estado_atual = afd1.estado_inicial

for simbolo in entrada:
    print(f"\nEstado atual   : {estado_atual}")
    print(f"Entrada atual  : {simbolo}")

    if (estado_atual, simbolo) not in afd1.func_transicao:
        print("Não há transição definida. Cadeia não reconhecida.")
        estado_atual = None
        break

    estado_atual = afd1.func_transicao[(estado_atual, simbolo)]

    if estado_atual is None:
        print("Transição inválida. Cadeia não reconhecida.")
        break

if estado_atual in afd1.estados_finais:
    print("\nCadeia reconhecida!")
else:
    print("\nCadeia não reconhecida.")

# Salvar
choice = input("\nDeseja salvar o arquivo? 1 - Sim / 2 - Não : ")

if choice == "1":
    afd1.salvarAFD("data/afd_xml.jff")
    print("Arquivo salvo como 'afd_xml.jff'.")
