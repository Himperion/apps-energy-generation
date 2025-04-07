# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import yaml
from io import BytesIO
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
    "name_file": "[Plantilla] - Potecia de carga",
    "format_file": "xlsx",
    "description": "Potencia demandada por la carga"
}

items_options_columns_df = {
    "Load" : ["Load(kW)"]
}

#%% main

st.markdown("# ⛽ Operación grupo electrógeno")

tab1, tab2 = st.tabs(["📑 Marco teórico", "📝 Entrada de datos"]) 

with tab1:
    with st.expander("**Marco teórico**"): 
        st.markdown("Un grupo electrógeno convierte la energía química en cinética y luego en eléctrica, todo esto a partir de un motor de combustión y un generador eléctrico. Se pueden clasificar por:")
        st.markdown("Tipos de combustible:")
        st.markdown(" - **Diésel:** Alta eficiencia y durabilidad para uso intensivo.")
        st.markdown(" - **Gasolina:** Portátiles y económicos, ideales para usos temporales o de menor escala.")
        st.markdown(" - **Gas:** Menos emisiones y operación más silenciosa; requieren acceso continuo a gas natural o propano.")
        st.markdown("*Esquema del grupo electrógeno*")

        col1, col2, col3 = st.columns( [0.25, 0.5, 0.25])

        with col1:
            st.write("")
        with col2:
            st.image("images//app7_img1.png")
        with col3:
            st.write("")

        st.markdown("$load$: Potencia de la carga (kW)")
        st.markdown("*Ia_gen*: Corriente de armadura del grupo electrógeno (A)")
        st.markdown("*Vt_gen*: Tensión de salida del grupo electrógeno (V)")
        st.markdown("*C*: Consumo (l/h)")
        
    with st.expander("**Ingreso de datos**"):
        st.markdown("Para esta sección, los datos pueden ingresarse de las siguientes maneras:")
        with st.container(border=True):
            st.markdown(f"**:blue[{selectDataEntryOptions[0]}:]**")
            st.markdown("Sí cuenta con los datos de la ficha técnica del grupo electrógeno puede ingresar manualmente desde este apartado.")
            st.markdown(f"**:blue[{selectDataEntryOptions[1]}:]**")
            st.markdown("Este archivo **YAML** para el ingreso rápido de información es descargado en la sección de **🧩 Componentes**.")

    with st.expander("**Opciones de la sección**"):
            st.markdown("Esta sección es posible seleccionar las opciones del ingreso de condiciones del componente")
            with st.container(border=True):
                st.markdown(f"**:blue[{optionsSelInput[0]}:]**")
                st.markdown("Generación automática de vector de carga **Load(kW)** para la caracterización del componente.")
                st.markdown(f"**:blue[{optionsSelInput[1]}:]**")
                st.markdown("Permite el ingreso mediante un archivo **XLSX** de múltiples valores de carga **Load(kW)** para obtener la operación del componente en el tiempo.")

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
        GE_data, df_GE = None, None
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
                df_GE = fun_app7.get_df_option_characteristic_curve(dict_pu=dictPU, dict_param=GE_data)

            elif option_sel == optionsSelInput[1] and archive_Load is not None:
                check = False
                try:
                    df_input = pd.read_excel(archive_Load)
                    df_GE, check, columnsOptionsSel = general.checkDataframeInput(dataframe=df_input, options=items_options_columns_df)

                    if check:
                        df_GE = fun_app7.getDataframeGE(df_GE, dictPU, GE_data, columnsOptionsSel)
                        
                    else:
                        st.error("Error al cargar archivo **Excel** (.xlsx)", icon="🚨")

                except:
                    st.error("Error al cargar archivo **Excel** (.xlsx)", icon="🚨")
                

        if df_GE is not None:
            if option_sel == optionsSelInput[1]:

                sub_tab1, sub_tab2 = st.tabs(["📋 Resultados",
                                              "💾 Descargas"])
                
                with sub_tab1:
                    with st.container(border=True):
                        st.dataframe(df_GE)

                with sub_tab2:
                    excel = to_excel(df_GE)
                    buffer_data = general.getBytesYaml(dictionary=GE_data)

                    with st.container(border=True):
                        st.markdown("**Archivos de opciones de ingreso de datos:**")
                        buttonYaml1 = general.yamlDownloadButton(bytesFileYaml=buffer_data,
                                                                file_name="GE_data",
                                                                label="💾 Descargar **:blue[archivo de datos]** del grupo electrógeno **YAML**")
                    
                    with st.container(border=True):
                        st.markdown("**Archivos de resultados:**")
                        st.download_button(
                                label="📄 Descargar **:blue[Resultados]** del grupo electrógeno **XLSX**",
                                data=excel,
                                file_name=general.nameFileHead(name="GE_operationAnalysis.xlsx"),
                                mime="xlsx")


            elif option_sel == optionsSelInput[0]:
                df_GE = fun_app7.getDataframeGE(dataframe=df_GE,
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
                            re_tab1, re_tab2 = st.tabs(["📈 Curva de consumo y eficiencia del GE",
                                                        "📉 Curva de carga del generador"])

                            with re_tab1:
                                fun_app7.getGraphConsumptionEfficiency(dataframe=df_GE)
                            with re_tab2:
                                fun_app7.getGraphLoadCharacteristic(dataframe=df_GE)

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
