import streamlit as st
import pandas as pd
import folium
import geopandas as gpd
from streamlit_folium import st_folium
import time
from math import isnan
import plotly.express as px
import plotly.graph_objects as go

APP_TITLE = 'Gráficas por país'
APP_SUB_TITLE = 'Fuente: Gapminder'

if 'year_enabled' not in st.session_state:
    st.session_state.year_enabled = False

metricList = ["PIB_capita","Esperanza_vida","Población","Población_urbana","Bebés_por_mujer","Saneamiento_básico"]
metricNames = ["PIB per cápita (2017 USD)", "Esperanza de vida", "Población total", "% Población urbana", "Bebés promedio por mujer", "% Acceso saneamiento básico"]

def display_time_filters(df):
    year_list = list(df['Año'].unique())
    minYear = int(min(year_list))
    maxYear = int(max(year_list))
    year = st.sidebar.slider('Año', min_value=minYear,max_value=maxYear,step=1, value=2020,disabled=st.session_state.year_enabled)
    return year
    

def display_prov_filter():
    return st.sidebar.selectbox('País', prov_list)

def display_grafica_filter(tipos):
    return st.sidebar.selectbox('Tipo de gráfica', tipos)

def display_show_text(tipoGrafica):
    if tipoGrafica == "Dispersión":
        text = 'Mostrar nombres de países'
    else:
        text = "Mostrar valores numéricos"
    return st.checkbox(text, value=False)

def display_histogram_intervals():
    return st.slider('Número de intervalos', min_value=1,max_value=25,step=1, value=8)

def display_metric_filter(metricNames):
    return st.sidebar.selectbox('Métrica', metricNames)

def display_metric_filter2(metricNames):
    return st.sidebar.selectbox('Métrica a comparar', metricNames,index=1)

def display_x_values(tag):
    return st.slider(f'Nº valores {tag}:', min_value=0,max_value=10,step=1, value=4)

def selectContinent():
    listaConts = ["Global", "Europa", "Oceanía", "América Norte", "América Sur", "África", "Asia"]
    return st.sidebar.selectbox('Continente', listaConts)

def selectLogScale(tag):
    return st.checkbox("Escala logarítmica "+tag, value=False)

def scatterPlot(df,m1,m2,showText,xLog=False,yLog=False):
    if showText:
        fig = px.scatter(df, x=m1, y=m2, color='Continente',text="País",hover_data=["País"],log_x=xLog,log_y=yLog)
    else:
        fig = px.scatter(df, x=m1, y=m2, color='Continente',hover_data=["País"],log_x=xLog,log_y=yLog)
    fig.update_layout(yaxis_title=metricNames[metricList.index(m1)],xaxis_title=metricNames[metricList.index(m2)])
    return fig

def histogram(df,m,nbins,showText):
    fig = px.histogram(df, x=m,nbins = nbins,text_auto=showText,labels={"count": "Sepal Length (cm)",})
    fig.update_layout(yaxis_title="Número de países",xaxis_title=metricNames[metricList.index(m)])
    fig.update_traces(marker_line_width=1,marker_line_color="white")
    return fig

def heatmap(df,showText):
    df = df.drop(columns=["País","Continente","ISO","Año","Unnamed: 0"])
    df = df.corr()
    
    fig = px.imshow(df,text_auto=showText,color_continuous_scale="RdBu")
    return fig

def lineChart(df,m):
    #df[m] = df[m].mean()
    df = df.groupby([df["Continente"],df["Año"]])[m].mean().reset_index()
    fig = px.line(df, x="Año", y=m, color='Continente')
    fig.update_layout(yaxis_title=metricNames[metricList.index(m)],xaxis_title="Año")
    return fig

def barChart(df,m,minV,maxV,setLog,showText):
    dfMin = df.nsmallest(minV,m)
    dfMax = df.nlargest(maxV,m)
    df = pd.concat([dfMin,dfMax])
    fig = px.bar(df, x=m, y='País',
                hover_data=[m], color=m,text_auto=showText,color_continuous_scale="RdBu",log_x=setLog)
    fig.update_layout(yaxis={'categoryorder':'total ascending'},xaxis_title=metricNames[metricList.index(m)])

    return fig

def display_graph(df, year,tipo, m1,m2=None, continente="Global", showText=False, intervals=8):
    if tipo!="Líneas":
        if continente == "Global":
            df = df[(df['Año'] == year)]
        else:
            df = df[(df['Año'] == year) & (df['Continente'] == continente)]
    else:
        if continente != "Global":
            df = df[df['Continente'] == continente]
    
    if tipo=="Dispersión":
        #Usamos escala logarítmica para algunos valores con mucha varianza
        c1,c2 = st.columns(2)
        with st.container():
            with c1:
                xLog = selectLogScale("eje x")
            with c2:
                yLog = selectLogScale("eje y")
        fig = scatterPlot(df,m1,m2,showText,xLog=xLog,yLog=yLog)
    elif tipo=="Histograma":
        fig = histogram(df,m1,intervals,showText)
    elif tipo=="Mapa de calor (correlaciones)":
        fig = heatmap(df,showText)
    elif tipo=="Líneas":
        fig = lineChart(df,m1)
    else: #Barras
        setLog = selectLogScale("")
        c1,c2 = st.columns(2)
        with st.container():
            with c1:
                minV = display_x_values("mínimos")
            with c2:
                maxV = display_x_values("máximos")
        fig = barChart(df,m1,minV,maxV,setLog,showText)


    st.plotly_chart(fig, use_container_width=True)


@st.cache_data(persist="disk")
def loadGeo():
    geo = gpd.read_file("geografia.geojson")
    return geo

@st.cache_data(persist="disk")
def loadData():
    df = pd.read_csv('metricas_globales.csv',encoding="utf-8")
    return df

@st.cache_data
def loadCountries():
    c_list = list(prov_data['País'].unique())
    c_dict = pd.Series(prov_data["País"].values,index=prov_data["ISO"]).to_dict()
    return c_list,c_dict

st.set_page_config(APP_TITLE,page_icon='📈')
#st.title(APP_TITLE)


prov_geo = loadGeo()
prov_data = loadData()

prov_list, prov_dict = loadCountries()

graficaList = ["Dispersión","Histograma","Barras","Mapa de calor (correlaciones)", "Líneas"]

holder = st.empty()
with holder:
    year = display_time_filters(prov_data)
holder.empty()
tipoGrafica = display_grafica_filter(graficaList)
continente = selectContinent()
metricName1,selectedMetric1 ="",""
if tipoGrafica != "Mapa de calor (correlaciones)":
    metricName1 = display_metric_filter(metricNames)
    selectedMetric1 = metricList[metricNames.index(metricName1)] #Métrica seleccionada a mostrar

#Deshabilitamos año
if tipoGrafica == "Líneas":
    st.session_state.year_enabled = False
else: 
    st.session_state.year_enabled = True
#Valores inicializados
selectedMetric2 = None
showText = False
intervalos = 8



st.caption(APP_SUB_TITLE)
with st.container():
    if tipoGrafica == "Histograma":
        st.header(f'Distribución de {metricName1} ({continente}) - {year}' )
        intervalos = display_histogram_intervals()
    elif tipoGrafica == "Dispersión":
        metricName2 = display_metric_filter2(metricNames)
        selectedMetric2 = metricList[metricNames.index(metricName2)] #Métrica seleccionada a mostrar
        st.header(f'{metricName1} y {metricName2} ({continente}) - {year}' )
    elif tipoGrafica == "Mapa de calor (correlaciones)":
        st.header(f'Correlaciones entre variables ({continente}) - {year}' )
    elif tipoGrafica == "Líneas":
        st.header(f'Evolución de {metricName1} ({continente})' )
    else: 
        st.header(f'Países con mínimo y máximo valor de {metricName1} - {year}' )

    if tipoGrafica not in  ["Líneas","Dispersión","Barras"]:
        showText = display_show_text(tipoGrafica)
    display_graph(prov_data, year,tipoGrafica, selectedMetric1,m2=selectedMetric2, continente=continente,showText=showText,intervals = intervalos)
