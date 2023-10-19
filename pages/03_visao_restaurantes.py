# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import folium
import pandas as pd
import numpy  as np
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title = "Visão Restaurante", layout = "wide")

#-------------------------------------
# Funções
#-------------------------------------
def clean_code(df):
    
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
def distancia_media_dos_restaurantes(df,city):
    colunas = ["Restaurant_latitude", "Restaurant_longitude", "Delivery_location_latitude", "Delivery_location_longitude"]
    df["distance"] = ( df.loc[:,colunas]
                         .apply(lambda x : haversine((x["Restaurant_latitude"],x["Restaurant_longitude"]),
                                         (x["Delivery_location_latitude"],x["Delivery_location_longitude"])),axis=1))

    df_distancia_media = df.loc[:,["distance","City"]].groupby(["City"]).mean().reset_index()
    distancia_media_aux = df_distancia_media.loc[df_distancia_media["City"] == city]
    distancia_media = np.round(distancia_media_aux["distance"],2)
    return distancia_media
#-------------------------------------
def tempo_medio_e_std_by_city(df):
    df_aux_exercicio3 = (df.loc[:,["Time_taken(min)","City"]]
                           .groupby(["City"])
                           .agg({"Time_taken(min)":["mean","std"]}))
    df_aux_exercicio3.columns = ["avg_time","std_time"]
    tempo_mean_std = df_aux_exercicio3.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x=tempo_mean_std['City'], y=tempo_mean_std['avg_time'], 
                   error_y=dict(type='data', array=tempo_mean_std['std_time']))) 
    fig.update_layout(barmode='group')
    return fig
#-------------------------------------
def tempo_medio_e_std_by_city_festival(df):
    df_aux_exercicio6 = (df.loc[:,["Time_taken(min)","City","Festival"]]
                           .groupby(["City","Festival"])
                           .agg({"Time_taken(min)":["mean","std"]}))
    df_aux_exercicio6.columns = ["avg_time","std_time"]
    tempo_mean_std_festival = df_aux_exercicio6.reset_index()
    tempo_mean_std_festival = np.round( tempo_mean_std_festival.loc[tempo_mean_std_festival['Festival'] == 'Yes'], 2 )
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x=tempo_mean_std_festival['City'], y=tempo_mean_std_festival['avg_time'],
                          marker_color = 'orange', error_y=dict(type='data', array=tempo_mean_std_festival['std_time']))) 
    fig.update_layout(barmode='group')
    return fig
#-------------------------------------
def tempo_medio_std(df, coluna_agrupada):
    df_aux_exercicio5 = (df.loc[:,["Time_taken(min)","City",coluna_agrupada]]
                           .groupby(["City",coluna_agrupada])
                           .agg({"Time_taken(min)":["mean","std"]}))

    df_aux_exercicio5.columns = ["avg_time","std_time"]
    tempo_medio_e_std = df_aux_exercicio5.reset_index()
    return tempo_medio_e_std
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
st.header( 'Marketplace - Visão Restaurantes' )


#img_path = r'C:\Users\Camila\Documents\repos\material_das_aulas\FTC_-_Analisando_Dados_com_Python\Ciclo_07\Ciclo_07_-_exercicios-resolvidos-por-mim\logo.jpg'
img = Image.open('logo.jpg')
st.sidebar.image(img)


st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )
st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider( 
    'Até qual valor?',
        value=pd.to_datetime( 2022, 4, 6 ),
    min_value=pd.to_datetime(2022, 2, 11 ),
    max_value=pd.to_datetime( 2022, 4, 6 ),
    format='DD-MM-YYYY')

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
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', ' ', ' '] )

with tab1:
    with st.container():
        st.markdown( "### Overal Metrics" )
        col1, col2, col3, col4 = st.columns( 4 )
        
        with col1:
            entregadores_unicos = df1["Delivery_person_ID"].nunique()
            col1.metric( 'Entregadores', entregadores_unicos )

        with col2:
            media_distancia_by_city = distancia_media_dos_restaurantes(df1, city = 'Metropolitian')
            col2.metric( 'Dist. média Metropolitian', media_distancia_by_city )
            
        with col3:
            media_distancia_by_city = distancia_media_dos_restaurantes(df1, city = 'Semi-Urban')
            col3.metric( 'Dist. média Semi-Urban', media_distancia_by_city )
                                             
        with col4:
            media_distancia_by_city = distancia_media_dos_restaurantes(df1, city = 'Urban')
            col4.metric( 'Dist. média Urban', media_distancia_by_city )

    with st.container():
        st.markdown( """---""" )
        st.markdown( "### Tempo Médio de Entrega" )
        tempo_medio_e_std_by_city_chart = tempo_medio_e_std_by_city(df1)
        st.plotly_chart( tempo_medio_e_std_by_city_chart )
        
    with st.container():
        st.markdown( """---""" )
        st.markdown( "### Tempo Médio de Entrega no Festival" )
        tempo_medio_e_std_by_city_chart_festival = tempo_medio_e_std_by_city_festival(df1)
        st.plotly_chart( tempo_medio_e_std_by_city_chart_festival)
        
    with st.container():
        st.markdown( """---""" )
        st.markdown( "### Tempo por tipo de tráfego" )
        tempo_por_trafego = tempo_medio_std(df1, coluna_agrupada="Road_traffic_density")
        st.dataframe( tempo_por_trafego, use_container_width=True)
          
    with st.container():
        st.markdown( """---""" )
        st.markdown( "### Tempo por tipo de pedido" )
        tempo_por_pedido = tempo_medio_std(df1, coluna_agrupada="Type_of_order")
        st.dataframe( tempo_por_pedido, use_container_width=True)
        
