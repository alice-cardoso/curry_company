# ====================================================================================================
#               Importando as bibliotecass
# ====================================================================================================

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from PIL import Image
from datetime import datetime


st.set_page_config(page_title="Visão Empresa",
                   page_icon=':chart_with_upwards_trend:', layout='wide')
# =================================================
#                     Funções
# =================================================


def limpa_cod(df1):
    '''
        limpa_cod -> limpeza do código
            1. Remoção dos espaços das variáveis de texto
            2. Mudança do tipo da coluna de dados
            3. Remoção dos dados NaN
            4. Formatação da coluna de datas            
            5. Limpeza da coluna de tempo ( remoção do texto da variável numérica)

            Input: dataframe
            Output: dataframe
    '''
    # Remover espaço da string
    for i in range(len(df1)):
        df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()
        df1.loc[i, 'Delivery_person_ID'] = df1.loc[i,
                                                   'Delivery_person_ID'].strip()

    # Excluir as linhas com a idade dos entregadores vazia
    linhas_vazias = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]

    # Conversao de texto/categoria/string para numeros inteiros
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    # Conversao de texto/categoria/strings para numeros decimais
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(
        float)

    # Conversao de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # Remove as linhas da culuna multiple_deliveries que tenham o conteudo igual a 'NaN '
    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # Remove as linhas da culuna Weatherconditions que tenham o conteudo igual a 'NaN '
    linhas_vazias = df1['Weatherconditions'] != 'conditions NaN'
    df1 = df1.loc[linhas_vazias, :]

    # Remove as linhas da culuna Weatherconditions que tenham o conteudo igual a 'NaN '
    linhas_vazias = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]

    # Comando para remover o texto de números
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:,
                                               'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:,
                                                 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    return (df1)


def metricas_pedido(df1):
    ''' metricas_pedido -> Gera o primeiro gráfico '''
    cols = ['ID', 'Order_Date']
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    return fig


def pedidos_densidade_transito(df1):
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby(
        'Road_traffic_density').count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN", :]
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
    return fig


def pedidos_tipos_cidade(df1):
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(
        ['City', 'Road_traffic_density']).count().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density',
                     size='ID', color='City')
    return fig


def pedido_semana(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby(
        'week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y='ID')
    return fig


def pedido_semana2(df1):
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby(
        'week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby(
        'week_of_year').nunique().reset_index()

    df_aux = pd.merge(df_aux01, df_aux02, how='inner', on='week_of_year')
    df_aux['order_by_deliver'] = df_aux['ID']/df_aux['Delivery_person_ID']

    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    return fig


def country_maps(df1):
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude',
                         'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != 'Nan', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'Nan', :]

    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']],
                      popup=location_info[['City', 'Road_traffic_density']]).add_to(map)

    folium_static(map, width=1024, height=600)

# ====================================================================================================
#               Importando o dataset
# ====================================================================================================


df = pd.read_csv('train.crdownload')
df1 = df.copy()

# ====================================================================================================
#               Limpando o dataset
# ====================================================================================================

df1 = limpa_cod(df1)

# ====================================================================================================
#               Layout - Barra Lateral
# ====================================================================================================

st.header(':blue[Marketplace - Visão Cliente]')

#image_path = r'C:\Users\User\repos_cds\ftc_analisando_dados_com_python\exercicios\logo.png'
#image = Image.open(image_path)
image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('Cury Company')
st.sidebar.markdown('Faster Delivery in Town')
st.sidebar.markdown('''---''')


st.sidebar.markdown('Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY')


st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)
st.sidebar.markdown('''---''')
st.sidebar.markdown(':gray[Powered by Alice Cardoso :balloon:]')

# ====================================================================================================
#                     FILTROS
# ====================================================================================================

# Filtro data
linhas_selecionas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionas, :]

# Filtro transito
linhas_selecionas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionas, :]

# ====================================================================================================
#               Layout no Streamlit
# ====================================================================================================

tab1, tab2, tab3 = st.tabs(
    ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    # -----------------PRIMEIRO GRÁFICO------------------------------------------------------------------
    with st.container():

        fig = metricas_pedido(df1)
        st.markdown('Total de pedidos por dia')
        st.plotly_chart(fig, use_container_width=True)

# --------------FIM DO PRIMEIRO GRÁFICO--------------------------------------------------------------
# -----------------SEGUNDO GRÁFICO---------------------

    with st.container():
        coluna1, coluna2 = st.columns(2)
        with coluna1:

            fig = pedidos_densidade_transito(df1)
            st.markdown('Pedidos por densidade do transito')
            st.plotly_chart(fig, user_contaier_width=True)

        with coluna2:

            fig = pedidos_tipos_cidade(df1)
            st.markdown('Pedidos por tipos de cidade')
            st.plotly_chart(fig, use_container_width=True)


# --------------FIM DO TERCEIRO GRÁFICO----------------
# -----------------QUARTO GRÁFICO---------------------

with tab2:
    with st.container():
        fig = pedido_semana(df1)
        st.markdown('Pedidos por semana')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():

        fig = pedido_semana2(df1)
        st.plotly_chart(fig, use_container_width=True)


with tab3:
    st.markdown('Mapa')
    country_maps(df1)
