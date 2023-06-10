import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Métricas por país",
    page_icon="🏘️"
)

@st.cache_data(persist="disk")
def loadData():
    df = pd.read_csv('metricas_globales.csv',encoding="utf-8")
    return df

@st.cache_data(persist="disk")
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')
st.title("Visualización de indicadores y métricas por país")
st.header("¿Qué es esta web?")

st.sidebar.success("Selecciona una página de la parte superior")

#Para poder justificar el texto es necesario html
st.markdown('<div style="text-align: justify;">¡Bienvenid@ a nuestra página web de estadísticas y mapas! Aquí encontrarás información detallada sobre las principales métricas que afectan la calidad de vida y la longevidad en todo el mundo. Explora nuestros mapas interactivos y gráficos para descubrir las variaciones regionales, las tendencias globales y las diferencias significativas dentro de cada continente.  Queremos proporcionar información visualmente atractiva que pueda ayudarte a comprender mejor el mundo en el que vivimos.</div>', unsafe_allow_html=True)


st.markdown('<div style="text-align: justify; margin-top:3vh;">Puedes descargar el conjunto de datos utilizado en esta web haciendo click en el siguiente botón:</div>', unsafe_allow_html=True)

st.download_button(
   "Descargar conjunto de datos (utf-8)",
   convert_df(loadData()),
   "datos.csv",
   "text/csv",
   key='download-csv'
)