# =================================================
#               Importando as bibliotecass
# =================================================

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import streamlit as st
import folium
from streamlit_folium import folium_static
from PIL import Image
from datetime import datetime

st.set_page_config(page_title="Visão Restaurantes",
                   page_icon=':broccoli:', layout='wide')


# =================================================
#               Importando o dataset
# =================================================

df = pd.read_csv('train.crdownload')
df1 = df.copy()


# ==================================================
#               Limpando o dataset
# ==================================================
# Remover spaco da string
for i in range(len(df1)):
    df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()
    df1.loc[i, 'Delivery_person_ID'] = df1.loc[i, 'Delivery_person_ID'].strip()

# Excluir as linhas com a idade dos entregadores vazia
# ( Conceitos de seleção condicional )
linhas_vazias = df1['Delivery_person_Age'] != 'NaN '
df1 = df1.loc[linhas_vazias, :]

# Conversao de texto/categoria/string para numeros inteiros
df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

# Conversao de texto/categoria/strings para numeros decimais
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

# Conversao de texto para data
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

# Remove as linhas da culuna multiple_deliveries que tenham o
# conteudo igual a 'NaN '
linhas_vazias = df1['multiple_deliveries'] != 'NaN '
df1 = df1.loc[linhas_vazias, :]
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

# Remove as linhas da culuna Weatherconditions que tenham o
# conteudo igual a 'NaN '
linhas_vazias = df1['Weatherconditions'] != 'conditions NaN'
df1 = df1.loc[linhas_vazias, :]

# Remove as linhas da culuna Weatherconditions que tenham o
# conteudo igual a 'NaN '
linhas_vazias = df1['City'] != 'NaN '
df1 = df1.loc[linhas_vazias, :]

# Comando para remover o texto de números
df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
df1.loc[:, 'Road_traffic_density'] = df1.loc[:,
                                             'Road_traffic_density'].str.strip()
df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

# Limpando a coluna de time taken
df1 = df1[df1['Time_taken(min)'] != 'NaN ']
df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(
    lambda x: x.split('(min) ')[1] if isinstance(x, str) else x)
df1['Time_taken(min)'].fillna(0, inplace=True)
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(float).astype(int)


# =================================================
#               Layout - Barra Lateral
# =================================================
st.header(':blue[Marketplace - Visão Restaurante]')

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
        # st.title('text1')

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            # st.markdown('coluna1')
            entregadores_unicos = len(
                df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entreg. Unicos', entregadores_unicos)  # print

        with col2:
            # st.markdown('coluna2')
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude',
                    'Restaurant_latitude', 'Restaurant_longitude']
            df1['distancia'] = df1.loc[:, cols].apply(lambda x: haversine(
                (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
            media_distancia = np.round(df1['distancia'].mean(), 2)
            col2.metric('Distancia média:',
                        media_distancia)  # print

        with col3:
            # st.markdown('coluna3')
            df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                      .groupby('Festival')
                      .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(
                df_aux.loc[df_aux['Festival'] == 'Yes ', 'avg_time'], 2)
            col3.metric('Tempo médio', df_aux)

        with col4:
            # st.markdown('coluna4')
            df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                      .groupby('Festival')
                      .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(
                df_aux.loc[df_aux['Festival'] == 'Yes ', 'std_time'], 2)
            col4.metric('STD entrega', df_aux)

        with col5:
            # st.markdown('coluna5')
            df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                      .groupby('Festival')
                      .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(
                df_aux.loc[df_aux['Festival'] == 'No ', 'avg_time'], 2)
            col5.metric('Tempo médio', df_aux)

        with col6:
            df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                      .groupby('Festival')
                      .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(
                df_aux.loc[df_aux['Festival'] == 'No ', 'std_time'], 2)
            col6.metric('STD de entrega', df_aux)
        st.markdown('''---''')

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            # st.title('Tempo médio de entrega por cidade')

            cols = ['Delivery_location_latitude', 'Delivery_location_longitude',
                    'Restaurant_latitude', 'Restaurant_longitude']
            df1['Distancia'] = df1.loc[:, cols].apply(lambda x:
                                                      haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)

            avg_distancia = df1.loc[:, ['City', 'Distancia']].groupby(
                "City").mean().reset_index()

            fig = go.Figure(data=[go.Pie(labels=avg_distancia['City'],
                            values=avg_distancia['Distancia'], pull=[0, 0.1, 0])])
            st.plotly_chart(fig)

        with col2:
            # st.markdown('coluna2')
            df_aux = df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({
                'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                              color='std_time', color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(df_aux['std_time']))
            st.plotly_chart(fig)
        st.markdown('''---''')
        col1, col2 = st.columns(2)
        with col1:
            # st.markdown('coluna1')
            cols = ['City', 'Time_taken(min)']
            df_aux = df1.loc[:, cols].groupby('City').agg(
                {'Time_taken(min)': ['mean', 'std']})

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Control',
                                 x=df_aux['City'],
                                 y=df_aux['avg_time'],
                                 error_y=dict(type='data', array=df_aux['std_time'])))
            st.plotly_chart(fig)

        with col2:
            # st.title('Distribuição por tempo')

            cols = ['City', 'Time_taken(min)', 'Type_of_order']
            df_aux = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg(
                {'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)
