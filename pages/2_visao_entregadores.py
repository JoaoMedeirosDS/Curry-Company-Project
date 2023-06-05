# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# Bibliotecas necessárias
import folium
import pandas as pd
import streamlit as st
from PIL import Image

from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Entregadores', page_icon = '', layout ='wide' )


#-------------------------------------
#Funções
#-------------------------------------
def top_deliveries(df1, top_asc):
    df2 = (  df1.loc[:, ['Time_taken(min)', 'City', 'Delivery_person_ID']]
                .groupby(['City', 'Delivery_person_ID'])
                .mean()
                .sort_values(['City', 'Time_taken(min)'], ascending = top_asc)
                .reset_index() )

    df1_aux1 = df2.loc[df2['City'] == 'Metropolitian'].head(10)
    df1_aux2 = df2.loc[df2['City'] == 'Urban'].head(10)
    df1_aux3 = df2.loc[df2['City'] == 'Semi-Urban'].head(10)
    df3 = pd.concat([df1_aux1, df1_aux2, df1_aux3]).reset_index(drop = True)
                
    return df3

def clean_code(df1):
    ''' Esta função tem a responsabilidade de limpar o dataframe
        
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variaveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variável númerica)
        
        Input: DataFrame
        Output: DataFrame
    '''
    
    # 1. Trocando Age para int
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    # 2. Trocando Ratings para float
    linhas_selecionadas = df1['Delivery_person_Ratings'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # 3. Trocando Order_Date para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'],format = '%d-%m-%Y')

    # 4. Trocando multiple_deliverys para int
    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # 5. Removendo os espaços das str
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip() 
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip() 

    # 6. Removendo o NaN da densidade de trafego
    linhas_selecionadas = df1['Road_traffic_density'] != 'NaN'
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # 7. Limpando a coluna 'Time_taken(min)'
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min)')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    # 8. Removendo o NaN de cidades
    linhas_selecionadas = df1['City'] != 'NaN'
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # 9. Removendo o NaN de Festival
    linhas_selecionadas = df1['Festival'] != 'NaN'
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    return df1
#---------------------------Inicio da estrutura logica do codigo--------------------------
#---------------------------------------
# Import DataSet
#---------------------------------------
df = pd.read_csv('dataset/train.csv')

#---------------------------------------
#limpando os dados
#---------------------------------------
df1 = clean_code(df)

#===============================================
# Barra Lateral
#===============================================

st.header('Marketpalce - Visão Empresa')

# image_path = 'C:/Users/WCC/OneDrive/Documentos/repos/programacao_python/Logo.PNG'

image= Image.open('Logo2.PNG')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = pd.datetime(2022, 4, 13),
    min_value = pd.datetime(2022, 2, 11),
    max_value = pd.datetime(2022, 4, 6),
    format = 'DD-MM-YYYY' )
    
st.header(date_slider)
st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect(
    'Escolha qual tipo de tráfico',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])
    
weather_options = st.sidebar.multiselect(
    'Escolha qual tipo de clima',
    ['conditions Sunny', 'conditions Cloudy', 'conditions Sandstorms', 'conditions Fog', 'conditions Windy', 'conditions Stormy'],
    default = ['conditions Sunny', 'conditions Cloudy', 'conditions Sandstorms', 'conditions Fog', 'conditions Windy', 'conditions Stormy'])

st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de Data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]
    
# Filtro de trafico
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]
    
# Filtro de clima
linhas_selecionadas = df1['Weatherconditions'].isin(weather_options)
df1 = df1.loc[linhas_selecionadas, :]

#=======================================================
# Layout Streamlit
#=======================================================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        
        # Entregador mais velho
        with col1:
            maior_idade = df1.loc[:,"Delivery_person_Age"].max()
            col1.metric('Maior idade', maior_idade)
        
        # Entregador mais novo
        with col2:
            menor_idade = df1.loc[:,"Delivery_person_Age"].min()
            col2.metric('Menor idade', menor_idade)
    
        # Melhor condição de veículo
        with col3:
            melhor_condicao = df1.loc[:,"Vehicle_condition"].max()
            col3.metric('Melhor condição', melhor_condicao)
    
        with col4:
            pior_condicao = df1.loc[:,"Vehicle_condition"].min()
            col3.metric('Pior condição', pior_condicao)
    
    with st.container():
        st.markdown('''---''')
        
        col1, col2 = st.columns(2)

        # Avaliação média por entregador
        with col1:
            st.markdown( '##### Avaliacao media por entregador' )

            df_avg_rating_per_deliver = (df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                            .groupby('Delivery_person_ID')
                                            .mean()
                                            .reset_index())
    
            col1.dataframe(df_avg_rating_per_deliver)

        with col2:
            st.markdown('##### Avaliacao media por transito')

            # A avaliação média por tipo de tráfego.
            df_avg_std_rating_by_traffic = ( df1.loc[:,['Delivery_person_Ratings', 'Road_traffic_density']]
                                                .groupby('Road_traffic_density')
                                                .agg( {'Delivery_person_Ratings': ['mean','std']} ) )
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            
            st.dataframe(df_avg_std_rating_by_traffic)
                                            
            # A avaliação média por condições climáticas.
            st.markdown( '##### Avaliacao media por clima' )
                                            
            df_avg_std_rating_by_weather = ( df1.loc[:,['Delivery_person_Ratings', 'Weatherconditions']]
                                                .groupby('Weatherconditions')
                                                .agg( {'Delivery_person_Ratings' : ['mean', 'std']} ) )

            df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
            
            st.dataframe(df_avg_std_rating_by_weather)
        
    
    with st.container():
        st.markdown( '''---''')
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        
        # Os entregadores mais rápidos por cidade.
        with col1:
            st.markdown( '##### Top Entregadores mais rapidos' )
            df3 = top_deliveries(df1, top_asc = True)
            
            st.dataframe(df3)
        
        # Os entregadores mais lentos por cidade.
        with col2:
            st.markdown( '##### Top Entregadores mais lentos' )
            df3 = top_deliveries(df1, top_asc = False)
                
            st.dataframe(df3)