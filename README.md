# 🤖 Autômato Finito Determinístico (AFD) - Projeto Python

---

### 📘 Descrição do Projeto

Este projeto permite criar, manipular e salvar Autômatos Finitos Determinísticos (AFD), uma importante estrutura em teoria da computação. Com ele, é possível:

- 🛠️ Criar AFDs personalizados a partir de entradas do usuário  
- 💾 Salvar AFDs no formato JFLAP (XML), permitindo a visualização e teste em ferramentas como JFLAP  
- 🔎 Testar AFDs com cadeias de entrada, verificando se são aceitas ou rejeitadas pelo autômato  
- 📉 Minimizar AFDs, removendo estados desnecessários e aplicando algoritmos de equivalência  
- ♻️ Realizar operações de união, interseção, complemento e diferença entre AFDs  
- 📂 Carregar e manipular AFDs a partir de arquivos XML compatíveis com JFLAP  

Este projeto é uma excelente ferramenta de aprendizado e prática para quem está estudando teoria dos autômatos e linguagens formais.

---

## ⚙️ Funcionalidades

- 🧱 **Configuração do AFD**: Defina estados, alfabeto, estado inicial, estados finais e transições interativamente  
- 🧪 **Testar AFD**: Verifique se uma cadeia é aceita pelo AFD  
- 🧹 **Minimização**: Remova estados inacessíveis e aplique minimização  
- ➕ **Operações com AFDs**: União, interseção, complemento e diferença  
- 💽 **Exportação JFLAP**: Salve o AFD em XML compatível com JFLAP  
- 📥 **Importação de XML**: Carregue AFDs de arquivos gerados no JFLAP  

---

## 🚀 Como Usar

### ✅ Requisitos

- Python 3.13.3 
- Bibliotecas: `xml.etree.ElementTree`, `xml.dom.minidom` (nativas do Python)

### 🧾 Passos para rodar

1. Clone ou baixe este repositório  
2. Abra o arquivo `afd.py` no seu editor de código  
3. Execute no terminal:

```bash
python afd.py
