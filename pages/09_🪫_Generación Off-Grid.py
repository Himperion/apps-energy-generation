# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import yaml
from datetime import datetime, date

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

st.sidebar.link_button(":violet-badge[**Ir a la app de herramientas**]", "https://app-nasa-power.streamlit.app/", icon="🔧")

st.markdown("# 🪫 Generación Off-Grid")

tab1, tab2, tab3, tab4 = st.tabs(["📑 Marco teórico", "💾 Entrada de datos", "📝 Análisis de resultados", "👨‍🏫 Visualización de resultados"])

with tab1:
    st.session_state['dictDataOffGrid'] = None

    with st.expander(":violet-badge[**Marco teórico**]", icon="✏️"):
        st.markdown("Los sistemas de generación eólica Off-Grid son especialmente relevantes en áreas remotas donde no hay acceso a la red eléctrica. Los sistemas híbridos con baterías y grupos electrógenos (GE), añaden una capa extra de seguridad y continuidad en el suministro eléctrico. Cuando la generación combinada de las celdas solares y los aerogeneradores, junto con las baterías, no es suficiente para satisfacer la demanda energética, el grupo electrógeno actúa como respaldo. Este se enciende automáticamente para suplir la carga del usuario, mientras que el sistema de generación fotovoltaica y eólica continúa operando para recargar las baterías hasta alcanzar los niveles necesarios para reconectarse.")

        col1, col2, col3 = st.columns( [0.2, 0.6, 0.2])
        
        with col2:
            st.image("images//app9_img1.png")

    with st.expander(":orange-badge[**Recomendaciones**]", icon="⚠️"):
        st.markdown("Antes de subir los archivos de los componentes, es necesario que consulte las fichas técnicas de cada uno. La potencia nominal del aerogenerador no debe superar los límites de potencia admitidos por el inversor y el regulador eólico. De igual forma, la potencia del arreglo de paneles fotovoltaicos debe mantenerse dentro de los límites establecidos para el inversor y el regulador fotovoltaico. Además, debe verificar que las tensiones de los reguladores de carga, tanto fotovoltaico como eólico, coincidan con la definida para su banco de baterías y, a su vez, con la tensión de entrada de los inversores. Los inversores deben tener tensiones y fases compatibles con la definida para el usuario. Por último, la potencia del grupo electrógeno debe seleccionarse en función de los puntos de mayor consumo, según la curva de demanda, considerando un margen de seguridad para evitar su sobredimensionamiento.")

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
                    uploadedXlsxPROJECT = st.file_uploader(label="**Cargar archivo :blue[Project_OffGrid] XLSX**", type=["xlsx"], key="uploadedXlsxPROJECT")

            elif projectDataEntry == selectDataEntryOptions[2]:
                uploadedXlsxDATA, uploadedYamlCOMPONENTS = None, None

                with st.container(border=True):
                    uploadedXlsxDATA = st.file_uploader(label="📋 **Cargar archivo de datos de carga, temperatura de operación y potencial energético del sitio EXCEL**", type=["xlsx"], key="uploadedXlsxDATA")

                with st.container(border=True):
                    uploadedYamlCOMPONENTS = st.file_uploader(label="💾 **Cargar archivo de componentes Off-Grid: :blue[Components_OffGrid] YAML**", type=["yaml", "yml"])
        
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
                    df_data, dictDataOffGrid = None, {}

                    if uploadedXlsxDATA is not None:
                        df_data = pd.read_excel(uploadedXlsxDATA)
                    else:
                        st.warning("Cargar archivo **XLSX** (.xlsx)", icon="⚠️")

                    if uploadedYamlCOMPONENTS is not None:
                        dictDataOffGrid = yaml.safe_load(uploadedYamlCOMPONENTS)
                    else:
                        st.warning("Cargar archivo  de componentes OffGrid **YAML** (.yaml)", icon="⚠️")

                    if len(dictDataOffGrid) > 0:
                        st.session_state["dictDataOffGrid"] = {**{"df_data": df_data}, **dictDataOffGrid}

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
                file_name=general.nameFileHead(name="Project_OffGrid.xlsx"),
                mime="xlsx",
                on_click="ignore")
            
            dict_downloadYAML = st.download_button(
                label="💾 Descargar **:blue[Archivo de componentes del proyecto Off-Grid] YAML**",
                data=bytesFileYamlComponets,
                file_name=general.nameFileHead(name="Components_OffGrid.yaml"),
                mime="text/yaml",
                on_click="ignore")
            
        with st.container(border=True):
            st.markdown("**Archivos de resultados:**")

            df_download = st.download_button(
                label="📄 Descargar **:blue[Archivo de resultado Off-Grid] XLSX**",
                data=bytesFileExcelResults,
                file_name=general.nameFileHead(name="Results_OffGrid.xlsx"),
                mime='xlsx',
                on_click="ignore")

        st.session_state["dictDataOffGrid"] = None

with tab3:
    st.session_state["dictDataOffGrid"] = None
    flagSubmittedAnalysis, uploaderXlsx = False, None

    with st.container(border=True):
        uploaderXlsx = st.file_uploader(label="**Cargar archivo :blue[Results_OffGrid] EXCEL**", type=["xlsx"], key='uploaderXlsx')  
        submitted = st.button("Aceptar")

        if submitted:
            if uploaderXlsx is not None:
                flagSubmittedAnalysis = True
            else:
                st.warning("**Cargar archivo :blue[Results_OnGrid]**", icon="⚠️")

    if flagSubmittedAnalysis:
        nameFileXlsx = uploaderXlsx.name
        if nameFileXlsx.split(" ")[1].split(".")[0] == "Results_OffGrid":
            try:
                df_data = pd.read_excel(uploaderXlsx, sheet_name="Result")
                dict_params = pd.read_excel(uploaderXlsx, sheet_name="Params").to_dict(orient="records")[0]
                timeInfo = general.getTimeData(df_data)

                df_dailyResult, df_monthlyResult, df_annualResult = None, None, None       

                df_dailyResult = general.getAnalysisInTime(df_data, timeInfo["deltaMinutes"], "day", "OffGrid")
                df_monthlyResult = general.getAnalysisInTime(df_data, timeInfo["deltaMinutes"], "month", "OffGrid")
                df_annualResult = general.getAnalysisInTime(df_data, timeInfo["deltaMinutes"], "year", "OffGrid")
                bytesFile = general.toExcelAnalysis(df_data, dict_params, df_dailyResult, df_monthlyResult, df_annualResult)

                df_download = st.download_button(
                    label="💾 Descargar **:blue[Análisis Off-Grid] XLSX**",
                    data=bytesFile,
                    file_name=general.nameFileHead(name="Analysis_OffGrid.xlsx"),
                    mime='xlsx',
                    on_click="ignore"
                    )
                
            except:
                st.error("Error al cargar archivo **EXCEL** (.xlsx)", icon="🚨")
        else:
            st.error(f"**Nombre de archivo no valido :blue[{nameFileXlsx}]**", icon="🚨")

with tab4:
    st.session_state["dictDataOffGrid"] = None
    uploaderAnalysisXlsx = None

    with st.container(border=True):
        uploaderAnalysisXlsx = st.file_uploader(label="**Cargar archivo :blue[Analysis_OffGrid] EXCEL**", type=["xlsx"], key="uploaderAnalysisXlsx")

    if uploaderAnalysisXlsx is not None:
        nameFileXlsx = uploaderAnalysisXlsx.name
        if nameFileXlsx.split(" ")[1].split(".")[0] == "Analysis_OffGrid":
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
                        col1, col2, col3 = st.columns(3, vertical_alignment="bottom")

                        with col1:
                            pf_date = st.date_input(label="Seleccionar fecha", min_value=timeInfo["dateIni"], max_value=timeInfo["dateEnd"], value=timeInfo["dateIni"])     # datetime.date
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
                                    pf_date = st.date_input(label="Seleccionar fecha", min_value=dateIni, max_value=dateEnd, value=dateIni)
                                with col2:
                                    submittedDaily = st.form_submit_button("Aceptar")

                            if submittedDaily:
                                fun_app9.displayDailyResults(df_data, df_dailyAnalysis, PARAMS_data, pf_date, label_systems)

                with tab3:
                    if df_dailyAnalysis is not None and df_monthlyAnalysis is not None:
                        listLabelsMonths = general.timeInfoMonthsGetLabels(timeInfoMonths=timeInfo["months"])
                        flagSubmittedMonth = False
                        optionYearRange, optionMonthRange = None, None

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
                                            submittedMonthly = st.form_submit_button("Aceptar")

                                        if submittedMonthly:
                                            flagSubmittedMonth = True

                        if flagSubmittedMonth and optionYearRange is not None and optionMonthRange is not None:
                            year = optionYearRange
                            month = general.fromMonthGetIndex(month=optionMonthRange)
                            pf_date = date(year, month, 1)
                            fun_app9.displayMonthlyResults(df_data, df_dailyAnalysis, df_monthlyAnalysis, PARAMS_data, pf_date, label_systems)
                    else:
                        if df_dailyAnalysis is None:
                            pesLabel = "DailyAnalysis"
                            st.warning(f"**El archivo :blue[{nameFileXlsx}] no cuenta con datos: :blue[{pesLabel}]**", icon="⚠️")
                        if df_monthlyAnalysis is None:
                            pesLabel = "MonthlyAnalysis"
                            st.warning(f"**El archivo :blue[{nameFileXlsx}] no cuenta con datos: :blue[{pesLabel}]**", icon="⚠️")

                with tab4:
                    if df_monthlyAnalysis is not None and df_annualAnalysis is not None:
                        flagSubmittedYear, year = False, None

                        with st.form("analysisYear", border=True):
                            col1, col2 = st.columns([0.6, 0.4], vertical_alignment="bottom")

                            with col1:
                                year = st.selectbox(label="Seleccionar año:", options=timeInfo["years"], index=0, key="optionYearRange")
                            with col2:
                                submitted = st.form_submit_button("Aceptar")

                            if submitted:
                                flagSubmittedYear = True

                        if flagSubmittedYear and year is not None:
                            pf_date = date(year, 1, 1)
                            fun_app9.displayAnnualResults(df_monthlyAnalysis, df_annualAnalysis, PARAMS_data, pf_date, label_systems)

                    else:
                        if df_monthlyAnalysis is None:
                            pesLabel = "MonthlyAnalysis"
                            st.warning(f"**El archivo :blue[{nameFileXlsx}] no cuenta con datos: :blue[{pesLabel}]**", icon="⚠️")
                        if df_annualAnalysis is None:
                            pesLabel = "AnnualAnalysis"
                            st.warning(f"**El archivo :blue[{nameFileXlsx}] no cuenta con datos: :blue[{pesLabel}]**", icon="⚠️")         


        else:
            st.error(f"**Nombre de archivo no valido :blue[{nameFileXlsx}]**", icon="🚨")
                            
                            


                        


        

        
        

        

                  

                    

                    


            


        