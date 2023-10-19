# Libraries
from haversine import haversine
from datetime import date 
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import folium
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title = "Visão Empresa", layout = "wide")

#-------------------------------------
# Funções
#-------------------------------------
def clean_code (df):

#         Esta função tem a responsabilidade de limpar  o dataframe.
#         Tipos de limpeza:
#         1. Remover espaço da string
#         2. Excluir as linhas vazias
#         3. Conversao de texto para numeros inteiros
#         4. Conversao de texto para numeros decimais
#         5. Conversao de texto para data
#         6. Remoção o texto da coluna do tempo de entrega
#         Input: Dataframe
#         Output: Dataframe

    #1. Remover espaço da string
    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df.loc[:, 'Delivery_person_ID'] = df.loc[:, 'Delivery_person_ID'].str.strip()
    df.loc[:, 'Delivery_person_Age'] = df.loc[:, 'Delivery_person_Age'].str.strip()
    df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
    df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()
    df.loc[:, 'multiple_deliveries'] = df.loc[:, 'multiple_deliveries'].str.strip()

    #2. Excluir as linhas vazias
    # ( Conceitos de seleção condicional )
    linhas_nao_vazias = df['Delivery_person_Age'] != 'NaN'
    df = df.loc[linhas_nao_vazias, :]
    linhas_nao_vazias = df['City'] != 'NaN'
    df = df.loc[linhas_nao_vazias, :]
    linhas_nao_vazias = df['Road_traffic_density'] != 'NaN'
    df = df.loc[linhas_nao_vazias, :]
    linhas_nao_vazias = df['Festival'] != 'NaN'
    df = df.loc[linhas_nao_vazias, :]
    linhas_nao_vazias = df['multiple_deliveries'] != 'NaN'
    df = df.loc[linhas_nao_vazias, :]

    #3. Conversao de texto/categoria/string para numeros inteiros
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

    #4 Conversao de texto/categoria/strings para numeros decimais
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )

    #5 Conversao de texto para data
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

    #6 Remoção o texto da coluna do tempo de entrega
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    df  = df.reset_index()

    return df
#-------------------------------------
def order_metric (df):
    #Order_metric
    pedidos_por_dia = (df.loc[:,["ID","Order_Date"]]
                         .groupby(["Order_Date"])
                         .count()
                         .reset_index())
    #gráfico de barras
    import plotly.express as px
    fig = px.bar(pedidos_por_dia, x="Order_Date",y="ID")    
    return fig
#-------------------------------------
def traffic_order_share (df):
    pedidos_por_tipo_de_trafego = (df.loc[:,["ID","Road_traffic_density"]]
                                     .groupby(["Road_traffic_density"])
                                     .count()
                                     .reset_index())
    pedidos_por_tipo_de_trafego["porcentagem_dos_pedidos"] = pedidos_por_tipo_de_trafego["ID"] / pedidos_por_tipo_de_trafego["ID"].sum()
    #gráfico de pizza
    fig = px.pie(pedidos_por_tipo_de_trafego, values = "porcentagem_dos_pedidos", names = "Road_traffic_density")
    return fig

#-------------------------------------
def traffic_order_city (df):
    pedidos_por_cidade_e_por_tipo_de_trafego = (df.loc[:,["ID","City","Road_traffic_density"]]
                                                  .groupby(["City","Road_traffic_density"])
                                                  .count()
                                                  .reset_index())
    #gráfico de bolhas
    fig = px.scatter(pedidos_por_cidade_e_por_tipo_de_trafego, x = "City", y = "Road_traffic_density", size="ID", color = "City")
    return fig
#-------------------------------------
def pedidos_semanais (df):
    df["week_of_year"] = df["Order_Date"].dt.strftime("%U")
    pedidos_por_semana = (df.loc[:,["ID","week_of_year"]]
                            .groupby(["week_of_year"])
                            .count()
                            .reset_index())
    #gráfico de linhas
    fig = px.line(pedidos_por_semana, x="week_of_year", y="ID")
    return fig
#-------------------------------------
def media_pedidos_por_semana (df):
    df_aux1_exercicio5 = (df.loc[:,["ID","week_of_year"]]
                            .groupby(["week_of_year"])
                            .count()
                            .reset_index())
    df_aux2_exercicio5 = (df.loc[:,["Delivery_person_ID","week_of_year"]]
                            .groupby(["week_of_year"])
                            .nunique()
                            .reset_index())
    df_aux3_exercicio5 = pd.merge(df_aux1_exercicio5, df_aux2_exercicio5, how = "inner")
    df_aux3_exercicio5["mean_of_delivery_order"] = (df_aux3_exercicio5["ID"] / df_aux3_exercicio5["Delivery_person_ID"])
    media_de_pedidos_dos_entregadores_por_semana = df_aux3_exercicio5
    #gráfico de linhas
    fig = px.line(media_de_pedidos_dos_entregadores_por_semana, x="week_of_year", y="mean_of_delivery_order")
    return fig
#-------------------------------------
def mapa_paises (df):
    localizacao_central = (df.loc[:,["Delivery_location_latitude","Delivery_location_longitude",
                                     "City","Road_traffic_density"]]
                             .groupby(["City","Road_traffic_density"])
                             .median()
                             .reset_index())
    map = folium.Map()
    for index, location_info in localizacao_central.iterrows():
        folium.Marker( [location_info["Delivery_location_latitude"],
                        location_info["Delivery_location_longitude"]],
                        popup = location_info[["City","Road_traffic_density"]]).add_to(map)
    folium_static(map,width=1024,height=600)
    
#------------------------------------- Início da estrutura lógica do código ---------------------------------
#-------------------------------------
# Import dataset
#-------------------------------------
#df = pd.read_csv( r'C:\Users\Camila\Documents\repos\material_das_aulas\FTC_-_Analisando_Dados_com_Python\Ciclo_07\Ciclo_07_-_exercicios-resolvidos-por-mim\dataset\train.csv' )
df = pd.read_csv('train.csv')
#-------------------------------------
# Limpeza dos dados
#-------------------------------------
df1 = clean_code(df)

#-------------------------------------
# Barra lateral
#-------------------------------------
st.header( 'Marketplace - Visão Empresa' )

#img_path = r'C:\Users\Camila\Documents\repos\material_das_aulas\FTC_-_Analisando_Dados_com_Python\Ciclo_07\Ciclo_07_-_exercicios-resolvidos-por-mim\logo.jpg'
img = Image.open('logo.jpg')
st.sidebar.image(img)

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )
st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider( 
    'Até qual valor?',
        value= datetime(2022,4,6),
    min_value= datetime(2022,2,11),
    max_value= datetime(2022,4,6),
    format="DD/MM/YY")

st.sidebar.markdown( """---""" )

traffic_options = st.sidebar.multiselect( 
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'], 
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider 
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

#-------------------------------------
# Layout no Streamlit
#-------------------------------------
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    with st.container():
        st.markdown("### Pedidos por dia")
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width = True)
    
    with st.container():
        col1,col2 = st.columns(2)
        
        with col1:
            st.markdown("### Pedidos por tipo de tráfego")
            fig = traffic_order_share (df1)
            st.plotly_chart(fig, use_container_width = True)
        
        with col2:
            st.markdown("### Pedidos por região")
            fig = traffic_order_city (df1)
            st.plotly_chart(fig, use_container_width = True)
            
with tab2:
    with st.container():
        st.markdown("### Pedidos por semana")
        fig = pedidos_semanais (df1)
        st.plotly_chart(fig, use_container_width = True)
    
    with st.container():
        st.markdown("### Média de pedidos dos entregadores por semana")
        fig = media_pedidos_por_semana (df1)
        st.plotly_chart(fig, use_container_width = True)
        
with tab3:
    st.markdown("### Localização central dos restaurantes")
    mapa_paises(df1)
    
