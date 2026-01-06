# Dashboard de análise de teste estático

Dashboard que fornece interface gráfica interativa para análise de dados
de empuxo de motores foguete. Basta entrar com um arquivo `wsv` (valores
separados por espaços) como o `teste-tyto.txt` de exemplo do repositório.

O arquivo tem a primeira coluna como tempo e a segunda como valor medido
na célula de carga e a tara é aplicada usando parâmetros passados.

## Instalação
Todas as dependências do projeto estão inclusas em:
```bash
pip install streamlit[charts]
```

## Execução local
Tendo as dependências instaladas, para rodar o app basta executar:
```bash
streamlit run app.py
```

## Calibrações diferentes
No momento, a equação de calibração está fixa na linha 7 do script
`stats.py`. Para outras calibrações é necessário calibrar manualmente,
mas será futuramente parametrizada.