# =================================================
#               Importando as bibliotecass
# =================================================

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from PIL import Image
from datetime import datetime

st.set_page_config(page_title="Visão Entregadores",
                   page_icon=':bicyclist:', layout='wide')


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


def top_entregadores(df1, top_asc):

    df2 = df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(
        ['City', 'Delivery_person_ID']).max().sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index()

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat([df_aux01, df_aux02, df_aux03]
                    ).reset_index(drop=True)
    return df3

# ====================================================================================================
#               Importando o dataset
# ====================================================================================================


df = pd.read_csv('train.crdownload')
df1 = df.copy()

# ====================================================================================================
#               Limpando o dataset
# ====================================================================================================

df1 = limpa_cod(df1)


# =================================================
#               Layout - Barra Lateral
# =================================================
st.header(':blue[Marketplace - Visão Entregadores]')

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

# =================================================
#                     FILTROS
# =================================================

# Filtro data
linhas_selecionas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionas, :]

# Filtro transito
linhas_selecionas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionas, :]

# =================================================
#               Layout no Streamlit
# =================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Métricas')
        col1, col2, col3, col4 = st.columns(4, gap='large')

        with col1:
            # st.subheader('Maior de idade')
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior de idade', maior_idade)

        with col2:
            # st.subheader('Menor de idade')
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor de idade', menor_idade)

        with col3:
            # st.subheader('Melhor condiçao de veículos')
            melhor_veiculo = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor veiculo', melhor_veiculo)
        with col4:
            pior_veiculo = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior veiculo', pior_veiculo)

    with st.container():
        st.markdown('''---''')
        # st.title('Avaliações')

        col1, col2 = st.columns(2)

        with col1:

            st.subheader('Média das avaliações por entregador')
            media_avaliacoes_entrega = (df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']].groupby(
                'Delivery_person_ID').mean().reset_index())
            st.dataframe(media_avaliacoes_entrega)

        with col2:
            st.subheader('Média das avaliações por transito')
            media_avaliacoes_trafego = (df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby(
                'Road_traffic_density').agg({'Delivery_person_Ratings': ['mean', 'std']}))

            # mudança do nome das colunas
            media_avaliacoes_trafego.columns = [
                'delivery_mean', 'delivery_std']

            # reset do index
            media_avaliacoes_trafego = media_avaliacoes_trafego.reset_index()
            st.dataframe(media_avaliacoes_trafego)

            st.subheader('Média das avaliações por clima')
            media_avaliacoes_clima = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby(
                'Weatherconditions').agg({'Delivery_person_Ratings': ['mean', 'std']}))

            # mudança do nome das colunas
            media_avaliacoes_clima.columns = ['delivery_mean', 'delivery_std']

            # reset do index
            media_avaliacoes_clima = media_avaliacoes_clima.reset_index()
            st.dataframe(media_avaliacoes_clima)

    with st.container():
        st.markdown('''---''')
        st.title('Velocidade de entrega')

        col1, col2 = st.columns(2)

        with col1:
            st.subheader('TOP entregadores mais rapidos')
            df3 = top_entregadores(df1, top_asc=True)
            st.dataframe(df3)

        with col2:

            st.subheader('TOP entregadores mais lentos')
            df3 = top_entregadores(df1, top_asc=False)
            st.dataframe(df3)
