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

select_data_entry_options = ["🛠️ Datos del grupo electrógeno",
                             "💾 Cargar archivo de datos del grupo electrógeno YAML"]

options_sel_input = ["📗 Obtener curvas característica del grupo electrógeno",
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
    st.text("Información tab1")
with tab2:
    data_entry_options = st.selectbox(label="Opciones de ingreso de datos", options=select_data_entry_options,
                                      index=0, placeholder="Selecciona una opción")
    
    if data_entry_options == select_data_entry_options[0]:
    
        with st.container(border=True):
            st.markdown("🔌 **:blue[{0}:]**".format("Datos eléctricos"))

            Pnom = fun_app7.get_widget_number_input(label=fun_app7.get_label_params(dict_param=dict_params["Pnom"]),
                                                    variable=dict_params["Pnom"]["number_input"])
            
            col1, col2 = st.columns(2)
            with col1:
                Voc = fun_app7.get_widget_number_input(label=fun_app7.get_label_params(dict_param=dict_params["Voc"]),
                                                       variable=dict_params["Voc"]["number_input"])
                phases = st.selectbox(label="**Fases:** sistema de corriente alterna",
                                      options=[value["label"] for value in dict_phases.values()],
                                      index=0, placeholder="Selecciona una opción")
            with col2:
                Vpc = fun_app7.get_widget_number_input(label=fun_app7.get_label_params(dict_param=dict_params["Vpc"]),
                                                       variable=dict_params["Vpc"]["number_input"])
                FP = fun_app7.get_widget_number_input(label=fun_app7.get_label_params(dict_param=dict_params["FP"]),
                                                      variable=dict_params["FP"]["number_input"])
        
        with st.container(border=True):
            st.markdown("🛢️ **:blue[{0}:]**".format("Datos de combustible"))

            Combustible = st.selectbox(label="**Tipo de combustible:**",
                                       options=[key for key in dict_fuel],
                                       index=0, placeholder="Selecciona una opción")

            col1, col2 = st.columns(2)
            with col1:
                C100 = fun_app7.get_widget_number_input(label=fun_app7.get_label_params(dict_param=dict_params["C'100"]),
                                                        variable=dict_params["C'100"]["number_input"])
            with col2:
                C0 = fun_app7.get_widget_number_input(label=fun_app7.get_label_params(dict_param=dict_params["C'0"]),
                                                      variable=dict_params["C'0"]["number_input"])
                
    elif data_entry_options == select_data_entry_options[1]:
        with st.container(border=True):
            uploaded_file_yaml = st.file_uploader(label="Sube tu archivo YAML", type=["yaml", "yml"])

    with st.container(border=True):
        st.markdown("🌞 **:blue[{0}:]**".format("Condiciones de operación del módulo"))

        option_sel = st.radio(label="Opciones para el ingreso de condiciones",
                              options=options_sel_input,
                              captions=["Generación automática de vector de carga para la caracterización del componente",
                                        "Ingreso de múltiples condiciones de carga para obtener la operación del componente "])
        
        if option_sel == options_sel_input[1]:
            label_Load = "Cargar archivo de carga del grupo electrógeno"
            archive_Load = st.file_uploader(label=label_Load, type={"xlsx"})

            fun_app7.get_download_button(**template)
        
    app_submitted = st.button("Aceptar")

    if app_submitted:
        GE_data, df_GE = None, None
        if data_entry_options == select_data_entry_options[0]:

            GE_data = {
                "Pnom": Pnom,
                "Voc": Voc,
                "Vpc": Vpc,
                "phases": fun_app7.from_value_label_get_key(dict_phases, phases),
                "FP": FP,
                "Combustible": Combustible,
                "PE_fuel": dict_fuel[Combustible]["PE"],
                "C100": C100,
                "C0": C0
            }

        elif data_entry_options == select_data_entry_options[1]:
            if uploaded_file_yaml is not None:
                GE_data = yaml.safe_load(uploaded_file_yaml)
            else:
                st.warning("Cargar archivo **YAML** (.yaml)", icon="⚠️")

        if GE_data is not None:
            In, Ra, dictPU = fun_app7.get_param_gp(GE_data, dict_phases)

            if option_sel == options_sel_input[0]:
                df_GE = fun_app7.get_df_option_characteristic_curve(dict_pu=dictPU, dict_param=GE_data)

            elif option_sel == options_sel_input[1] and archive_Load is not None:
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
            if option_sel == options_sel_input[1]:

                sub_tab1, sub_tab2 = st.tabs(["📋 Resultados",
                                              "💾 Descargas"])
                
                with sub_tab1:
                    with st.container(border=True):
                        st.dataframe(df_GE)

                with sub_tab2:
                    excel = to_excel(df_GE)
                    buffer_data = fun_app7.get_bytes_yaml(dictionary=GE_data)

                    with st.container(border=True):
                        st.markdown("**Archivos de opciones de ingreso de datos:**")
                        st.download_button(
                                label="💾 Descargar **:blue[archivo de datos]** del grupo electrógeno **YAML**",
                                data=buffer_data,
                                file_name=fun_app7.name_file_head(name="GE_data.yaml"),
                                mime="text/yaml"
                                )
                    
                    with st.container(border=True):
                        st.markdown("**Archivos de resultados:**")
                        st.download_button(
                                label="📄 Descargar **:blue[Resultados]** del grupo electrógeno **XLSX**",
                                data=excel,
                                file_name=fun_app7.name_file_head(name="GE_operationAnalysis.xlsx"),
                                mime="xlsx")


            elif option_sel == options_sel_input[0]:
                df_GE = fun_app7.getDataframeGE(dataframe=df_GE,
                                                dict_pu=dictPU,
                                                dict_param=GE_data,
                                                columnsOptionsSel={"Load": "Load(kW)"})

                sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📋 Resultados",
                                                        "📊 Graficas",
                                                        "💾 Descargas"])
                
                with sub_tab1:
                    with st.container(border=True):
                        st.dataframe(df_GE)

                with sub_tab2:
                    with st.container(border=True):
                        if option_sel == options_sel_input[0]:
                            re_tab1, re_tab2 = st.tabs(["📈 Curva de consumo y eficiencia del GE",
                                                        "📉 Curva de carga del generador"])

                            with re_tab1:
                                fun_app7.getGraphConsumptionEfficiency(dataframe=df_GE)
                            with re_tab2:
                                fun_app7.getGraphLoadCharacteristic(dataframe=df_GE)

                with sub_tab3:
                    buffer_data = fun_app7.get_bytes_yaml(dictionary=GE_data)
                    excel = to_excel(df_GE)

                    with st.container(border=True):
                        with st.container(border=True):
                            st.markdown("**Archivos de opciones de ingreso de datos:**")
                            st.download_button(
                                label="💾 Descargar **:blue[archivo de datos]** del grupo electrógeno **YAML**",
                                data=buffer_data,
                                file_name=fun_app7.name_file_head(name="GE_data.yaml"),
                                mime="text/yaml"
                                )
                            
                        with st.container(border=True):
                            st.markdown("**Archivos de resultados:**")
                            st.download_button(
                                label="📄 Descargar **:blue[Resultados]** del grupo electrógeno **XLSX**",
                                data=excel,
                                file_name=fun_app7.name_file_head(name="GE_characteristicCurve.xlsx"),
                                mime="xlsx")                
