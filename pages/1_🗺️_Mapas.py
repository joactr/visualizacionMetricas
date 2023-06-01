import streamlit as st
import pandas as pd
import folium
import geopandas as gpd
from streamlit_folium import st_folium
import time
from math import isnan


APP_TITLE = 'Métricas por país'
APP_SUB_TITLE = 'Fuente: Gapminder'

def display_time_filters(df):
    year_list = list(df['Año'].unique())
    minYear = int(min(year_list))
    maxYear = int(max(year_list))
    year = st.sidebar.slider('Año', min_value=minYear,max_value=maxYear,step=1, value=2020)
    return year
    

def display_prov_filter():
    return st.sidebar.selectbox('País', prov_list)

def display_metric_filter(metricNames):
    return st.sidebar.selectbox('Métrica', metricNames)

def selectContinent():
    listaConts = ["Global", "Europa", "Oceanía", "América Norte", "América Sur", "África", "Asia"]
    return st.sidebar.selectbox('Continente', listaConts)

def createFoliumMap(df,selectedMetric):
    legendNames = {"PIB_capita":"PIB per cápita en USD (inflación 2017)","Esperanza_vida": "Esperanza de vida (años)","Población": "Total de población",
                    "Población_urbana":"% Población urbana","Bebés_por_mujer":"Bebés promedio por mujer","Saneamiento_básico":"% Acceso a saneamiento básico"}
    legendName = legendNames[selectedMetric]
    
    coropletas = folium.Choropleth(geo_data=prov_geo,data=df,columns=["ISO", selectedMetric],
                                   key_on="feature.properties.ISO", fill_color="RdYlGn",fill_opacity=0.7,line_opacity=1.0,legend_name=legendName)
    return coropletas

def display_map(df, year, selectedMetric, continente):
    if continente == "Global":
        df = df[(df['Año'] == year)]
    else:
        df = df[(df['Año'] == year) & (df['Continente'] == continente)]

    coropletas = createFoliumMap(df, selectedMetric)
    #Creamos mapa, centrado en españa, con poco zoom, sin la marca de agua inferior derecha, límites al scrollear
    m = folium.Map(location=[40.42,  -3.7], zoom_start=2, min_zoom = 1.3,attributionControl=False,
                  min_lot=-250,max_lot=250, min_lat=-70, max_lat=250, max_bounds=True)
    coropletas.add_to(m)
    coropletas.geojson.add_child(
        folium.features.GeoJsonTooltip(fields=['COUNTRY'],
                                       aliases=["País: "], labels=False,
                                       style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")))
    
    folium.LayerControl().add_to(m)
    st_map = st_folium(m, width=700, height=450,returned_objects=["last_active_drawing"])
    codigo = '00'
    if st_map['last_active_drawing']:
        codigo = st_map['last_active_drawing']['properties']['ISO']
    return codigo

def number_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

def display_datos_paro(df, year, prov_name, selectedMetric, name):
    df = df[(df['Año'] == year) & (df['País'] == prov_name)]
    if not isnan(df[selectedMetric].iat[0]):
        if selectedMetric == "PIB_capita":
            st.metric(name, "$"+str(int(df[selectedMetric].iat[0])))
        elif selectedMetric == "Esperanza_vida":
            st.metric(name, str(int(df[selectedMetric].iat[0]))+" años")
        elif selectedMetric == "Población":
            st.metric(name, number_format(df[selectedMetric].iat[0]))
        elif selectedMetric == "Bebés_por_mujer":
            st.metric(name, str(df[selectedMetric].iat[0]))
        else:
            st.metric(name, str(df[selectedMetric].iat[0])+' %')
    else: #No tenemos el dato
        st.metric(name, "Desconocido")

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

st.set_page_config(APP_TITLE,page_icon='🗺️')
#st.title(APP_TITLE)


prov_geo = loadGeo()
prov_data = loadData()

prov_list, prov_dict = loadCountries()

metricList = ["PIB_capita","Esperanza_vida","Población","Población_urbana","Bebés_por_mujer","Saneamiento_básico"]
metricNames = ["PIB per cápita (2017 USD)", "Esperanza de vida", "Población total", "% Población urbana", "Bebés promedio por mujer", "% Acceso saneamiento básico"]
year = display_time_filters(prov_data)
continente = selectContinent()
metricName = display_metric_filter(metricNames)
selectedMetric = metricList[metricNames.index(metricName)] #Métrica seleccionada a mostrar
st.header(f'{metricName} ({continente}) - {year}' )
st.caption(APP_SUB_TITLE)
with st.container():
    prov_code = display_map(prov_data, year, selectedMetric, continente)
prov_name = display_prov_filter()


#Display Metrics
if (prov_code!='00'):
    prov_name = prov_dict[prov_code]


st.subheader(f'Métricas en: \t{prov_name}')    


with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        display_datos_paro(prov_data, year, prov_name,"PIB_capita","PIB per cápita (2017 USD)")
    with col2:
        display_datos_paro(prov_data, year, prov_name,"Esperanza_vida", "Esperanza de vida")
    with col3:
        display_datos_paro(prov_data, year, prov_name,"Población","Población total")
with st.container(): 
    col4, col5, col6 = st.columns(3)
    with col4:
        display_datos_paro(prov_data, year, prov_name,"Población_urbana","% Población urbana")
    with col5:
        display_datos_paro(prov_data, year, prov_name,"Bebés_por_mujer","Bebés promedio por mujer")
    with col6:
        display_datos_paro(prov_data, year, prov_name,"Saneamiento_básico","% Acceso saneamiento básico")