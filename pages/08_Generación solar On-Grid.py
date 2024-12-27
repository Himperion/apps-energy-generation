# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
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

dictMonths = {1: "enero",
              2: "febrero",
              3: "marzo",
              4: "abril",
              5: "mayo",
              6: "junio",
              7: "julio",
              8: "agosto",
              9: "septiembre",
              10: "octubre",
              11: "noviembre",
              12: "diciembre"}

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

listGenerationOptions = ["Generación solar", "Generación eólica"]

showOutput = [f"{params_PV[elm]['label']}{params_PV[elm]['unit']}: {params_PV[elm]['description']}" for elm in ["Voc", "Isc", "Impp", "Vmpp", "Pmpp"]]


#%% session state

if 'check_DATA' not in st.session_state:
    st.session_state['check_DATA'] = False

if 'check_PV' not in st.session_state:
    st.session_state['check_PV'] = False

if 'check_INV_PV' not in st.session_state:
    st.session_state['check_INV_PV'] = False

if 'check_AERO' not in st.session_state:
    st.session_state['check_AERO'] = False

if 'check_INV_AERO' not in st.session_state:
    st.session_state['check_INV_AERO'] = False

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

    generationOptions = st.multiselect(label="Opciones de generación eléctrica", options=listGenerationOptions, default=listGenerationOptions[0])

    with st.container(border=True):
        st.markdown("📋 **:blue[Datos de carga, temperatura de operación y potencial energetico del sitio:]**")

        uploadedXlsxDATA = st.file_uploader(label="**Cargar archivo EXCEL**", type=["xlsx"], key='uploadedYamlDATA')

    with st.form("On-Grid", border=False):

        validateEntries = {
                'check_DATA': False,
                'check_PV': False,
                'check_INV_PV': False,
                'check_AERO': False,
                'check_INV_AERO': False,
            }
        
        if listGenerationOptions[0] in generationOptions:
            with st.container(border=True):

                with st.container(border=True):
                    st.markdown(f"{dict_components['PV']['emoji']} **:blue[{dict_components['PV']['name']}:]**")

                    uploadedYamlPV = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlPV')

                    st.markdown("🧑‍🔧 Conexión de los módulos")
                    col1, col2 = st.columns(2)

                    with col1:
                        PVs = fun_app8.get_widget_number_input(label=fun_app8.get_label_params(dict_param=params_PV["PVs"]),
                                                            disabled=False, variable=params_PV["PVs"]["number_input"])
                    with col2:
                        PVp = fun_app8.get_widget_number_input(label=fun_app8.get_label_params(dict_param=params_PV["PVp"]),
                                                            disabled=False, variable=params_PV["PVp"]["number_input"])
                
                with st.container(border=True):
                    st.markdown(f"{dict_components['INV_PV']['emoji']} **:blue[{dict_components['INV_PV']['name']}:]**")

                    uploadedYamlINV_PV = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlINV_PV')

        if listGenerationOptions[1] in generationOptions:
            with st.container(border=True):

                with st.container(border=True):
                    st.markdown(f"{dict_components['AERO']['emoji']} **:green[{dict_components['AERO']['name']}:]**")

                    uploadedYamlAERO = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlAERO')

                with st.container(border=True):
                    st.markdown(f"{dict_components['INV_AERO']['emoji']} **:green[{dict_components['INV_AERO']['name']}:]**")

                    uploadedYamlINV_AERO = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlINV_AERO')

        with st.container(border=True):
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

            if uploadedYamlINV_PV is not None:
                try:
                    INVPV_data = yaml.safe_load(uploadedYamlINV_PV)
                    validateEntries['check_INVPV'] = fun_app8.check_dict_input(INVPV_data, optionsKeysUploadedINV)
                except:
                    st.error("Error al cargar archivo **YAML** (.yaml)", icon="🚨")

            else:
                st.error("Cargar **Datos del Inversor**", icon="🚨")

            if validateEntries['check_DATA'] and validateEntries['check_PV'] and validateEntries['check_INVPV']:

                st.session_state['dictDataOnGrid'] = {
                    'df_data': df_data,
                    'PV_data': PV_data,
                    'INVPV_data': fun_app8.getParametersINV_data(INVPV_data),
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
                st.text(validateEntries['check_INVPV'])


    if st.session_state['dictDataOnGrid'] is not None:
        #
        COMP_data = fun_app8.processComponentData(PV_data=st.session_state['dictDataOnGrid']['PV_data'],
                                                  INVPV_data=st.session_state['dictDataOnGrid']['INV_data'],
                                                  PVs=st.session_state['dictDataOnGrid']['PVs'],
                                                  PVp=st.session_state['dictDataOnGrid']['PVp'],
                                                  V_PCC=st.session_state['dictDataOnGrid']['V_PCC'])

        df_out = fun_app8.solarGenerationOnGrid(**st.session_state['dictDataOnGrid'])
        bytesFile = fun_app8.toExcel(df=df_out, dict_params=COMP_data)

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
                    df_data = pd.read_excel(uploaderXlsx, sheet_name="Dataframe")
                    COMP_data = pd.read_excel(uploaderXlsx, sheet_name="Params").to_dict(orient="records")[0]
                    timeInfo = fun_app8.getTimeData(df_data)



                    for i in range(0,len(timeInfo["years"])):
                        st.text(timeInfo["months"][i])

                        if len(timeInfo["months"][i]) == 12:
                            # Analisis anual
                            st.text("Analisis anual")
                        else:
                            # Analisis mensual

                            for j in range(0,len(timeInfo["months"][i]),1):

                                st.text(f"{timeInfo['years'][i]} {dictMonths[timeInfo['months'][i][j]].capitalize()}")

                                df_month = df_data[(df_data["dates (Y-M-D hh:mm:ss)"].dt.year == timeInfo["years"][i]) & (df_data["dates (Y-M-D hh:mm:ss)"].dt.month == timeInfo["months"][i][j])]

                                dict_reportParams = fun_app8.getReportParams(df_month=df_month, deltaMinutes=timeInfo["deltaMinutes"], timeDeltaType="month")

                                for key in dict_reportParams:
                                    st.text(f"{dict_reportParams[key]['label']}: {key}{dict_reportParams[key]['unit']}= {dict_reportParams[key]['value']}")

                                    
                                st.text("-----------------------------------------------------------------------------")
  
                except:
                    st.error("Error al cargar archivo **EXCEL** (.xlsx)", icon="🚨")
            else:
                st.error("Cargar **Dataset generación Off-Grid**", icon="🚨")
    

        