# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# Bibliotecas necessárias
import folium
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image

from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Restaurantes', page_icon = '', layout ='wide' )


#-------------------------------------
#Funções
#-------------------------------------
def avg_std_time_on_traffic(df1):
    df1_aux = (  df1.loc[:, ['City', 'Road_traffic_density', 'Time_taken(min)']]
                    .groupby(['City', 'Road_traffic_density'])
                    .agg({'Time_taken(min)' : ['mean', 'std']}) )

    df1_aux.columns = ['avg_time', 'std_time']
    df1_aux = df1_aux.reset_index()
    fig = px.sunburst(df1_aux, path=['City', 'Road_traffic_density'], values = 'avg_time',
                            color='std_time', color_continuous_scale='RdBu',
                            color_continuous_midpoint=np.average(df1_aux['std_time'] ) )
                
    return fig

def avg_std_time_graph(df1):
    df1_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)' : ['mean', 'std']})
    df1_aux.columns = ['avg_time', 'std_time'] #renomeia as colunas
    df1_aux = df1_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',x=df1_aux['City'],y=df1_aux['avg_time'],error_y=dict(type='data', array=df1_aux['std_time'])))
    fig.update_layout(barmode='group')
                
    return fig

def avg_std_time_delivery(df1, festival, op):
    ''' 
        Esta função calcula o tempo médio e o desvio padrão de tempo de entrega com ou sem festival
        Parâmetros:
            Input:
                -df1: Dataframe com os dados necessários para calculo
                -op: Tipo de operação que precisa ser calculado
                    'avg_time': Calcula o tempo médio
                    'std_time': Calcula o desvio padrão do tempo
            Output:
                -df1: Dataframe com 2 colunas e 1 linha
            
    '''
    colunas = ['Festival', 'Time_taken(min)']
    df1_aux = df1.loc[:, colunas].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
    df1_aux.columns = ['avg_time', 'std_time']
    df1_aux = df1_aux.reset_index()
    df1_aux = np.round(df1_aux.loc[df1_aux['Festival'] == festival, op], 2)
                
    return df1_aux

def distance(df1, fig):
    if fig == False:
        colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:, colunas].apply( lambda x: 
                               haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 ) 
        avg_distance = np.round(df1['distance'].mean(), 2)
        return avg_distance
    
    else:
        colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:, colunas].apply( lambda x: 
                                    haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ),axis=1) 

        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure( data=[go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
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

#============================================
# Barra Lateral
#============================================
st.header('Marketplace - Visao Restaurantes')

# image_path = 'C:/Users/WCC/OneDrive/Documentos/repos/programacao_python/Logo.PNG'

image= Image.open('Logo2.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY' )

st.header( date_slider )
st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low','Medium','High','Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'] )

weather_options = st.sidebar.multiselect(
    'Quais as condições de clima',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default =  ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'] )

st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Comunidade DS' )

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de clima
linhas_selecionadas = df1['Weatherconditions'].isin(weather_options)
df1 = df1.loc[linhas_selecionadas, :]

#============================================
# Layout no Streamlit
#============================================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        # Quantidade de entregadores únicos
        with col1:
            entregadores_unicos = df1['Delivery_person_ID'].nunique()
            
            col1.metric('Entregadores', entregadores_unicos)
        
        # A distância média dos resturantes e dos locais de entrega.
        with col2:
            avg_distance = distance(df1, fig = False)
            col2.metric('Distância média', avg_distance)
        
        # O tempo médio de entrega durante os Festivais.
        with col3:
            df1_aux = avg_std_time_delivery(df1, festival = 'Yes', op = 'avg_time')
            col3.metric('Tempo médio',df1_aux)
        
        # O desvio padrão de entrega médio durante os Festivais.
        with col4:
            df1_aux = avg_std_time_delivery(df1, festival = 'Yes', op = 'std_time')
            col4.metric('STD médio',df1_aux)
        
        # O tempo médio de entrega sem os Festivais.
        with col5:
            df1_aux = avg_std_time_delivery(df1, festival = 'No', op = 'avg_time')
            col5.metric('Tempo médio',df1_aux)
            
        # O desvio padrão de entrega médio sem os Festivais.
        with col6:
            df1_aux = avg_std_time_delivery(df1, festival = 'No', op = 'std_time')
            col6.metric('STD médio',df1_aux)
        
    with st.container():
        st.markdown('''---''')
        col1, col2 = st.columns(2)
        
        # O tempo médio de entrega por cidade.
        with col1:
            st.markdown('## Tempo médio de entrega por cidade.')
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig, use_container_width=True)
            
        # Tempo médio por tipo de entrega
        with col2:
            st.markdown('## Tempo médio por tipo de entrega')
            df1_aux = (  df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                            .groupby(['City', 'Type_of_order'])
                            .agg({'Time_taken(min)' : ['mean', 'std']}) )
            df1_aux.columns = ['avg_time', 'std_time']
            df1_aux = df1_aux.reset_index()  

            st.dataframe(df1_aux, use_container_width=True)
    
    # O tempo médio e o desvio padrão de entrega por cidade.
    with st.container():
        st.markdown('''---''')
        st.title('Distribuição do Tempo')
        col1, col2 = st.columns(2)
        with col1:
            fig = distance(df1, fig = True)
            st.plotly_chart(fig, use_container_width=True)
                       
        with col2:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)
            
    with st.container():
        st.markdown('''---''')