# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import yaml
from datetime import datetime

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

dir_components = "files//[DATA] - Components.xlsx"

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
                          "💾 Cargar archivo de componentes YAML",
                          "🖥️ Ingresar datos del proyecto con el banco de componentes"]

#%% session state

if 'dictDataOnGrid' not in st.session_state:
    st.session_state['dictDataOnGrid'] = None

#%% main

st.sidebar.link_button("Ir a la app de herramientas", "https://app-nasa-power.streamlit.app/", icon="🔧")

st.markdown("# 🔌 Generación On-Grid")

tab1, tab2, tab3, tab4 = st.tabs(["📑 Información", "💾 Entrada de datos", "📝 Análisis de resultados",  "👨‍🏫 Visualización de resultados"])

with tab1:
    with st.expander(":violet-badge[**Marco teórico**]", icon="✏️"):
        st.markdown("Los sistemas híbridos combinan diferentes fuentes de energía renovable para mejorar el suministro de energía. Al integrar tecnologías fotovoltaicas y eólicas, se puede aprovechar la energía del sol y del viento, compensando las limitaciones de cada una y proporcionando una solución más robusta y versátil. El sistema hibrido On-Grid está configurado de forma que se reduzca el consumo o que se puedan inyectar los excedentes a la red. Para este sistema se usa un inversor AC/DC integrado a la salida del aerogenerador priorizando la compatibilidad con los inversores DC/AC On-Grid disponibles en el mercado.")

        col1, col2, col3 = st.columns( [0.2, 0.6, 0.2])
        with col2:
            st.image("images//app8_img2.png")
        
    with st.expander(":orange-badge[**Recomendaciones**]", icon="⚠️"):
        st.markdown("Antes de subir los archivos de los componentes, es necesario que consulte las fichas técnicas de cada componente del sistema.")
        st.markdown("Es importante verificar lo siguiente:")
        st.markdown(" - La potencia nominal del aerogenerador no debe superar la potencia máxima del inversor eólico.")
        st.markdown(" - El arreglo de paneles fotovoltaicos debe mantenerse dentro de los límites de potencia máxima del inversor fotovoltaico.")
        st.markdown(" - Las tensiones de los inversores fotovoltaico y eólico deben coincidir con la del punto de conexión y tener el mismo número de fases.")

with tab2:
    generationOptions = None

    with st.container(border=True):
        projectDataEntry = st.selectbox(label="Opciones de ingreso de datos", options=selectDataEntryOptions,
                                        index=None, placeholder="Selecciona una opción")
        
        if projectDataEntry == selectDataEntryOptions[0] or projectDataEntry == selectDataEntryOptions[3]:
            uploadedYamlPV, uploadedYamlINV_PV = None, None
            uploadedYamlAERO, uploadedYamlINV_AERO = None, None
            uploadedXlsxDATA = None
            PVs, PVp, rho, V_PCC = None, None, None, None

            generationOptions = st.multiselect(label="Opciones de generación eléctrica", options=listGenerationOptions, default=None)

            with st.container(border=True):
                uploadedXlsxDATA = st.file_uploader(label="📋 **Cargar archivo de datos de carga, temperatura de operación y potencial energetico del sitio EXCEL**", type=["xlsx"], key='uploadedYamlDATA')

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
                                PVs = general.widgetNumberImput(dictParam=params_PV["PVs"], key="PVs", disabled=False)
                            with col2:
                                PVp = general.widgetNumberImput(dictParam=params_PV["PVp"], key="PVp", disabled=False)
                        
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
                    V_PCC = st.number_input(label="⚡ **Tensión PCC (punto de conexión común)**", value=127.0, placeholder="Ingrese un valor",
                                            format="%0.1f", step=None, min_value=0.0, max_value=1000.0)
                    
            elif projectDataEntry == selectDataEntryOptions[1]:
                with st.container(border=True):
                    uploadedXlsxPROJECT = st.file_uploader(label="**Cargar archivo :blue[Project_OnGrid] XLSX**", type=["xlsx"], key="uploadedXlsxPROJECT")

            elif projectDataEntry == selectDataEntryOptions[2]:
                uploadedXlsxDATA, uploadedYamlCOMPONENTS = None, None

                with st.container(border=True):
                    uploadedXlsxDATA = st.file_uploader(label="📋 **Cargar archivo de datos de carga, temperatura de operación y potencial energético del sitio EXCEL**", type=["xlsx"], key="uploadedXlsxDATA")

                with st.container(border=True):
                    uploadedYamlCOMPONENTS = st.file_uploader(label="💾 **Cargar archivo de componentes On-Grid: :blue[Components_OnGrid] YAML**", type=["yaml", "yml"], key="uploadedYamlCOMPONENTS")
        
            elif projectDataEntry == selectDataEntryOptions[3]:
                selected_PV, selected_INVPV = None, None
                selected_AERO, selected_INVAERO = None, None

                if listGenerationOptions[0] in generationOptions:
                    df_PV = general.getDataComponent(sheetLabel=dict_components["PV"]["sheet_label"], dir=dir_components, onLine=True)
                    df_PV = df_PV.drop(columns=["datasheet"])
                    df_INVPV = general.getDataComponent(sheetLabel=dict_components["INVPV"]["sheet_label"], dir=dir_components, onLine=True)
                    df_INVPV = df_INVPV.drop(columns=["datasheet"])
                    df_INVPV = df_INVPV[df_INVPV["grid_type"] == "On-Grid"]
                    
                    with st.container(border=True):
                        st.markdown("☀️ **:blue[Generación de energía solar]**")

                        with st.container(border=True):
                            st.markdown(f"**:blue[{dict_components['PV']['label']}]**")
                            selected_PV = general.dataframe_AgGrid(dataframe=df_PV, height=250)

                        with st.container(border=True):
                            st.markdown("🧑‍🔧 **:blue[Conexión de los módulos]**")
                            col1, col2 = st.columns(2)

                            with col1:
                                PVs = general.widgetNumberImput(dictParam=params_PV["PVs"], key="PVs", disabled=False)
                            with col2:
                                PVp = general.widgetNumberImput(dictParam=params_PV["PVp"], key="PVp", disabled=False)

                        with st.container(border=True):
                            st.markdown(f"**:blue[{dict_components['INVPV']['label']}]**")
                            selected_INVPV = general.dataframe_AgGrid(dataframe=df_INVPV, height=250)

                if listGenerationOptions[1] in generationOptions:
                    df_AERO = general.getDataComponent(sheetLabel=dict_components["AERO"]["sheet_label"], dir=dir_components, onLine=True)
                    df_AERO = df_AERO.drop(columns=["datasheet"])
                    df_INVAERO = general.getDataComponent(sheetLabel=dict_components["INVAERO"]["sheet_label"], dir=dir_components, onLine=True)
                    df_INVAERO = df_INVAERO.drop(columns=["datasheet"])
                    df_INVAERO = df_INVAERO[df_INVAERO["grid_type"] == "On-Grid"]
                    
                    with st.container(border=True):
                        st.markdown("🌀 **:green[Generación de energía eólica]**")

                        with st.container(border=True):
                            st.markdown(f"**:green[{dict_components['AERO']['label']}]**")
                            selected_AERO = general.dataframe_AgGrid(dataframe=df_AERO, height=250)

                        with st.container(border=True):
                            st.markdown(f"**:green[{dict_components['INVAERO']['label']}]**")
                            selected_INVAERO = general.dataframe_AgGrid(dataframe=df_INVAERO, height=250)

                with st.container(border=True):
                    V_PCC = st.number_input(label="⚡ **Tensión PCC (punto de conexión común)**", value=127.0, placeholder="Ingrese un valor",
                                            format="%0.1f", step=None, min_value=0.0, max_value=1000.0)
                
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
                            PV_data, INVPV_data, AERO_data, INVAERO_data  = None, None, None, None

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

                elif projectDataEntry == selectDataEntryOptions[2]:
                    df_data, dictDataOnGrid = None, {}

                    if uploadedXlsxDATA is not None:
                        df_data = pd.read_excel(uploadedXlsxDATA)
                    else:
                        st.warning("Cargar archivo **XLSX** (.xlsx)", icon="⚠️")

                    if uploadedYamlCOMPONENTS is not None:
                        dictDataOnGrid = yaml.safe_load(uploadedYamlCOMPONENTS)
                    else:
                        st.warning("Cargar archivo  de componentes OffGrid **YAML** (.yaml)", icon="⚠️")

                    if len(dictDataOnGrid) > 0:
                        st.session_state["dictDataOnGrid"] = {**{"df_data": df_data}, **dictDataOnGrid}

                elif projectDataEntry == selectDataEntryOptions[3]:
                    if len(generationOptions) != 0:
                        PV_data, INVPV_data, AERO_data, INVAERO_data  = None, None, None, None
                        checkProject, validateEntries = False, general.initializeDictValidateEntries(generationType="OnGrid")
                        componentInTheProject = general.getDictComponentInTheProject(generationOptions)
                        
                        if uploadedXlsxDATA is not None:
                            nameFileXlsxDATA = uploadedXlsxDATA.name
                            validateEntries["check_DATA"], df_data, columnsOptionsData = general.getDataValidation(uploadedXlsxDATA, componentInTheProject)

                        if validateEntries["check_DATA"]:
                            if componentInTheProject["generationPV"]:       # Generación PV
                                if selected_PV is not None and selected_INVPV is not None:
                                    selected_PV.reset_index(drop=True, inplace=True)
                                    selected_INVPV.reset_index(drop=True, inplace=True)
                                    
                                    PV_data = general.getDictDataRow(selected_row=selected_PV, key="PV")
                                    INVPV_data = general.getDictDataRow(selected_row=selected_INVPV, key="INVPV")

                                    validateEntries["check_PV"], validateEntries["check_INVPV"] = True, True
                                else:
                                    if selected_PV is None:
                                        st.warning(f"**Falta agregar componente: :blue[{dict_components['PV']['name']}]**", icon="⚠️")
                                    if selected_INVPV is None:
                                        st.warning(f"**Falta agregar componente: :blue[{dict_components['INVPV']['name']}]**", icon="⚠️")

                            if componentInTheProject["generationAERO"]:     # Generación AERO
                                if selected_AERO is not None and selected_INVAERO is not None:
                                    selected_AERO.reset_index(drop=True, inplace=True)
                                    selected_INVAERO.reset_index(drop=True, inplace=True)

                                    AERO_data = general.getDictDataRow(selected_row=selected_AERO, key="AERO")
                                    INVAERO_data = general.getDictDataRow(selected_row=selected_INVAERO, key="INVAERO")

                                    validateEntries["check_AERO"], validateEntries["check_INVAERO"] = True, True
                                else:
                                    if selected_AERO is None:
                                        st.warning(f"**Falta agregar componente: :blue[{dict_components['AERO']['name']}]**", icon="⚠️")
                                    if selected_INVAERO is None:
                                        st.warning(f"**Falta agregar componente: :blue[{dict_components['INVAERO']['name']}]**", icon="⚠️")

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
                        else:
                            st.warning(f"**Debe ingresar archivo de datos de carga, temperatura de operación y potencial energético del sitio**", icon="⚠️")
                    else:
                        st.warning("**Debe ingresar por lo menos una opción de generación**", icon="⚠️")

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
                file_name=general.nameFileHead(name="Project_OnGrid.xlsx"),
                mime="xlsx",
                on_click="ignore")
            
            dict_downloadYAML = st.download_button(
                label="💾 Descargar **:blue[Archivo de componentes del proyecto On-Grid] YAML**",
                data=bytesFileYamlComponets,
                file_name=general.nameFileHead(name="Components_OnGrid.yaml"),
                mime="text/yaml",
                on_click="ignore")
            
        with st.container(border=True):
            st.markdown("**Archivos de resultados:**")

            df_download = st.download_button(
                label="📄 Descargar **:blue[Archivo de resultado On-Grid] XLSX**",
                data=bytesFileExcelResults,
                file_name=general.nameFileHead(name="Results_OnGrid.xlsx"),
                mime='xlsx',
                on_click="ignore")
            
        st.session_state["dictDataOnGrid"] = None
        
with tab3:
    st.session_state["dictDataOnGrid"] = None
    flagSubmittedAnalysis, uploaderXlsx = False, None

    with st.container(border=True):
        uploaderXlsx = st.file_uploader(label="**Cargar archivo :blue[Results_OnGrid] EXCEL**", type=["xlsx"], key='uploaderXlsx')  
        submitted = st.button("Aceptar")

        if submitted:
            if uploaderXlsx is not None:
                flagSubmittedAnalysis = True
            else:
                st.warning("**Cargar archivo :blue[Results_OnGrid]**", icon="⚠️")

    if flagSubmittedAnalysis:
        nameFileXlsx = uploaderXlsx.name
        if nameFileXlsx.split(" ")[1].split(".")[0] == "Results_OnGrid":
            try:
                df_data = pd.read_excel(uploaderXlsx, sheet_name="Result")
                dict_params = pd.read_excel(uploaderXlsx, sheet_name="Params").to_dict(orient="records")[0]
                timeInfo = general.getTimeData(df_data)

                df_dailyResult, df_monthlyResult, df_annualResult = None, None, None

                df_dailyResult = general.getAnalysisInTime(df_data, timeInfo["deltaMinutes"], "day", "OnGrid")
                df_monthlyResult = general.getAnalysisInTime(df_data, timeInfo["deltaMinutes"], "month", "OnGrid")
                df_annualResult = general.getAnalysisInTime(df_data, timeInfo["deltaMinutes"], "year", "OnGrid")
                bytesFile = general.toExcelAnalysis(df_data, dict_params, df_dailyResult, df_monthlyResult, df_annualResult)

                st.download_button(
                    label="💾 Descargar **:blue[Análisis On-Grid] XLSX**",
                    data=bytesFile,
                    file_name=general.nameFileHead(name="Analysis_OnGrid.xlsx"),
                    mime="xlsx",
                    on_click="ignore"
                    )

            except:
                st.error("Error al cargar archivo **EXCEL** (.xlsx)", icon="🚨")
        else:
            st.error(f"**Nombre de archivo no valido :blue[{nameFileXlsx}]**", icon="🚨")

with tab4:
    st.session_state["dictDataOnGrid"] = None
    uploaderAnalysisXlsx = None

    with st.container(border=True):
        uploaderAnalysisXlsx = st.file_uploader(label="**Cargar archivo :blue[Analysis_OnGrid] EXCEL**", type=["xlsx"], key="uploaderAnalysisXlsx")  
    
    if uploaderAnalysisXlsx is not None:
        nameFileXlsx = uploaderAnalysisXlsx.name
        if nameFileXlsx.split(" ")[1].split(".")[0] == "Analysis_OnGrid":
            df_data, df_dailyAnalysis, df_monthlyAnalysis, df_annualAnalysis = None, None, None, None
            sheetNamesXls, PARAMS_data, timeInfo = [], None, None

            try:
                xls = pd.ExcelFile(uploaderAnalysisXlsx)
                sheetNamesXls = xls.sheet_names
                if "Data" in sheetNamesXls:
                    df_data = pd.read_excel(xls, sheet_name="Data")
                    df_data["dates (Y-M-D hh:mm:ss)"] = pd.to_datetime(df_data["dates (Y-M-D hh:mm:ss)"])
                if "DailyAnalysis" in sheetNamesXls:
                    df_dailyAnalysis = pd.read_excel(xls, sheet_name="DailyAnalysis")
                    df_dailyAnalysis["dates (Y-M-D hh:mm:ss)"] = pd.to_datetime(df_dailyAnalysis["dates (Y-M-D hh:mm:ss)"])
                if "MonthlyAnalysis" in sheetNamesXls:
                    df_monthlyAnalysis = pd.read_excel(xls, sheet_name="MonthlyAnalysis")
                    df_monthlyAnalysis["dates (Y-M-D hh:mm:ss)"] = pd.to_datetime(df_monthlyAnalysis["dates (Y-M-D hh:mm:ss)"])
                if "AnnualAnalysis" in sheetNamesXls:
                    df_annualAnalysis = pd.read_excel(xls, sheet_name="AnnualAnalysis")
                    df_annualAnalysis["dates (Y-M-D hh:mm:ss)"] = pd.to_datetime(df_annualAnalysis["dates (Y-M-D hh:mm:ss)"], format="%Y")
                if "Params" in sheetNamesXls:
                    PARAMS_data = pd.read_excel(xls, sheet_name="Params").to_dict(orient="records")[0]
                    PARAMS_data = general.getFixFormatDictParams(PARAMS_data, dataKeyList)
            except:
                st.error(f"**Error al cargar archivo :blue[{nameFileXlsx}]**", icon="🚨")

            if df_data is not None:
                timeInfo = general.getTimeData(df_data)

            if timeInfo is not None and PARAMS_data is not None:
                listTimeRanges = general.getListOfTimeRanges(deltaMinutes=timeInfo["deltaMinutes"])
                label_systems = general.getGenerationSystemsNotationLabel(**PARAMS_data["componentInTheProject"])

                tab1, tab2, tab3, tab4 = st.tabs(["🕛 Flujos de potencia", "📅 Análisis diario", "📆 Análisis mensual", "🗓️ Análisis anual"])

                with tab1:
                    with st.form("analysisTime", border=True):
                        col1, col2, col3 = st.columns([0.4, 0.4, 0.2], vertical_alignment="bottom")

                        with col1:
                            pf_date = st.date_input(label="Seleccionar fecha", min_value=timeInfo["dateIni"], max_value=timeInfo["dateEnd"], value=timeInfo["dateIni"])
                        with col2:
                            pf_time = st.selectbox(label="Seleccionar hora", options=listTimeRanges)
                        with col3:
                            submitted = st.form_submit_button("Aceptar")

                        if submitted:
                            pf_time = datetime.strptime(pf_time, '%H:%M:%S').time()     
                            
                            with st.container(border=True):
                                general.displayInstantResults(df_data, PARAMS_data, pf_date, pf_time, label_systems)

                with tab2:
                    if df_dailyAnalysis is not None:
                        dateIni = df_dailyAnalysis.loc[0, "dates (Y-M-D hh:mm:ss)"]
                        dateEnd = df_dailyAnalysis.loc[df_dailyAnalysis.index[-1], "dates (Y-M-D hh:mm:ss)"]

                        with st.form("analysisDaily", border=True):
                            with st.container(border=True):
                                col1, col2 = st.columns([0.8, 0.2], vertical_alignment="bottom")

                                with col1:
                                    day_imput = st.date_input(label="Seleccionar fecha", min_value=dateIni, max_value=dateEnd, value=dateIni)
                                with col2:
                                    submittedDaily = st.form_submit_button("Aceptar")

                            if submittedDaily:
                                fun_app8.displayDailyResults(df_data, df_dailyAnalysis, day=day_imput)
                    else:
                        pesLabel = "DailyAnalysis"
                        st.warning(f"**El archivo :blue[{nameFileXlsx}] no cuenta con datos: :blue[{pesLabel}]**", icon="⚠️")

                with tab3:
                    if df_dailyAnalysis is not None and df_monthlyAnalysis is not None:
                        listLabelsMonths = general.timeInfoMonthsGetLabels(timeInfoMonths=timeInfo["months"])
                        optionYearRange, optionMonthRange = None, None
                        flagSubmittedMonth = False

                        with st.container(border=True):
                            col1, col2 = st.columns([0.4, 0.6], vertical_alignment="center")

                            with col1:
                                optionYearRange = st.selectbox(label="Seleccionar año:", options=timeInfo["years"], index=None)

                            with col2:
                                if optionYearRange is not None:
                                    indexYear = timeInfo["years"].index(optionYearRange)

                                    with st.form("analysisMonth", border=False):
                                        col1, col2 = st.columns([0.6, 0.4], vertical_alignment="bottom")

                                        with col1:
                                            optionMonthRange = st.selectbox(label="Seleccionar mes:", options=listLabelsMonths[indexYear], index=None)
                                        with col2:
                                            submitted = st.form_submit_button("Aceptar")

                            if submitted:
                                if optionMonthRange is not None:
                                    flagSubmittedMonth = True
                                else:
                                    st.warning("**Ingresar mes**", icon="⚠️")

                        if flagSubmittedMonth:
                            fun_app8.displayMonthlyResults(df_data, df_dailyAnalysis, df_monthlyAnalysis, optionYearRange, optionMonthRange)
                    else:
                        if df_dailyAnalysis is None:
                            pesLabel = "DailyAnalysis"
                            st.warning(f"**El archivo :blue[{nameFileXlsx}] no cuenta con datos: :blue[{pesLabel}]**", icon="⚠️")
                        if df_monthlyAnalysis is None:
                            pesLabel = "MonthlyAnalysis"
                            st.warning(f"**El archivo :blue[{nameFileXlsx}] no cuenta con datos: :blue[{pesLabel}]**", icon="⚠️")

                with tab4:
                    if df_monthlyAnalysis is not None and df_annualAnalysis is not None:
                        flagSubmittedYear = False
                        listYears = timeInfo["years"]

                        with st.form("analysisYear", border=True):
                            col1, col2 = st.columns([0.6, 0.4], vertical_alignment="bottom")

                            with col1:
                                optionYearRange = st.selectbox(label="Seleccionar año:", options=listYears, index=None, key="optionYearRange")
                            with col2:
                                submitted = st.form_submit_button("Aceptar")

                            if submitted:
                                flagSubmittedYear = True

                        if flagSubmittedYear:
                            df_annualAnalysisFilter = df_annualAnalysis[df_annualAnalysis["dates (Y-M-D hh:mm:ss)"].dt.year == optionYearRange]
                            df_monthlyAnalysisFilter = df_monthlyAnalysis[df_monthlyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.year == optionYearRange]

                            fun_app8.displayAnnualResults(df_monthlyAnalysis, df_annualAnalysis, optionYearRange)
                    else:
                        if df_monthlyAnalysis is None:
                            pesLabel = "MonthlyAnalysis"
                            st.warning(f"**El archivo :blue[{nameFileXlsx}] no cuenta con datos: :blue[{pesLabel}]**", icon="⚠️")
                        if df_annualAnalysis is None:
                            pesLabel = "AnnualAnalysis"
                            st.warning(f"**El archivo :blue[{nameFileXlsx}] no cuenta con datos: :blue[{pesLabel}]**", icon="⚠️")

        else:
            st.error(f"**Nombre de archivo no valido :blue[{nameFileXlsx}]**", icon="🚨")
