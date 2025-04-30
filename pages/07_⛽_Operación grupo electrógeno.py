# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import yaml
from io import BytesIO
from datetime import datetime, date

from funtions import general, fun_app7

#%% funtions

@st.cache_data
def to_excel(df: pd.DataFrame):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    
    processed_data = output.getvalue()
        
    return processed_data

#%% global variables

with open("files//[GE] - params.yaml", 'r') as archivo:
    dict_params = yaml.safe_load(archivo)

with open("files//[GE] - PE.yaml", 'r') as archivo:
    dict_fuel = yaml.safe_load(archivo)

dict_phases = {
    "Monofásico": {"Num": 1, "label": "1️⃣ Monofásico"},
    "Trifásico": {"Num": 3, "label": "3️⃣ Trifásico"}
}

selectDataEntryOptions = ["🛠️ Datos del grupo electrógeno",
                          "💾 Cargar archivo de datos del grupo electrógeno YAML"]

optionsSelInput = ["📗 Obtener curvas característica del grupo electrógeno",
                   "📚 Ingresar datos de potencia demandada por la carga"]

template = {
    "directory": "files",
    "name_file": "[Plantilla] - Potencia de carga",
    "format_file": "xlsx",
    "description": "Potencia demandada por la carga"
}

items_options_columns_df = {
    "Load" : ["Load(kW)"]
}

dataKeyList = ["Pnom", "Voc", "Vpc", "phases", "FP", "Combustible", "PE_fuel", "C100", "C0"]

#%% main

st.sidebar.link_button(":violet-badge[**Ir a la app de herramientas**]", "https://app-nasa-power.streamlit.app/", icon="🔧")

st.markdown("# ⛽ Operación grupo electrógeno")

tab1, tab2, tab3 = st.tabs(["📑 Información", "💾 Entrada de datos", "👨‍🏫 Visualización de resultados"]) 

with tab1:
    with st.expander(":violet-badge[**Marco teórico**]", icon="✏️"):
        st.subheader("Introducción", divider="violet")
        st.markdown("Un grupo electrógeno convierte la energía química en cinética y luego en eléctrica, todo esto a partir de un motor de combustión y un generador eléctrico. Se pueden clasificar por:")
        st.markdown("Tipos de combustible:")
        st.markdown(" - **Diésel:** Alta eficiencia y durabilidad para uso intensivo.")
        st.markdown(" - **Gasolina:** Portátiles y económicos, ideales para usos temporales o de menor escala.")
        st.markdown(" - **Gas:** Menos emisiones y operación más silenciosa; requieren acceso continuo a gas natural o propano.")
        st.markdown(" - **Biogás:** Sostenibles y ecológicos; utilizando desechos orgánicos para la generación de energía.")
        st.markdown("*Esquema del grupo electrógeno*")

        col1, col2, col3 = st.columns( [0.25, 0.5, 0.25])

        with col2:
            st.image("images//app7_img1.png")

        st.markdown("$load$: Potencia de la carga *(kW)*")
        st.markdown("*Ia_gen*: Corriente de armadura del grupo electrógeno *(A)*")
        st.markdown("*Vt_gen*: Tensión de salida del grupo electrógeno *(V)*")
        st.markdown("*C*: Consumo *(L/h)*")

        st.subheader("Ingreso de datos", divider="blue")
        st.markdown("Para esta sección, los datos pueden ingresarse de las siguientes maneras:")
        with st.container(border=True):
            st.markdown(f"**:blue[{selectDataEntryOptions[0]}:]**")
            st.markdown("Sí cuenta con los datos de la ficha técnica del grupo electrógeno puede ingresar manualmente desde este apartado.")
            st.markdown(f"**:blue[{selectDataEntryOptions[1]}:]**")
            st.markdown("Este archivo **YAML** para el ingreso rápido de información es descargado en la sección de **🧩 Componentes**.")


        st.subheader("Opciones de la sección", divider="green")
        st.markdown("Esta sección es posible seleccionar las opciones del ingreso de condiciones del componente")
        with st.container(border=True):
            st.markdown(f"**:green[{optionsSelInput[0]}:]**")
            st.markdown("Generación automática de vector de carga **Load(kW)** para la caracterización del componente.")
            st.markdown(f"**:green[{optionsSelInput[1]}:]**")
            st.markdown("Permite el ingreso mediante un archivo **XLSX** de múltiples valores de carga **Load(kW)** para obtener la operación del componente en el tiempo.")


    with st.expander(":blue-badge[**Infografía**]", icon="📝"):
        infographic_path = "files/infographic/07_GE.pdf"
        infographic_label = "Operación grupo electrógeno"
    
        general.infographicViewer(infographic_path, infographic_label)
           
with tab2:
    data_entry_options = st.selectbox(label="Opciones de ingreso de datos", options=selectDataEntryOptions,
                                      index=0, placeholder="Selecciona una opción")
    
    if data_entry_options == selectDataEntryOptions[0]:
        with st.container(border=True):
            st.markdown("🔌 **:blue[{0}:]**".format("Datos eléctricos"))
            
            Pnom = general.widgetNumberImput(dictParam=dict_params["Pnom"], key="Pnom", disabled=False)
            
            col1, col2 = st.columns(2)
            with col1:
                Voc = general.widgetNumberImput(dictParam=dict_params["Voc"], key="Voc", disabled=False)
                phases = st.selectbox(label="**Fases:** sistema de corriente alterna",
                                      options=[value["label"] for value in dict_phases.values()],
                                      index=0, placeholder="Selecciona una opción")
            with col2:
                Vpc = general.widgetNumberImput(dictParam=dict_params["Vpc"], key="Vpc", disabled=False)
                FP = general.widgetNumberImput(dictParam=dict_params["FP"], key="FP", disabled=False)
        
        with st.container(border=True):
            st.markdown("🛢️ **:blue[{0}:]**".format("Datos de combustible"))

            Combustible = st.selectbox(label="**Tipo de combustible:**",
                                       options=[key for key in dict_fuel],
                                       index=0, placeholder="Selecciona una opción")

            col1, col2 = st.columns(2)
            with col1:
                C100 = general.widgetNumberImput(dictParam=dict_params["C'100"], key="C100", disabled=False)
            with col2:
                C0 = general.widgetNumberImput(dictParam=dict_params["C'0"], key="C0", disabled=False)
                
    elif data_entry_options == selectDataEntryOptions[1]:
        with st.container(border=True):
            uploaded_file_yaml = st.file_uploader(label="Sube tu archivo YAML", type=["yaml", "yml"])

    with st.container(border=True):
        st.markdown("🌞 **:blue[{0}:]**".format("Condiciones de operación del componente"))

        option_sel = st.radio(label="Opciones para el ingreso de condiciones",
                              options=optionsSelInput,
                              captions=["Generación automática de vector de carga para la caracterización del componente",
                                        "Ingreso de múltiples condiciones de carga para obtener la operación del componente "])
        
        if option_sel == optionsSelInput[1]:
            label_Load = "Cargar archivo de carga del grupo electrógeno"
            archive_Load = st.file_uploader(label=label_Load, type={"xlsx"})

            fun_app7.get_download_button(**template)
        
    app_submitted = st.button("Aceptar")

    if app_submitted:
        GE_data, df_data, check, bytesFile = None, None, False, None
        if data_entry_options == selectDataEntryOptions[0]:

            GE_data = {
                "Pnom": Pnom,
                "Voc": Voc,
                "Vpc": Vpc,
                "phases": general.fromValueLabelGetKey(dict_in=dict_phases, key_label="label", value_label=phases),
                "FP": FP,
                "Combustible": Combustible,
                "PE_fuel": dict_fuel[Combustible]["PE"],
                "C100": C100,
                "C0": C0
            }

        elif data_entry_options == selectDataEntryOptions[1]:
            if uploaded_file_yaml is not None:
                GE_data = yaml.safe_load(uploaded_file_yaml)
            else:
                st.warning("Cargar archivo **YAML** (.yaml)", icon="⚠️")

        if GE_data is not None:
            In, Ra, dictPU = fun_app7.get_param_gp(GE_data, dict_phases)

            if option_sel == optionsSelInput[0]:
                df_data = fun_app7.get_df_option_characteristic_curve(dict_pu=dictPU, dict_param=GE_data)
                check = True

            elif option_sel == optionsSelInput[1] and archive_Load is not None:
                try:
                    df_input = pd.read_excel(archive_Load)
                    df_data, check, columnsOptionsSel = general.checkDataframeInput(dataframe=df_input, options=items_options_columns_df)

                    if check:
                        timeInfo = general.getTimeData(df_data)
                        df_data = fun_app7.getDataframeGE(df_data, dictPU, GE_data, columnsOptionsSel)

                        df_dailyResult, df_monthlyResult, df_annualResult = None, None, None

                        df_dailyResult = fun_app7.getAnalysisInTime(df_data, GE_data, timeInfo["deltaMinutes"], "day")
                        df_monthlyResult = fun_app7.getAnalysisInTime(df_data, GE_data, timeInfo["deltaMinutes"], "month")
                        df_annualResult = fun_app7.getAnalysisInTime(df_data, GE_data, timeInfo["deltaMinutes"], "year")
                        bytesFile = general.toExcelAnalysis(df_data, GE_data, df_dailyResult, df_monthlyResult, df_annualResult)

                    else:
                        st.error("Error al cargar archivo **Excel** (.xlsx)", icon="🚨")
                except:
                    st.error("Error al cargar archivo **Excel** (.xlsx)", icon="🚨")
               
        if df_data is not None and check:
            if option_sel == optionsSelInput[1]:
                if bytesFile is not None:
                    st.download_button(
                        label="💾 Descargar **:blue[Análisis GE] XLSX**",
                        data=bytesFile,
                        file_name=general.nameFileHead(name="Analysis_GE.xlsx"),
                        mime="xlsx",
                        on_click="ignore"
                        )

            elif option_sel == optionsSelInput[0]:
                df_GE = fun_app7.getDataframeGE(dataframe=df_data,
                                                dict_pu=dictPU,
                                                dict_param=GE_data,
                                                columnsOptionsSel={"Load": "Load(kW)"})

                sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📋 Resultados",
                                                        "📊 Gráficas",
                                                        "💾 Descargas"])
                
                with sub_tab1:
                    with st.container(border=True):
                        st.dataframe(df_GE)
                        
                with sub_tab2:
                    with st.container(border=True):
                        if option_sel == optionsSelInput[0]:
                            fun_app7.visualizeCurvesGE(df_GE)
                            
                with sub_tab3:
                    buffer_data = general.getBytesYaml(dictionary=GE_data)
                    excel = to_excel(df_GE)

                    with st.container(border=True):
                        with st.container(border=True):
                            st.markdown("**Archivos de opciones de ingreso de datos:**")
                            
                            buttonYaml2 = general.yamlDownloadButton(bytesFileYaml=buffer_data,
                                                                     file_name="GE_data",
                                                                     label="💾 Descargar **:blue[archivo de datos]** del grupo electrógeno **YAML**")
                            
                        with st.container(border=True):
                            st.markdown("**Archivos de resultados:**")
                            st.download_button(
                                label="📄 Descargar **:blue[Resultados]** del grupo electrógeno **XLSX**",
                                data=excel,
                                file_name=general.nameFileHead(name="GE_characteristicCurve.xlsx"),
                                mime="xlsx")

with tab3:
    uploaderAnalysisXlsx = None

    with st.container(border=True):
        uploaderAnalysisXlsx = st.file_uploader(label="**Cargar archivo :blue[Analysis_GE] EXCEL**", type=["xlsx"], key="uploaderAnalysisXlsx")

    if uploaderAnalysisXlsx is not None:
        nameFileXlsx = uploaderAnalysisXlsx.name
        if nameFileXlsx.split(" ")[1].split(".")[0] == "Analysis_GE":
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
                numberPhases = general.fromLabelObtainNumberOf(PARAMS_data["phases"])
                label_systems = "GE"
                PARAMS_data = {**PARAMS_data, **{"generationType": "GE", "columnsOptionsData": None, "numberPhases": numberPhases}}

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
                            df_datatime = general.get_df_datatime(df_data, pf_date, pf_time)
                            df_GE = fun_app7.getCompleteDataframeGE(PARAMS_data, dict_phases)
                            dict_CE, dict_LC = fun_app7.get_dict_CE_LC(df_datatime)

                            with st.container(border=True):
                                general.displayInstantResults(df_data, PARAMS_data, pf_date, pf_time, label_systems)

                            with st.expander(f"**:blue[Curvas característica del grupo electrógeno]**", icon="📈"):
                                fun_app7.visualizeCurvesGE(df_GE, dict_CE, dict_LC)

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
                                fun_app7.displayDailyResults(df_data, df_dailyAnalysis, PARAMS_data, pf_date, label_systems, dict_phases)

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
                            fun_app7.displayMonthlyResults(df_data, df_dailyAnalysis, df_monthlyAnalysis, PARAMS_data, pf_date, label_systems)
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
                            fun_app7.displayAnnualResults(df_monthlyAnalysis, df_annualAnalysis, PARAMS_data, pf_date, label_systems)

                    else:
                        if df_monthlyAnalysis is None:
                            pesLabel = "MonthlyAnalysis"
                            st.warning(f"**El archivo :blue[{nameFileXlsx}] no cuenta con datos: :blue[{pesLabel}]**", icon="⚠️")
                        if df_annualAnalysis is None:
                            pesLabel = "AnnualAnalysis"
                            st.warning(f"**El archivo :blue[{nameFileXlsx}] no cuenta con datos: :blue[{pesLabel}]**", icon="⚠️")         

                







    
    

