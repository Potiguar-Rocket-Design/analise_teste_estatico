import streamlit as st
from plotly import express as px, figure_factory as ff
import pandas as pd
import numpy as np
from plotly import graph_objects as go

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
    if cel == 'Pequena':
        full_fig = px.line(x=full_data[:, 0], y=full_data[:, 1], markers=True, title=file.name, template='plotly_dark')
    else:
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

# curva teórica (opcional)
# ------------------------
ref_file = st.file_uploader(
        'Curva teórica (opcional): `.txt`, `.csv` ou `.wsv` com duas colunas '
        '(tempo [s] e empuxo [N]) separadas por espaço.',
        type=['csv', 'txt', 'wsv'], key='curva_teorica')

ref_data = None
if ref_file is not None:
    try:
        df_ref = formatar_txt(ref_file)  # DataFrame com tempo e valor
        if df_ref.shape[1] < 2:
            raise ValueError('O arquivo precisa ter ao menos duas colunas.')
        # array [tempo, empuxo], mesmo formato usado nas funções de estatística
        ref_data = df_ref.iloc[:, :2].to_numpy(dtype=float)
    except (ValueError, TypeError) as e:
        st.error(f'Não foi possível ler a curva teórica: {e}')
        ref_data = None

# cópia dos dados experimentais para o gráfico (estatísticas usam `data` original)
data_plot = data.copy()
if ref_data is not None:
    alinhar = st.checkbox('Alinhar início da curva experimental em t = 0 s', value=True)
    if alinhar:
        data_plot[:, 0] = data_plot[:, 0] - data_plot[0, 0]

col1, col2 = st.columns([60,40])
with col1:
    fig = px.line(x=data_plot[:, 0], y=data_plot[:, 1], markers=True, title=f'Curva de empuxo {name}', template='plotly_dark')
    fig.update_traces(name='Experimental', showlegend=True)
    if ref_data is not None:
        fig.add_trace(go.Scatter(
                x=ref_data[:, 0], y=ref_data[:, 1],
                mode='lines+markers', name='Teórica',
                line=dict(dash='dash'),
        ))
    fig.update_layout(xaxis_title='Tempo [s]', yaxis_title='Empuxo [N]',
                      legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
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
                'modeBarButtonsToRemove': ['lasso2d', 'select', 'pan', 'autoScale'],
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


# comparação teórico x experimental
# ---------------------------------
if ref_data is not None:
    st.header('Comparação: teórico x experimental', divider=True)

    def _metricas(d):
        return [
            impulso_total(d),
            empuxo_medio(d),
            empuxo_maximo(d),
            tempo_queima(d),
            tempo_pico(d),
        ]

    nomes = ['Impulso total [Ns]', 'Empuxo médio [N]', 'Empuxo máximo [N]',
             'Tempo de queima [ms]', 'Tempo até o pico [ms]']
    m_teo = _metricas(ref_data)
    m_exp = _metricas(data)
    df_comp = pd.DataFrame({
        'Variável': nomes,
        'Teórico': [f'{v:.3f}' for v in m_teo],
        'Experimental': [f'{v:.3f}' for v in m_exp],
        'Diferença [%]': [
            f'{(e - t) / t * 100:+.2f}' if t != 0 else '—'
            for t, e in zip(m_teo, m_exp)
        ],
    })
    st.dataframe(df_comp, hide_index=True, use_container_width=True)
    st.caption('Diferença percentual em relação à curva teórica: (experimental − teórico) / teórico.')