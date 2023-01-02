import streamlit as st
from PIL import Image

st.set_page_config(page_title = "Home")

#img_path = r'C:\Users\Camila\Documents\repos\material_das_aulas\FTC_-_Analisando_Dados_com_Python\Ciclo_07\Ciclo_07_-_exercicios-resolvidos-por-mim\logo.jpg'
img = Image.open('logo.jpg')
st.sidebar.image(img)

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.write("# Cury Company Growth Dashboard")

st.markdown(
    """
    O Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa
        - Visão Gerencial: Métricas gerais de comportamento
        - Visão Tática: Indicadores semanais de crescimento
        - Visão Geográfica: Insights de geolocalização
    - Visão Entregador
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante
        - Indicadores semanais de crescimento dos restaurantes 
    ### Ajuda
    - Envie suas dúvidas para: camilasparise@gmail.com
    """
)


