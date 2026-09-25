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
UNIDADE_TEMPO_EXP = 'ms'  # unidade de tempo dos dados experimentais (a mesma usada em tempo_queima/tempo_pico)

ref_file = st.file_uploader(
        'Curva teórica (opcional): '
        '(tempo e empuxo [N]) separadas por espaço.',
        type=['csv', 'txt', 'wsv', 'eng'], key='curva_teorica')

ref_data = None  # curva teórica já convertida para a unidade de tempo do experimento
if ref_file is not None:
    unidade_ref = st.selectbox('Unidade de tempo da curva teórica', ['s', 'ms'], index=0)
    try:
        df_ref = formatar_txt(ref_file)  # DataFrame com tempo e valor
        if df_ref.shape[1] < 2:
            raise ValueError('O arquivo precisa ter ao menos duas colunas.')
        # array [tempo, empuxo], mesmo formato usado nas funções de estatística
        ref_data = df_ref.iloc[:, :2].to_numpy(dtype=float)
        if unidade_ref == 's' and UNIDADE_TEMPO_EXP == 'ms':
            ref_data[:, 0] = ref_data[:, 0] * 1000  # s -> ms
    except (ValueError, TypeError) as e:
        st.error(f'Não foi possível ler a curva teórica: {e}')
        ref_data = None

t_exp, y_exp = data[:, 0].astype(float), data[:, 1].astype(float)
xaxis_title = f'Tempo [{UNIDADE_TEMPO_EXP}]'
yaxis_title = 'Empuxo [N]'

if ref_data is not None:
    t_ref, y_ref = ref_data[:, 0].copy(), ref_data[:, 1].copy()

    col_a, col_b = st.columns(2)
    with col_a:
        alinhar = st.checkbox('Alinhar início da curva experimental em t = 0', value=True)
    with col_b:
        modo_norm = st.selectbox(
                'Normalização das curvas',
                ['Nenhuma', 'Empuxo (pico = 1)', 'Empuxo e tempo (comparar forma)'],
                index=0,
        )

    if alinhar or modo_norm == 'Empuxo e tempo (comparar forma)':
        t_exp = t_exp - t_exp[0]
        t_ref = t_ref - t_ref[0]

    if modo_norm in ('Empuxo (pico = 1)', 'Empuxo e tempo (comparar forma)'):
        y_exp = y_exp / np.nanmax(y_exp)
        y_ref = y_ref / np.nanmax(y_ref)
        yaxis_title = 'Empuxo normalizado'

    if modo_norm == 'Empuxo e tempo (comparar forma)':
        # tempo de 0 a 1: fração da duração de cada queima
        t_exp = t_exp / t_exp[-1] if t_exp[-1] != 0 else t_exp
        t_ref = t_ref / t_ref[-1] if t_ref[-1] != 0 else t_ref
        xaxis_title = 'Tempo normalizado (fração da queima)'

col1, col2 = st.columns([60,40])
with col1:
    fig = px.line(x=t_exp, y=y_exp, markers=True, title=f'Curva de empuxo {name}', template='plotly_dark')
    fig.update_traces(name='Experimental', showlegend=True)
    if ref_data is not None:
        fig.add_trace(go.Scatter(
                x=t_ref, y=y_ref,
                mode='lines+markers', name='Teórica',
                line=dict(dash='dash'),
        ))
    fig.update_layout(xaxis_title=xaxis_title, yaxis_title=yaxis_title,
                      legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
    if ref_data is not None:
        st.plotly_chart(fig, config={
            'modeBarButtonsToRemove': ['lasso2d', 'select', 'pan', 'zoomIn', 'zoomOut', 'autoScale'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': f'curva_empuxo_{name}_comp:{modo_norm}',
                'width': 600,
                'height': 500,
                'template': 'plotly',
            }
        }, theme=None)
    else:
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