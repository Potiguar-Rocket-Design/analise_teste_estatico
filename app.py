import streamlit as st
from plotly import express as px, figure_factory as ff
import pandas as pd

from stats import *


# cabeçalho
# ---------
st.logo('Logo - PRD.png')
st.set_page_config(page_title='PRD: Análise de dados de teste estático', layout='centered', page_icon='Logo - PRD.png')
st.image('elet.jpg')
st.header('Sistema de análise de dados de teste estático')
st.subheader('Potiguar Rocket Design', divider=True)

with st.sidebar:
    st.image('analise_de_dados.jpg')

cel = st.selectbox('Selecione a célula de carga', ['Grande', 'Pequena'])

# upload de arquivo
# -----------------
uploaded_files = st.file_uploader(
        'Faça upload dos dados.'
        ' O arquivo precisa ser um `.csv`, `.txt` ou `.wsv` com valores separados por espaço "` `".',
        accept_multiple_files=True, type=['csv', 'txt', 'wsv'])

if isinstance(uploaded_files, list):
    file_name = st.selectbox('Selecione arquivo', map(lambda f: f.name, uploaded_files))
    if file_name is None:
        file = None
    else:
        file = list(filter(lambda f: f.name == file_name, uploaded_files))[0]
else:
    file = uploaded_files

if file is None:
    st.stop()  # aguarda arquivo


# leitura de arquivo
# ------------------
full_data = np.loadtxt(file, delimiter=' ')
with st.expander('Visualizar arquivo'):
    st.write(full_data)


# seleção de intervalo
# --------------------
with st.expander('Selecione os dados', expanded=True):
    st.header('Utilize o botão "Box Select" para selecionar a queima na imagem.')
    st.text('Utilize os botões "Zoom", "Pan" e "Reset Axis" para auxiliar na navegação.')
    full_fig = px.line(x=full_data[:, 0], y=-full_data[:, 1], markers=True, title=file.name, template='plotly_dark')
    full_fig.update_layout(xaxis_title='Tempo', yaxis_title='Empuxo')

    selection_event = st.plotly_chart(
            full_fig,
            on_select='rerun',
            config={
                'modeBarButtonsToRemove': ['lasso2d', 'toImage']
            },
            theme=None
    )
    # st.write(event)
    selected_indices = selection_event['selection']['point_indices']

    if len(selected_indices) < 2:
        st.stop()  # wait for input

    min_index = selected_indices[0]
    max_index = selected_indices[-1]
    st.metric('Intervalo de índices selecionado:', f'[{min_index}, {max_index}]')


# extração de dados
# -----------------
if cel == 'Pequena':
    data = calibrar_curva_cel_pequena(full_data[min_index:max_index, :])
else:
    data = calibrar_curva_cel_grande(full_data[min_index:max_index, :])
data_dict = {
    "Variável": [
        "Impulso total",
        "Empuxo médio",
        "Empuxo máximo",
        "Tempo de queima",
        "Tempo até o pico",
        "Classe do motor"
    ],
    "Valor": [
        f"{impulso_total(data):.3f} Ns",
        f"{empuxo_medio(data):.3f} N",
        f"{empuxo_maximo(data):.3f} N",
        f"{tempo_queima(data):.0f} ms",
        f"{tempo_pico(data):.0f} ms",
        classe_motor(impulso_total(data)),
    ]
}


# exibição dos dados
# ------------------
st.header('Dados do teste estático', divider=True)
name = st.text_input('Nome do teste:', value=file.name)

col1, col2 = st.columns([60,40])
with col1:
    fig = px.line(x=data[:, 0], y=data[:, 1], markers=True, title=f'Curva de empuxo {name}', template='plotly_dark')
    fig.update_layout(xaxis_title='Tempo [s]', yaxis_title='Empuxo [N]')
    st.plotly_chart(fig, config={
        'modeBarButtonsToRemove': ['lasso2d', 'select', 'pan', 'zoomIn', 'zoomOut', 'autoScale'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': f'curva_empuxo_{name}',
            'width': 600,
            'height': 500,
            'template': 'plotly',
        }
    }, theme=None)
with col2:
    df_stats = pd.DataFrame(
            data_dict
    )
    fig_table = ff.create_table(df_stats)
    st.plotly_chart(
            fig_table,
            config={
                'modeBarButtonsToRemove': ['lasso2d', 'select', 'pan', 'zoom', 'zoomIn', 'zoomOut', 'autoScale'],
                # 'staticPlot': True,
                'scrollZoom': False,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'tabela_teste_estatico_{name}',
                }
            },
            theme=None,
    )
    st.text('Clique em "📷 Download plot as a PNG" para realizar download do gráfico ou da tabela.')
