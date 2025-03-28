# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import yaml

from funtions import general, fun_app9

#%%  global variables

with open("files//[COMP] - dict_components.yaml", 'r') as archivo:
    dict_components = yaml.safe_load(archivo)

with open("files//[AERO] - params.yaml", 'r') as archivo:
    params_AERO = yaml.safe_load(archivo)

with open("files//[BAT] - params.yaml", 'r') as archivo:
    params_BAT = yaml.safe_load(archivo)

with open("files//[RC] - params.yaml", 'r') as archivo:
    params_RC = yaml.safe_load(archivo)

params_PV, rename_PV, showOutputPV = fun_app9.getGlobalVariablesPV()

dataKeyList = ["PV_data", "INVPV_data", "RCPV_data",
               "AERO_data", "INVAERO_data", "RCAERO_data",
               "BAT_data", "GE_data", "rho", "PVs", "PVp", "Ns_BAT", "Np_BAT",
               "columnsOptionsData", "numberPhases", "validateEntries", "componentInTheProject",
               "generationType"]

listGenerationOptions = ["Generación solar", "Generación eólica", "Respaldo grupo electrógeno"]

listGenerationOptions = general.getListGenerationOptions(generationType="OffGrid")

selectDataEntryOptions = ["📝 Ingresar datos del proyecto",
                          "💾 Cargar archivo de proyecto XLSX",
                          "💾 Cargar archivo de componentes YAML"]

#%% session state

if 'dictDataOffGrid' not in st.session_state:
    st.session_state['dictDataOffGrid'] = None

#%% main

st.markdown("# 🪫 Generación Off-Grid")

tab1, tab2, tab3 = st.tabs(["📑 Marco teórico", "💾 Entrada de datos", "📝 Análisis de resultados"])

with tab1:
    st.session_state['dictDataOffGrid'] = None

    with st.expander("**Marco teórico**"):
        col1, col2, col3 = st.columns( [0.05, 0.9, 0.05])

        with col1:
            st.write("")
        with col2:
            st.image("images//app9_img1.png")
        with col3:
            st.write("")

    with st.expander("**Ingreso de datos**"):
        st.markdown("Ingreso de datos")

with tab2:
    generationOptions = None

    with st.container(border=True):
        projectDataEntry = st.selectbox(label="Opciones de ingreso de datos", options=selectDataEntryOptions,
                                        index=None, placeholder="Selecciona una opción")
        
        if projectDataEntry == selectDataEntryOptions[0]:
            uploadedYamlPV, uploadedYamlINV_PV, uploadedYamlRC_PV = None, None, None
            uploadedYamlAERO, uploadedYamlINV_AERO, uploadedYamlRC_AERO = None, None, None
            uploadedXlsxDATA, uploadedYamlGE, uploadedYamlBAT = None, None, None
            PVs, PVp, Ns_BAT, Np_BAT, rho = None, None, None, None, None
            
            generationOptions = st.multiselect(label="Opciones de generación eléctrica", options=listGenerationOptions, default=listGenerationOptions[0])

            with st.container(border=True):
                st.markdown("📋 **:blue[Datos de carga, temperatura de operación y potencial energetico del sitio:]**")
                uploadedXlsxDATA = st.file_uploader(label="**Cargar archivo EXCEL**", type=["xlsx"], key="uploadedXlsxDATA")

                if listGenerationOptions[1] in generationOptions:
                    rho = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_AERO["rho"]),
                                                       variable=params_AERO["rho"]["number_input"], key="rho", disabled=False)
                else:
                    rho = None

        with st.form("Off-Grid", border=False):

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
                                PVs = fun_app9.get_widget_number_input(label=general.getLabelParams(dict_param=params_PV["PVs"]),
                                                                       disabled=False, key="PVs", variable=params_PV["PVs"]["number_input"])
                            with col2:
                                PVp = fun_app9.get_widget_number_input(label=general.getLabelParams(dict_param=params_PV["PVp"]),
                                                                       disabled=False, key="PVp", variable=params_PV["PVp"]["number_input"])
                    
                        with st.container(border=True):
                            st.markdown(f"{dict_components['INVPV']['emoji']} **:blue[{dict_components['INVPV']['name']}:]**")
                            uploadedYamlINV_PV = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlINV_PV')

                        with st.container(border=True):
                            st.markdown("🪫 **:blue[Regulador de carga:]**")
                            uploadedYamlRC_PV = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlRC_PV')
                        
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
                            st.markdown("🪫 **:green[Regulador de carga:]**")
                            uploadedYamlRC_AERO = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlRC_AERO')

                if (listGenerationOptions[0] in generationOptions) or (listGenerationOptions[1] in generationOptions):
                    with st.container(border=True):
                        st.markdown("🔋 **:blue[Banco de baterías:]**")
                        uploadedYamlBAT = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key="uploadedYamlBAT")

                        st.markdown("🧑‍🔧 Conexión del banco de baterías")
                        col1, col2 = st.columns(2)
                        with col1:
                            Ns_BAT = fun_app9.get_widget_number_input(label=general.getLabelParams(dict_param=params_BAT["Ns"]),
                                                                      disabled=False, key="Ns_BAT", variable=params_BAT["Ns"]["number_input"])
                        with col2:
                            Np_BAT = fun_app9.get_widget_number_input(label=general.getLabelParams(dict_param=params_BAT["Np"]),
                                                                      disabled=False, key="Np_BAT", variable=params_BAT["Np"]["number_input"])

                if listGenerationOptions[2] in generationOptions:
                    with st.container(border=True):
                        st.markdown("⛽ **:red[Respaldo grupo electrógeno]**")
                        uploadedYamlGE = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlGE')

            elif projectDataEntry == selectDataEntryOptions[1]:
                with st.container(border=True):
                    st.markdown("💾 **:blue[Cargar archivo de proyecto Off-Grid]**")
                    uploadedXlsxPROJECT = st.file_uploader(label="**Cargar archivo XLSX**", type=["xlsx"], key="uploadedXlsxPROJECT")

            elif projectDataEntry == selectDataEntryOptions[2]:
                with st.container(border=True):
                    st.markdown("📋 **:blue[Datos de carga, temperatura de operación y potencial energetico del sitio:]**")
                    uploadedXlsxDATA = st.file_uploader(label="**Cargar archivo EXCEL**", type=["xlsx"], key="uploadedXlsxDATA")

                with st.container(border=True):
                    st.markdown("💾 **:blue[Cargar archivo de componentes Off-Grid]**")
                    uploadedYamlCOMPONENTS = st.file_uploader(label="Subir archivo de componentes YAML", type=["yaml", "yml"])
        
            submitted = st.form_submit_button("Aceptar")

            if submitted:
                
                if projectDataEntry == selectDataEntryOptions[0]:
                    checkProject, validateEntries = False, general.initializeDictValidateEntries(generationType="OffGrid")
                    componentInTheProject = general.getDictComponentInTheProject(generationOptions)
                    checkUploaded = general.getErrorForMissingComponent(uploadedYamlPV, uploadedYamlINV_PV, uploadedYamlRC_PV,
                                                                        uploadedYamlAERO, uploadedYamlINV_AERO, uploadedYamlRC_AERO,
                                                                        uploadedXlsxDATA, uploadedYamlGE, uploadedYamlBAT,
                                                                        "OffGrid", componentInTheProject)
                    
                    if checkUploaded:
                        validateEntries['check_DATA'], df_data, columnsOptionsData = general.getDataValidation(uploadedXlsxDATA, componentInTheProject)
                    
                        if len(generationOptions) != 0:
                            PV_data, INVPV_data, RCPV_data,  = None, None, None
                            AERO_data, INVAERO_data, RCAERO_data = None, None, None
                            BAT_data, GE_data = None, None

                            validateEntries, BAT_data = general.getDataGEorBATValidation(uploadedYamlBAT, validateEntries, "BAT")
                            
                            if componentInTheProject["generationPV"]:       # Generación PV
                                validateEntries, PV_data, INVPV_data, RCPV_data = general.getDataOffGridValidation(uploadedYamlPV, uploadedYamlINV_PV, uploadedYamlRC_PV, validateEntries, "PV")

                            if componentInTheProject["generationAERO"]:     # Generación AERO
                                validateEntries, AERO_data, INVAERO_data, RCAERO_data = general.getDataOffGridValidation(uploadedYamlAERO, uploadedYamlINV_AERO, uploadedYamlRC_AERO, validateEntries, "AERO")

                            if componentInTheProject["generationGE"]:       # Generación GE
                                validateEntries, GE_data = general.getDataGEorBATValidation(uploadedYamlGE, validateEntries, "GE")

                            validateComponents = general.getDictValidateComponent(validateEntries=validateEntries, generationType="OffGrid")
                            checkProject = general.getCheckValidateGeneration(**componentInTheProject, **validateComponents, generationType="OffGrid")

                            if checkProject:
                                numberPhases = general.getNumberPhases(INVPV_data, INVAERO_data, GE_data)
                                compatibilityBAT = fun_app9.getCompatibilityBAT(RCPV_data, RCAERO_data, BAT_data, Ns_BAT, componentInTheProject["generationPV"], componentInTheProject["generationAERO"])

                                if numberPhases is not None:
                                    if compatibilityBAT:
                                        st.session_state["dictDataOffGrid"] = {
                                            "df_data": df_data,
                                            "PV_data": PV_data,
                                            "INVPV_data": INVPV_data,
                                            "RCPV_data": RCPV_data,
                                            "AERO_data": AERO_data,
                                            "INVAERO_data": INVAERO_data,
                                            "RCAERO_data": RCAERO_data,
                                            "BAT_data": BAT_data,
                                            "GE_data": GE_data,
                                            "rho": rho,
                                            "PVs": PVs,
                                            "PVp": PVp,
                                            "Ns_BAT": Ns_BAT,
                                            "Np_BAT": Np_BAT,
                                            "columnsOptionsData": columnsOptionsData,
                                            "numberPhases": numberPhases,
                                            "validateEntries": validateEntries,
                                            "componentInTheProject": componentInTheProject,
                                            "generationType": "OffGrid"
                                            }
                                        
                                    else:
                                        st.error("**Incompatibilidad entre el banco de baterías y el regulador de carga**", icon="🚨")
                                else:
                                    st.error("**No coincide el número de fases de los distintos componentes**", icon="🚨")
                        else:
                            st.error("Ingresar **Opciones de generación eléctrica**", icon="🚨")     
                                
                elif projectDataEntry == selectDataEntryOptions[1]:

                    df_data = pd.read_excel(uploadedXlsxPROJECT, sheet_name="Data")
                    TOTAL_data = pd.read_excel(uploadedXlsxPROJECT, sheet_name="Params").to_dict(orient="records")[0]
                    TOTAL_data = general.getFixFormatDictParams(TOTAL_data, dataKeyList)
                    TOTAL_data["df_data"] = df_data

                    st.session_state["dictDataOffGrid"] = {**{"df_data": df_data}, **TOTAL_data}

                elif projectDataEntry == selectDataEntryOptions[2]:
                    df_data, dictDataOffGrid = None, None

                    if uploadedXlsxDATA is not None:
                        df_data = pd.read_excel(uploadedXlsxDATA)
                    else:
                        st.warning("Cargar archivo **XLSX** (.xlsx)", icon="⚠️")

                    if uploadedYamlCOMPONENTS is not None:
                        dictDataOffGrid = yaml.safe_load(uploadedYamlCOMPONENTS)
                    else:
                        st.warning("Cargar archivo  de componentes OffGrid **YAML** (.yaml)", icon="⚠️")

    if st.session_state["dictDataOffGrid"] is not None:

        df_offGrid = fun_app9.generationOffGrid(**st.session_state["dictDataOffGrid"])
        TOTAL_data, bytesFileExcelProject = fun_app9.getBytesFileExcelProjectOffGrid(dictDataOffGrid=st.session_state["dictDataOffGrid"], dataKeyList=dataKeyList)
        bytesFileYamlComponets = general.getBytesFileYamlComponentsProject(dictDataProject=st.session_state["dictDataOffGrid"])
        bytesFileExcelResults = general.toExcelResults(df=df_offGrid, dictionary=TOTAL_data, df_sheetName="Result", dict_sheetName="Params")

        with st.container(border=True):
            st.markdown("**Archivos de opciones de ingreso de datos:**")

            df_downloadXLSX = st.download_button(
                label="💾 Descargar **:blue[Archivo de proyecto Off-Grid] XLSX**",
                data=bytesFileExcelProject,
                file_name=general.nameFileHead(name="project_OffGrid.xlsx"),
                mime="xlsx")
            
            dict_downloadYAML = st.download_button(
                label="💾 Descargar **:blue[Archivo de componentes del proyecto Off-Grid] YAML**",
                data=bytesFileYamlComponets,
                file_name=general.nameFileHead(name="components_OffGrid.yaml"),
                mime="text/yaml")
            
        with st.container(border=True):
            st.markdown("**Archivos de resultados:**")

            df_download = st.download_button(
                label="📄 Descargar **:blue[Archivo de resultado Off-Grid] XLSX**",
                data=bytesFileExcelResults,
                file_name=general.nameFileHead(name="results_OffGrid.xlsx"),
                mime='xlsx')

        st.session_state["dictDataOffGrid"] = None

with tab3:
    st.session_state["dictDataOffGrid"] = None

    with st.container(border=True):
        st.markdown("**💾 :blue[Cargar archivo de análisis de resultados :]**")

        uploaderXlsx = st.file_uploader(label="**Cargar archivo EXCEL**", type=["xlsx"], key="uploaderXlsx")
        submitted = st.button("Aceptar")

        if submitted:
            if uploaderXlsx is not None:
                try:
                    df_resultOffGrid = pd.read_excel(uploaderXlsx, sheet_name="Result")
                    timeInfo = general.getTimeData(df_resultOffGrid)
                    
                    df_dailyResult, df_monthlyResult, df_annualResult = None, None, None       

                    df_dailyResult = general.getAnalysisInTime(df_resultOffGrid, timeInfo["deltaMinutes"], "day", "OffGrid")
                    df_monthlyResult = general.getAnalysisInTime(df_resultOffGrid, timeInfo["deltaMinutes"], "month", "OffGrid")
                    df_annualResult = general.getAnalysisInTime(df_resultOffGrid, timeInfo["deltaMinutes"], "year", "OffGrid")
                    bytesFile = general.toExcelAnalysis(df_resultOffGrid, df_dailyResult, df_monthlyResult, df_annualResult)

                    df_download = st.download_button(
                        label="💾 Descargar **:blue[Análisis] XLSX**",
                        data=bytesFile,
                        file_name=general.nameFileHead(name="Analysis_OffGrid.xlsx"),
                        mime='xlsx')
                except:
                    st.error("Error al cargar archivo **EXCEL** (.xlsx)", icon="🚨")

        

        
        

        

                  

                    

                    


            


        