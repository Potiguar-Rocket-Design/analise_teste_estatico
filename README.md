
# 🚀 Analisador de Dados de Empuxo - Tyto II

Este script realiza a leitura, análise e visualização dos dados de empuxo de um motor-foguete com base em arquivos `.txt` contendo dados de força. Ele permite identificar os principais parâmetros do motor, como impulso total, empuxo médio, pico de empuxo e tempo de queima, além de classificá-lo conforme a tabela padrão de classes de motores.

---

## 📁 Estrutura esperada

- O script deve ser executado na mesma pasta onde está localizado o arquivo `.txt` contendo os dados (por exemplo: `teste1.txt`).
- O arquivo `.txt` deve conter duas colunas separadas por espaço:
  - Primeira coluna: tempo em milissegundos (ms)
  - Segunda coluna: valores brutos de força (inteiros)

Exemplo de linha no arquivo:
```
100 8300
110 8900
...
```

---

## ▶️ Como usar

### 1. **Execute o script**
O script buscará automaticamente o primeiro arquivo `.txt` no diretório (exceto `saidaDeDados.txt`) e carregará os dados para análise.

### 2. **Menu Interativo**
Durante a execução, um menu interativo será exibido no terminal:

```
Digite o comando:
1 - Definir a quantidade de pontos antes do apice
2 - Definir a quantidade de pontos depois do apice
3 - Pré-visualizar gráfico
4 - Visualizar dados do Motor
0 - Encerrar e gerar arquivo com os pontos
```

#### Comandos:

- **1**: Define quantos pontos antes do pico de empuxo devem ser considerados na análise.
- **2**: Define quantos pontos após o pico de empuxo devem ser considerados.
- **3**: Exibe um gráfico de força (N) vs tempo (ms) com base nos parâmetros definidos.
- **4**: Exibe os seguintes dados do motor:
  - Impulso total (Ns)
  - Classe do motor (A, B, C, ...)
  - Empuxo médio (N)
  - Empuxo máximo (N)
  - Tempo total de queima (ms)
  - Tempo até o pico de empuxo (ms)
- **0**: Gera o arquivo `saidaDeDados.txt` com os pontos analisados (tempo e força), prontos para exportação ou análise posterior.

---

## 🧪 Pré-requisitos

Instale as bibliotecas necessárias com:

```bash
pip install numpy pandas matplotlib
```

---

## 📄 Saída

O script gera um arquivo chamado `saidaDeDados.txt` contendo os dados filtrados e tratados (tempo e força após compensações), com os pontos considerados relevantes para análise.

---

## ✨ Exemplo de resultado

```
| Métrica               | Valor     |
|-----------------------|-----------|
| Impulso total (Ns)    | 22.345    |
| Classe do motor       | D         |
| Empuxo médio (N)      | 15.678    |
| Empuxo máximo (N)     | 34.200    |
| Tempo de queima (ms)  | 204       |
| Tempo até o pico (ms) | 93        |
```

---

## 🚀 Créditos

Tyto II - Projeto PRD  
Análise de dados de motores-foguete  
Desenvolvido para análise de testes experimentais com sensores de força.
