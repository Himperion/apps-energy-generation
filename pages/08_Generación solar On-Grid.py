# -*- coding: utf-8 -*-
import streamlit as st
import yaml

from funtions import fun_app8

#%%  global variables

with open("files//[COMP] - dict_components.yaml", 'r') as archivo:
    dict_components = yaml.safe_load(archivo)

with open("files//[PV] - params.yaml", 'r') as archivo:
    params_PV = yaml.safe_load(archivo)

#%% main

st.markdown("# Generación Solar Off-Grid")

tab1, tab2, tap3 = st.tabs(["📑 Marco teórico", "💾 Entrada de datos", "📝 Análisis"])

to_yaml = {
    "PV": {"label": "🪟 Módulo fotovoltaico", "sheet_label": "PV", "name": "Módulo fotovoltaico", "emoji": "🪟"},
    "INV": {"label": "🖲️ Inversor", "sheet_label": "INV", "name": "Inversor", "emoji": "🖲️"},
    "BAT": {"label": "🔋 Baterías", "sheet_label": "BAT", "name": "Baterías",  "emoji": "🔋"},
    "RC": {"label": "📶 Regulador de carga", "sheet_label": "RC", "name": "Regulador de carga",  "emoji": "📶"},
    "AERO": {"label": "🪁 Aerogenerador", "sheet_label": "AERO", "name": "Aerogenerador",  "emoji": "🪁"},
    "GE": {"label": "⛽ Grupo electrógeno", "sheet_label": "GE", "name": "Grupo electrógeno",  "emoji": "⛽"}
}

with tab2:
    with st.form("On-Grid"):
        with st.container(border=True):
            st.markdown(f"{dict_components['PV']['emoji']} **:blue[{dict_components['PV']['name']}:]**")

            uploadedYamlPV = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlPV')

            
            st.markdown("🧑‍🔧 **Conexión de los módulos**")
            col1, col2 = st.columns(2)

            with col1:
                PVs = fun_app8.get_widget_number_input(label=fun_app8.get_label_params(dict_param=params_PV["PVs"]),
                                                    disabled=False, variable=params_PV["PVs"]["number_input"])
            with col2:
                PVp = fun_app8.get_widget_number_input(label=fun_app8.get_label_params(dict_param=params_PV["PVp"]),
                                                    disabled=False, variable=params_PV["PVp"]["number_input"])
        
        with st.container(border=True):
            st.markdown(f"{dict_components['INV']['emoji']} **:blue[{dict_components['INV']['name']}:]**")

            uploadedYamlINV = st.file_uploader(label="Cargar archivo YAML", type=["yaml", "yml"], key='uploadedYamlINV')

        submitted = st.form_submit_button("Aceptar")

        if submitted:
            st.text("Ajaaaaaaaaaaaaaaaaaaaa")

        