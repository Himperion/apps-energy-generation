# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import yaml

from funtions import fun_app8

#%%  global variables

with open("files//[COMP] - dict_components.yaml", 'r') as archivo:
    dict_components = yaml.safe_load(archivo)

with open("files//[PV] - params.yaml", 'r') as archivo:
    params_PV = yaml.safe_load(archivo)

with open("files//[PV] - dict_replace.yaml", 'r') as archivo:
    rename_PV = yaml.safe_load(archivo)

optionsColumnsUploadedDATA = {
    "Dates": ("dates (Y-M-D hh:mm:ss)"),
    "Geff" : ("Gef(W/m^2)", "Gef(W/m²)", "Gin(W/m²)", "Gin(W/m^2)"),
    "Toper" : ("Toper(°C)"),
    "Load" : ("Load(kW)")
}

optionsKeysUploadedPV = [
    "alpha_sc",
    "beta_voc",
    "cells_in_series",
    "celltype",
    "gamma_pmp",
    "i_mp",
    "i_sc",
    "v_mp",
    "v_oc"
]

optionsKeysUploadedINV = [
    "Pac_max",
    "Vac_max",
    "Vac_min",
    "Vac_nom",
    "Vbb_nom",
    "efficiency_max",
    "grid_type",
    "phases"
]

showOutput = [f"{params_PV[elm]['label']}{params_PV[elm]['unit']}: {params_PV[elm]['description']}" for elm in ["Voc", "Isc", "Impp", "Vmpp", "Pmpp"]]


#%% session state

if 'check_DATA' not in st.session_state:
    st.session_state['check_DATA'] = False

if 'check_PV' not in st.session_state:
    st.session_state['check_PV'] = False

if 'check_INV' not in st.session_state:
    st.session_state['check_INV'] = False

if 'dictDataOnGrid' not in st.session_state:
    st.session_state['dictDataOnGrid'] = None

#%% main

st.markdown("# Generación Solar Off-Grid")

tab1, tab2, tab3 = st.tabs(["📑 Marco teórico", "💾 Entrada de datos", "📝 Análisis"])

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

        validateEntries = {
                'check_DATA': False,
                'check_PV': False,
                'check_INV': False
            }

        with st.container(border=True):
            st.markdown("📋 **:blue[Datos de carga, temperatura de operación y potencial solar del sitio:]**")

            uploadedXlsxDATA = st.file_uploader(label="**Cargar archivo EXCEL**", type=["xlsx"], key='uploadedYamlDATA')

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

            uploadedYamlINV = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlINV')

            st.markdown("⚡ **PCC (Punto de conexión común**")

            V_PCC = st.number_input(label="Tensión del punto de conexión común", value=127.0, placeholder="Ingrese un valor",
                                    format="%0.1f", step=None, min_value=0.0, max_value=1000.0)

        submitted = st.form_submit_button("Aceptar")

        if submitted:
            if uploadedXlsxDATA is not None:
                try:
                    df_data = pd.read_excel(uploadedXlsxDATA)
                    df_data, validateEntries['check_DATA'], columnsOptionsData = fun_app8.check_dataframe_input(df_data, optionsColumnsUploadedDATA)
                except:
                    st.error("Error al cargar archivo **EXCEL** (.xlsx)", icon="🚨")
            else:
                st.error("Cargar **Datos de carga, temperatura de operación y potencial solar del sitio**", icon="🚨")

            if uploadedYamlPV is not None:
                try:
                    PV_data = yaml.safe_load(uploadedYamlPV)
                    validateEntries['check_PV'] = fun_app8.check_dict_input(PV_data, optionsKeysUploadedPV)
                except:
                    st.error("Error al cargar archivo **YAML** (.yaml)", icon="🚨")

            else:
                st.error("Cargar **Datos del módulo fotovoltaico**", icon="🚨")

            if uploadedYamlINV is not None:
                try:
                    INV_data = yaml.safe_load(uploadedYamlINV)
                    validateEntries['check_INV'] = fun_app8.check_dict_input(INV_data, optionsKeysUploadedINV)
                except:
                    st.error("Error al cargar archivo **YAML** (.yaml)", icon="🚨")

            else:
                st.error("Cargar **Datos del Inversor**", icon="🚨")

            if validateEntries['check_DATA'] and validateEntries['check_PV'] and validateEntries['check_INV']:
                
                st.session_state['dictDataOnGrid'] = {
                    'df_data': df_data,
                    'PV_data': PV_data,
                    'INV_data': INV_data,
                    'PVs': PVs,
                    'PVp': PVp,
                    'V_PCC': V_PCC,
                    'columnsOptionsData': columnsOptionsData,
                    'params_PV': params_PV,
                    'rename_PV': rename_PV,
                    'show_output': showOutput
                }

            else:

                st.text(validateEntries['check_DATA'])
                st.text(validateEntries['check_PV'])
                st.text(validateEntries['check_INV'])


    if st.session_state['dictDataOnGrid'] is not None:
        #
        df_out = fun_app8.solarGenerationOnGrid(**st.session_state['dictDataOnGrid'])
        bytesFile = fun_app8.to_excel(df_out)

        df_download = st.download_button(
            label="📄 Descargar **:blue[Dataset] XLSX**",
            data=bytesFile,
            file_name=fun_app8.name_file_head(name="dataset_OffGrid.xlsx"),
            mime='xlsx')
        
with tab3:
    
    st.session_state['check_DATA'] = False
    st.session_state['check_PV'] = False
    st.session_state['check_INV'] = False
    st.session_state['dictDataOnGrid'] = None


    with st.form("analysisOnGrid"):
        uploaderXlsx = st.file_uploader(label="**Cargar archivo EXCEL**", type=["xlsx"], key='uploaderXlsx')  

        submitted = st.form_submit_button("Aceptar")

        if submitted:
            if uploaderXlsx is not None:
                try:
                    df_data = pd.read_excel(uploaderXlsx)
                    timeInfo = fun_app8.getTimeData(df_data)

                    for key, value in timeInfo.items():
                        st.text(f"{key}: {value}")

                    st.dataframe(df_data)
                    
                except:
                    st.error("Error al cargar archivo **EXCEL** (.xlsx)", icon="🚨")
            else:
                st.error("Cargar **Dataset generación Off-Grid**", icon="🚨")
    

        