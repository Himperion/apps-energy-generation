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

with open("files//[AERO] - params.yaml", 'r') as archivo:
    params_AERO = yaml.safe_load(archivo)

optionsColumnsUploadedDATA = {
    "Dates": ("dates (Y-M-D hh:mm:ss)"),
    "Geff" : ("Gef(W/m^2)", "Gef(W/m²)", "Gin(W/m²)", "Gin(W/m^2)"),
    "Toper" : ("Toper(°C)"),
    "Load" : ("Load(kW)")
}

dict_phases = {
    "Monofásico": {"Num": 1, "label": "1️⃣ Monofásico"},
    "Trifásico": {"Num": 3, "label": "3️⃣ Trifásico"}
}

itemsOptionsColumnsDf = {
    "DATA": {
        "Dates": ("dates (Y-M-D hh:mm:ss)"),
        "Load" : ("Load(kW)")
    },
    "PV" : {
        "Geff" : ["Gef(W/m^2)", "Gef(W/m²)", "Gin(W/m²)", "Gin(W/m^2)"],
        "Toper" : ["Toper(°C)"]
    },
    "AERO" : {
        "Vwind" : ["Vwind(m/s)", "Vwind 10msnm(m/s)", "Vwind 50msnm(m/s)"]
    }
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

optionsKeysUploadedINVPV = [
    "Pac_max",
    "Vac_max",
    "Vac_min",
    "Vac_nom",
    "Vbb_nom",
    "efficiency_max",
    "grid_type",
    "phases"
]

optionsKeysUploadedAERO = [
    "D",
    "V_in",
    "V_nom",
    "V_max",
    "P_nom"
]

optionsKeysUploadedINVAERO = optionsKeysUploadedINVPV

listGenerationOptions = ["Generación solar", "Generación eólica"]

showOutputPV = [f"{params_PV[elm]['label']}{params_PV[elm]['unit']}: {params_PV[elm]['description']}" for elm in ["Voc", "Isc", "Impp", "Vmpp", "Pmpp"]]

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

st.markdown("# 🔌 Generación On-Grid")

tab1, tab2, tab3 = st.tabs(["📑 Marco teórico", "💾 Entrada de datos", "📝 Análisis"])

with tab2:
    generationOptions = st.multiselect(label="Opciones de generación eléctrica", options=listGenerationOptions, default=listGenerationOptions[0])

    with st.container(border=True):
        st.markdown("📋 **:blue[Datos de carga, temperatura de operación y potencial energetico del sitio:]**")

        uploadedXlsxDATA = st.file_uploader(label="**Cargar archivo EXCEL**", type=["xlsx"], key='uploadedYamlDATA')

        if listGenerationOptions[1] in generationOptions:
            rho = fun_app8.get_widget_number_input(label=fun_app8.get_label_params(dict_param=params_AERO["rho"]),
                                                   variable=params_AERO["rho"]["number_input"], disabled=False)
        else:
            rho = None
        
    with st.form("On-Grid", border=False):

        validateEntries = {
                'check_DATA': False,
                'check_PV': False,
                'check_INV_PV': False,
                'check_AERO': False,
                'check_INV_AERO': False,
            }
        
        PVs, PVp = None, None
        
        if listGenerationOptions[0] in generationOptions:
            with st.container(border=True):
                st.markdown("☀️ **:blue[Generación de energía solar]**")
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
                st.markdown("🌀 **:green[Generación de energía eólica]**")
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
                validateEntries['check_DATA'], df_data, columnsOptionsData = fun_app8.getDataValidation(uploadedXlsxDATA, generationOptions, itemsOptionsColumnsDf, listGenerationOptions)
            else:
                st.error("Cargar **Datos de carga, temperatura de operación y potencial solar del sitio**", icon="🚨")

            if len(generationOptions) != 0:
                PV_data, INVPV_data, AERO_data, INVAERO_data = None, None, None, None

                if listGenerationOptions[0] in generationOptions:   # Generación PV
                    validateEntries['check_PV'], validateEntries['check_INV_PV'], PV_data, INVPV_data = fun_app8.getDataCompValidation(uploadedYamlPV, uploadedYamlINV_PV, optionsKeysUploadedPV, optionsKeysUploadedINVPV)
                    
                if listGenerationOptions[1] in generationOptions:   # Generación AERO
                    validateEntries['check_AERO'], validateEntries['check_INV_AERO'], AERO_data, INVAERO_data = fun_app8.getDataCompValidation(uploadedYamlAERO, uploadedYamlINV_AERO, optionsKeysUploadedAERO, optionsKeysUploadedINVAERO)

            else:
                st.error("Ingresar **Opciones de generación eléctrica**", icon="🚨")

            if fun_app8.getConditionValidateEntries(validateEntries):
                numberPhases = fun_app8.getNumberPhases(INVPV_data, INVAERO_data)

                if numberPhases is not None:

                    st.session_state['dictDataOnGrid'] = {
                        'df_data': df_data,
                        'PV_data': PV_data,
                        'INVPV_data': fun_app8.getParametersINV_data(INVPV_data),
                        'AERO_data': AERO_data,
                        'INVAERO_data': fun_app8.getParametersINV_data(INVAERO_data),
                        'rho': rho,
                        'PVs': PVs,
                        'PVp': PVp,
                        'V_PCC': V_PCC,
                        'columnsOptionsData': columnsOptionsData,
                        'params_PV': params_PV,
                        'rename_PV': rename_PV,
                        'showOutputPV': showOutputPV,
                        'numberPhases': numberPhases
                    }
                else:
                    st.error("Incompatibilidad de conexión entre inversores", icon="🚨")

    if st.session_state['dictDataOnGrid'] is not None:
        dictProcessComponentData = fun_app8.getImputProcessComponentData(st.session_state['dictDataOnGrid'])
        COMP_data = fun_app8.processComponentData(**dictProcessComponentData)
        df_out = fun_app8.generationOnGrid(**st.session_state['dictDataOnGrid'])

        st.dataframe(df_out)
        bytesFile = fun_app8.toExcelResults(df=df_out, dict_params=COMP_data)

        df_download = st.download_button(
            label="📄 Descargar **:blue[Dataset] XLSX**",
            data=bytesFile,
            file_name=fun_app8.name_file_head(name="dataset_OnGrid.xlsx"),
            mime='xlsx')
        
with tab3:
    st.session_state['check_DATA'] = False
    st.session_state['check_PV'] = False
    st.session_state['check_INV_PV'] = False
    st.session_state['check_AERO'] = False
    st.session_state['check_INV_AERO'] = False
    st.session_state['dictDataOnGrid'] = None
        
    with st.container(border=True):
        uploaderXlsx = st.file_uploader(label="**Cargar archivo EXCEL**", type=["xlsx"], key='uploaderXlsx')  

        submitted = st.button("Aceptar")

        if submitted:
            if uploaderXlsx is not None:
                try:
                    df_data = pd.read_excel(uploaderXlsx, sheet_name="Data")
                    #COMP_data = pd.read_excel(uploaderXlsx, sheet_name="Params").to_dict(orient="records")[0]
                    timeInfo = fun_app8.getTimeData(df_data)


                    #PV_data, INVPV_data, AERO_data, INVAERO_data, PVs, PVp, V_PCC = fun_app8.getDictParams(COMP_data)

                    df_dailyResult, df_monthlyResult, df_annualResult = None, None, None

                    df_dailyResult = fun_app8.getAnalysisInTime(df_data, timeInfo["deltaMinutes"], "day")
                    df_monthlyResult = fun_app8.getAnalysisInTime(df_data, timeInfo["deltaMinutes"], "month")
                    df_annualResult = fun_app8.getAnalysisInTime(df_data, timeInfo["deltaMinutes"], "year")

                    bytesFile = fun_app8.toExcelAnalysis(df_data, df_dailyResult, df_monthlyResult, df_annualResult)

                    df_download = st.download_button(
                        label="📄 Descargar **:blue[Análisis] XLSX**",
                        data=bytesFile,
                        file_name=fun_app8.name_file_head(name="Analysis_OnGrid.xlsx"),
                        mime='xlsx')

                except:
                    st.error("Error al cargar archivo **EXCEL** (.xlsx)", icon="🚨")
            else:
                st.error("Cargar **Dataset generación Off-Grid**", icon="🚨")
     