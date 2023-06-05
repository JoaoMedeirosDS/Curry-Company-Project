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

st.set_page_config( page_title='Visão Empresa', page_icon = '', layout ='wide' )

#-------------------------------------
#Funções
#-------------------------------------
def country_maps(df1):
    df1_aux = (  df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
                    .groupby(['City','Road_traffic_density'])
                    .median()
                    .reset_index() )

    map = folium.Map()
    for index, location_info in df1_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup = location_info[['City', 'Road_traffic_density']]).add_to(map)
    folium_static(map, width = 1024, height = 600)
            
def order_share_by_week(df1):
    df1_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df1_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    df1_aux = pd.merge(df1_aux1, df1_aux2, how = 'inner')
    df1_aux['order_by_delivery'] = df1_aux['ID'] / df1_aux['Delivery_person_ID']
    fig = px.line(df1_aux, x = 'week_of_year', y= 'order_by_delivery')

    return fig

def order_by_week(df1):
    df1['week_of_year'] = df1.loc[:, 'Order_Date'].dt.strftime('%U')
    df1_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df1_aux, x = 'week_of_year', y = 'ID')
            
    return fig

def traffic_order_city(df1):
    df1_aux = (  df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                    .groupby(['City', 'Road_traffic_density'])
                    .count()
                    .reset_index() )
    df1_aux = df1_aux.loc[df1_aux['Road_traffic_density'] != 'NaN', :]
    df1_aux = df1_aux.loc[df1_aux['City'] != 'NaN', :]
    fig =  px.scatter(df1_aux, x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'Road_traffic_density')
                       
    return fig
                       
def traffic_order_share(df1):
    df1_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df1_aux = df1_aux.loc[df1_aux['Road_traffic_density'] != 'NaN', :]
    df1_aux['perc_ID'] = 100 * (df1_aux['ID'] / df1_aux['ID'].sum())
    fig =  px.pie(df1_aux,values = 'perc_ID', names = 'Road_traffic_density')
            
    return fig
        
def order_metric(df1):
    # Seleção de linhas
    df1_aux = df1.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    
    # desenhar grafico de linhas
    fig = px.bar(df1_aux, x = 'Order_Date', y = 'ID')
        
    return fig

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

image= Image.open('Logo2.png')
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
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )


with tab1:
    # Quantidade de pedidos por dia
    with st.container():
        fig = order_metric(df1)
        st.title('Pedidos por dia')
        st.plotly_chart(fig, use_container_width = True)

    with st.container():
        col1, col2 = st.columns(2)
        
        # Distribuição de pedidos por tipo de tráfego
        with col1:
            fig = traffic_order_share(df1)
            st.title('Pedidos por tipo de tráfego')
            st.plotly_chart(fig, use_container_width = True)
            

        # Comparação do volume de pedidos por cidade e tipo de tráfego.
        with col2:
            fig = traffic_order_city(df1)
            st.title('Comparação de pedidos')
            st.plotly_chart(fig, use_container_width = True)
            
with tab2:
    # Quantidade de pedidos por semana
    with st.container():
        fig = order_by_week(df1)
        st.title('Pedidos por semana')
        st.plotly_chart(fig, use_container_width = True) 
    
    # A quantidade de pedidos por entregador por semana.
    with st.container():
        fig = order_share_by_week(df1)
        st.title('Pedidos por entregador por semana')
        st.plotly_chart(fig, use_container_width = True)
        
with tab3:
    # A localização central de cada cidade por tipo de tráfego.
    with st.container():
        st.markdown('# Country Maps')
        country_maps(df1)