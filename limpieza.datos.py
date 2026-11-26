
import pandas as pd 
import streamlit as st
st.title("Limpieza de datos")
st.write("esta apliacion permite limpiar y procesar datos")
ruta = "https://github.com/ospinagrandaxiomara-jpg/fundamentos-de-programaci-n-/raw/refs/heads/main/data_prueba.csv"
df = pd.read_csv(ruta)
print(df.head())
st.dataframe(df.head())
