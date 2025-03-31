# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import yaml

from funtions import general, fun_app8

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

dataKeyList = ["PV_data", "INVPV_data", "AERO_data", "INVAERO_data",
               "rho", "PVs", "PVp", "V_PCC",
               "columnsOptionsData", "numberPhases", "componentInTheProject",
               "generationType"]

listGenerationOptions = general.getListGenerationOptions(generationType="OnGrid")

showOutputPV = [f"{params_PV[elm]['label']}{params_PV[elm]['unit']}: {params_PV[elm]['description']}" for elm in ["Voc", "Isc", "Impp", "Vmpp", "Pmpp"]]

selectDataEntryOptions = ["📝 Ingresar datos del proyecto",
                          "💾 Cargar archivo de proyecto XLSX",
                          "💾 Cargar archivo de componentes YAML"]

#%% session state

if 'check_DATA' not in st.session_state:
    st.session_state['check_DATA'] = False

if 'check_PV' not in st.session_state:
    st.session_state['check_PV'] = False

if 'check_INVPV' not in st.session_state:
    st.session_state['check_INVPV'] = False

if 'check_AERO' not in st.session_state:
    st.session_state['check_AERO'] = False

if 'check_INVAERO' not in st.session_state:
    st.session_state['check_INVAERO'] = False

if 'dictDataOnGrid' not in st.session_state:
    st.session_state['dictDataOnGrid'] = None

#%% main

st.markdown("# 🔌 Generación On-Grid")

tab1, tab2, tab3 = st.tabs(["📑 Información", "💾 Entrada de datos", "📝 Análisis de resultados"])

with tab1:
    with st.expander("**Marco teórico**"):
        st.markdown("Marco teórico")
    with st.expander("**Ingreso de datos**"):
        st.markdown("Ingreso de datos")

with tab2:
    generationOptions = None

    with st.container(border=True):
        projectDataEntry = st.selectbox(label="Opciones de ingreso de datos", options=selectDataEntryOptions,
                                        index=None, placeholder="Selecciona una opción")
        
        if projectDataEntry == selectDataEntryOptions[0]:
            uploadedYamlPV, uploadedYamlINV_PV = None, None
            uploadedYamlAERO, uploadedYamlINV_AERO = None, None
            uploadedXlsxDATA = None
            PVs, PVp, rho, V_PCC = None, None, None, None

            generationOptions = st.multiselect(label="Opciones de generación eléctrica", options=listGenerationOptions, default=listGenerationOptions[0])

            with st.container(border=True):
                st.markdown("📋 **:blue[Datos de carga, temperatura de operación y potencial energetico del sitio:]**")
                uploadedXlsxDATA = st.file_uploader(label="**Cargar archivo EXCEL**", type=["xlsx"], key='uploadedYamlDATA')

                if listGenerationOptions[1] in generationOptions:
                    rho = general.widgetNumberImput(dictParam=params_AERO["rho"], key="rho", disabled=False)
                else:
                    rho = None
                
        with st.form("On-Grid", border=False):

            if projectDataEntry == selectDataEntryOptions[0]:
                if listGenerationOptions[0] in generationOptions:
                    with st.container(border=True):
                        st.markdown("☀️ **:blue[Generación de energía solar]**")
                        with st.container(border=True):
                            st.markdown(f"{dict_components['PV']['emoji']} **:blue[{dict_components['PV']['name']}:]**")
                            uploadedYamlPV = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlPV')

                            st.markdown("🧑‍🔧 Conexión de los módulos")
                            col1, col2 = st.columns(2)

                            with col1:
                                PVs = general.widgetNumberImput(dictParam=params_AERO["PVs"], key="PVs", disabled=False)
                            with col2:
                                PVp = general.widgetNumberImput(dictParam=params_AERO["PVp"], key="PVp", disabled=False)
                        
                        with st.container(border=True):
                            st.markdown(f"{dict_components['INVPV']['emoji']} **:blue[{dict_components['INVPV']['name']}:]**")
                            uploadedYamlINV_PV = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlINV_PV')

                if listGenerationOptions[1] in generationOptions:
                    with st.container(border=True):
                        st.markdown("🌀 **:green[Generación de energía eólica]**")
                        with st.container(border=True):
                            st.markdown(f"{dict_components['AERO']['emoji']} **:green[{dict_components['AERO']['name']}:]**")
                            uploadedYamlAERO = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlAERO')

                        with st.container(border=True):
                            st.markdown(f"{dict_components['INVAERO']['emoji']} **:green[{dict_components['INVAERO']['name']}:]**")
                            uploadedYamlINV_AERO = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlINV_AERO')

                with st.container(border=True):
                    st.markdown("⚡ **PCC (Punto de conexión común**")
                    V_PCC = st.number_input(label="Tensión del punto de conexión común", value=127.0, placeholder="Ingrese un valor",
                                            format="%0.1f", step=None, min_value=0.0, max_value=1000.0)
                    
            elif projectDataEntry == selectDataEntryOptions[1]:
                with st.container(border=True):
                    st.markdown("💾 **:blue[Cargar archivo de proyecto On-Grid]**")
                    uploadedXlsxPROJECT = st.file_uploader(label="**Cargar archivo XLSX**", type=["xlsx"], key="uploadedXlsxPROJECT")


            submitted = st.form_submit_button("Aceptar")

            if submitted:

                if projectDataEntry == selectDataEntryOptions[0]:
                    checkProject, validateEntries = False, general.initializeDictValidateEntries(generationType="OnGrid")
                    componentInTheProject = general.getDictComponentInTheProject(generationOptions)
                    checkUploaded = general.getErrorForMissingComponent(uploadedYamlPV, uploadedYamlINV_PV, None,
                                                                        uploadedYamlAERO, uploadedYamlINV_AERO, None,
                                                                        uploadedXlsxDATA, None, None,
                                                                        "OnGrid", componentInTheProject)
                    
                    if checkUploaded:
                        validateEntries["check_DATA"], df_data, columnsOptionsData = general.getDataValidation(uploadedXlsxDATA, componentInTheProject)

                        if len(generationOptions) != 0:
                            PV_data, INVPV_data  = None, None
                            AERO_data, INVAERO_data = None, None

                            if componentInTheProject["generationPV"]:       # Generación PV
                                validateEntries, PV_data, INVPV_data = general.getDataOnGridValidation(uploadedYamlPV, uploadedYamlINV_PV, validateEntries, "PV")
                        
                            if componentInTheProject["generationAERO"]:     # Generación AERO
                                validateEntries, AERO_data, INVAERO_data = general.getDataOnGridValidation(uploadedYamlAERO, uploadedYamlINV_AERO, validateEntries, "AERO")

                            validateComponents = general.getDictValidateComponent(validateEntries=validateEntries, generationType="OnGrid")
                            checkProject = general.getCheckValidateGeneration(**componentInTheProject, **validateComponents,
                                                                              validateGE=None, validateBAT=None,
                                                                              generationType="OnGrid")
                            
                            if checkProject:
                                numberPhases = general.getNumberPhases(INVPV_data=INVPV_data, INVAERO_data=INVAERO_data, GE_data=None)

                                if numberPhases is not None:
                                    st.session_state["dictDataOnGrid"] = {
                                        "df_data": df_data,
                                        "PV_data": PV_data,
                                        "INVPV_data": fun_app8.getParametersINV_data(INVPV_data),
                                        "AERO_data": AERO_data,
                                        "INVAERO_data": fun_app8.getParametersINV_data(INVAERO_data),
                                        "rho": rho,
                                        "PVs": PVs,
                                        "PVp": PVp,
                                        "V_PCC": V_PCC,
                                        "columnsOptionsData": columnsOptionsData,
                                        "numberPhases": numberPhases,
                                        "componentInTheProject": componentInTheProject,
                                        "generationType": "OnGrid"
                                        }
                                else:
                                    st.error("Incompatibilidad de conexión entre inversores", icon="🚨")

                elif projectDataEntry == selectDataEntryOptions[1]:
                    
                    df_data = pd.read_excel(uploadedXlsxPROJECT, sheet_name="Data")
                    TOTAL_data = pd.read_excel(uploadedXlsxPROJECT, sheet_name="Params").to_dict(orient="records")[0]
                    TOTAL_data = general.getFixFormatDictParams(TOTAL_data, dataKeyList)
                    TOTAL_data["df_data"] = df_data

                    st.session_state["dictDataOnGrid"] = {**{"df_data": df_data}, **TOTAL_data}

                    
    if st.session_state["dictDataOnGrid"] is not None:

        df_onGrid = fun_app8.generationOnGrid(**st.session_state["dictDataOnGrid"])
        TOTAL_data, bytesFileExcelProject = fun_app8.getBytesFileExcelProjectOnGrid(dictDataOnGrid=st.session_state["dictDataOnGrid"], dataKeyList=dataKeyList)
        bytesFileYamlComponets = general.getBytesFileYamlComponentsProject(dictDataProject=st.session_state["dictDataOnGrid"])
        bytesFileExcelResults = general.toExcelResults(df=df_onGrid, dictionary=TOTAL_data, df_sheetName="Result", dict_sheetName="Params")

        with st.container(border=True):
            st.markdown("**Archivos de opciones de ingreso de datos:**")
            df_downloadXLSX = st.download_button(
                label="💾 Descargar **:blue[Archivo de proyecto On-Grid] XLSX**",
                data=bytesFileExcelProject,
                file_name=general.nameFileHead(name="project_OnGrid.xlsx"),
                mime="xlsx")
            
            dict_downloadYAML = st.download_button(
                label="💾 Descargar **:blue[Archivo de componentes del proyecto On-Grid] YAML**",
                data=bytesFileYamlComponets,
                file_name=general.nameFileHead(name="components_OnGrid.yaml"),
                mime="text/yaml")
            
        with st.container(border=True):
            st.markdown("**Archivos de resultados:**")
            df_download = st.download_button(
                label="📄 Descargar **:blue[Archivo de resultado On-Grid] XLSX**",
                data=bytesFileExcelResults,
                file_name=general.nameFileHead(name="results_OnGrid.xlsx"),
                mime='xlsx')
            
        st.session_state["dictDataOnGrid"] = None
        
with tab3:
    st.session_state["dictDataOnGrid"] = None

    with st.container(border=True):
        uploaderXlsx = st.file_uploader(label="**Cargar archivo EXCEL**", type=["xlsx"], key='uploaderXlsx')  
        submitted = st.button("Aceptar")

        if submitted:
            if uploaderXlsx is not None:
                try:
                    df_data = pd.read_excel(uploaderXlsx, sheet_name="Result")
                    timeInfo = general.getTimeData(df_data)

                    df_dailyResult, df_monthlyResult, df_annualResult = None, None, None

                    df_dailyResult = general.getAnalysisInTime(df_data, timeInfo["deltaMinutes"], "day", "OnGrid")
                    df_monthlyResult = general.getAnalysisInTime(df_data, timeInfo["deltaMinutes"], "month", "OnGrid")
                    df_annualResult = general.getAnalysisInTime(df_data, timeInfo["deltaMinutes"], "year", "OnGrid")
                    bytesFile = general.toExcelAnalysis(df_data, df_dailyResult, df_monthlyResult, df_annualResult)

                    df_download = st.download_button(
                        label="💾 Descargar **:blue[Análisis] XLSX**",
                        data=bytesFile,
                        file_name=general.nameFileHead(name="Analysis_OnGrid.xlsx"),
                        mime='xlsx')

                except:
                    st.error("Error al cargar archivo **EXCEL** (.xlsx)", icon="🚨")
            else:
                st.error("Cargar **Dataset generación Off-Grid**", icon="🚨")