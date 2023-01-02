# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import folium
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title = "Visão Entregador", layout = "wide")

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
def avaliacao_media_e_std (df, coluna_agrupada):
    df_mean_std = (df1.loc[:,["Delivery_person_Ratings",coluna_agrupada]]
                                  .groupby([coluna_agrupada])
                                  .agg({"Delivery_person_Ratings":["mean","std"]}))
    # mudança de nome das colunas            
    df_mean_std.columns = ['delivery_mean', 'delivery_std']
    # reset do index
    df_mean_std = df_mean_std.reset_index()

    return df_mean_std
#-------------------------------------
def top_entregadores (df, top_asc):
    df_velocidade_entregadores = (df.loc[:,["Time_taken(min)","City","Delivery_person_ID"]]
                                    .groupby(["City","Delivery_person_ID"])
                                    .mean()
                                    .sort_values(["City","Time_taken(min)"],ascending=top_asc)
                                    .reset_index())
    df_aux1_exercicio6 = df_velocidade_entregadores.loc[df_velocidade_entregadores["City"] == "Metropolitian",:].head(10)
    df_aux2_exercicio6 = df_velocidade_entregadores.loc[df_velocidade_entregadores["City"] == "Urban",:].head(10)
    df_aux3_exercicio6 = df_velocidade_entregadores.loc[df_velocidade_entregadores["City"] == "Semi-Urban",:].head(10)
    # concatenação e reset do index
    df_top_entregadores = pd.concat([df_aux1_exercicio6,df_aux2_exercicio6,df_aux3_exercicio6]).reset_index()
    return df_top_entregadores

#------------------------------------- Início da estrutura lógica do código ---------------------------------
#-------------------------------------
# Import dataset
#-------------------------------------
#df = pd.read_csv( r'C:\Users\Camila\Documents\repos\material_das_aulas\FTC_-_Analisando_Dados_com_Python\Ciclo_07\Ciclo_07_-_exercicios-resolvidos-por-mim\dataset\train.csv' )
df = pd.read_csv(r'dataset\train.csv')
#-------------------------------------
# Limpeza dos dados
#-------------------------------------
df1 = clean_code(df)

#-------------------------------------
# Barra lateral
#-------------------------------------
st.header( 'Marketplace - Visão Entregadores' )

#img_path = r'C:\Users\Camila\Documents\repos\material_das_aulas\FTC_-_Analisando_Dados_com_Python\Ciclo_07\Ciclo_07_-_exercicios-resolvidos-por-mim\logo.jpg'
img = Image.open('logo.jpg')
st.sidebar.image(img)

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )
st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider( 
    'Até qual valor?',
        value=pd.datetime( 2022, 4, 6 ),
    min_value=pd.datetime(2022, 2, 11 ),
    max_value=pd.datetime( 2022, 4, 6 ),
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
        st.markdown( '### Overall Metrics' )
        col1, col2, col3, col4 = st.columns( 4 )

        with col1:
            # A maior idade dos entregadores
            maior_idade = df1["Delivery_person_Age"].max()
            col1.metric( 'Maior de idade', maior_idade )
       
        with col2:
            # A menor idade dos entregadores
            menor_idade = df1["Delivery_person_Age"].min()
            col2.metric( 'Menor idade', menor_idade )
            
        with col3:
            # A melhor condição climática
            melhor_condicao = df1["Vehicle_condition"].max()
            col3.metric( 'Melhor condição climática', melhor_condicao )
            
        with col4:
            # A pior condição climática
            pior_condicao = df1["Vehicle_condition"].min()
            col4.metric( 'Pior condição climática', pior_condicao )
            
    with st.container():
        st.markdown( """---""" )
        st.markdown( '### Avaliações' )
        
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '##### Avaliação média por entregador' )
            df_aval_media_por_entregador = (df1.loc[:,["Delivery_person_Ratings","Delivery_person_ID"]]
                                               .groupby(["Delivery_person_ID"])
                                               .mean()
                                               .reset_index())
            st.dataframe( df_aval_media_por_entregador )
                
        with col2:
            st.markdown( '##### Avaliação média por trânsito' )
            df_mean_std_por_trafego = avaliacao_media_e_std (df1, coluna_agrupada="Road_traffic_density")
            st.dataframe( df_mean_std_por_trafego )
            
            st.markdown( '##### Avaliação média por clima' )
            df_mean_std_por_cond_climatica = avaliacao_media_e_std (df1, coluna_agrupada="Weatherconditions")
            st.dataframe( df_mean_std_por_cond_climatica )
    
    with st.container():
        st.markdown( """---""" )
        st.markdown( '### Velocidade de Entrega' )
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown( '##### Top Entregadores mais rápidos' )
            df_top_entregadores_mais_rapidos = top_entregadores(df1, top_asc=True)
            st.dataframe( df_top_entregadores_mais_rapidos )
            
        with col2:
            st.markdown( '##### Top Entregadores mais lentos' )
            df_top_entregadores_mais_lentos = top_entregadores(df1, top_asc=False)
            st.dataframe( df_top_entregadores_mais_lentos )