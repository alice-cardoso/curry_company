import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon=":house:"
)

# image_path = r'C:\Users\User\repos_cds\ftc_analisando_dados_com_python\exercicios\logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('Cury Company')
st.sidebar.markdown('Faster Delivery in Town')
st.sidebar.markdown('''---''')

st.write('Dashboard da Empresa')
st.sidebar.markdown(
    'Essa dashboard foi desenvolvida para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.')
