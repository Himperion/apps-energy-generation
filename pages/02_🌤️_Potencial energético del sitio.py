# -*- coding: utf-8 -*-

import warnings, yaml
import pandas as pd
import streamlit as st
from io import BytesIO
from funtions import fun_app2

warnings.filterwarnings("ignore")

#%% funtions

@st.cache_data
def to_excel(df: pd.DataFrame):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    
    processed_data = output.getvalue()
        
    return processed_data

#%% global variables

with open("files//[PV] - params.yaml", 'r') as archivo:
    dict_params = yaml.safe_load(archivo)

template = {
    "directory": "files",
    "name_file": "[Plantilla] - Temperatura de operación",
    "format_file": "xlsx",
    "description": "Irradiancia efectiva y Temperatura ambiente del sitio"
}

items_options_columns_df = {
    "Geff" : ("Gef(W/m^2)", "Gef(W/m²)", "Gin(W/m²)", "Gin(W/m^2)"),
    "Tamb" : ("Tamb(°C)", "Tamb 2msnm(°C)")
}

dict_parameters = {
    "Irradiancia (W/m^2)" : ("ALLSKY_SFC_SW_DWN", "Gin(W/m²)"),
    "Velocidad del viento a 10 msnm (m/s)" : ("WS10M", "Vwind 10msnm(m/s)"),
    "Velocidad del viento a 50 msnm (m/s)" : ("WS50M", "Vwind 50msnm(m/s)"),
    "Temperatura ambiente a 2 msnm (°C)" : ("T2M", "Tamb 2msnm(°C)")
    }

options_multiselect = list(dict_parameters.keys())

select_data_entry_options = ["📌 Datos del sitio",
                             "💾 Cargar archivo de datos del sitio YAML"]

select_coordinate_options = ["Sistema sexagesimal GMS",
                             "Sistema decimal GD"]

#%% main

st.markdown("# 🌤️ Datos climáticos y potencial energético del sitio")

tab1, tab2, tab3 = st.tabs(["📑 Marco teórico", "📝 Entrada de datos", "🌡️ Temperatura de operación"])

with tab1:
    st.text("Ajaaaaaaaaaaaaa")

with tab2:
    data_entry_options = st.selectbox(label="Opciones de ingreso de datos", options=select_data_entry_options,
                                      index=0, placeholder="Selecciona una opción")
    
    if data_entry_options == select_data_entry_options[0]:
        coordinate_options = st.selectbox(label="Opciones de ingreso de coordenadas geográficas",
                                          options=select_coordinate_options,
                                          index=1, placeholder="Selecciona una opción")
        
        with st.container(border=True):
            st.markdown("🌎 **:blue[{0}:]**".format("Datos del sitio"))
        
            if coordinate_options == select_coordinate_options[0]:
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns(4)

                    NS = col1.selectbox("**Latitud:**", ["N", "S"], index=0)
                    lat_degrees = col2.number_input(label="Grados", min_value=0, value=7)
                    lat_minutes = col3.number_input(label="Minutos", min_value=0, value=8)
                    lat_seconds = col4.number_input(label="Segundos", min_value=0.0, format="%.4f", value=31.4016)

                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns(4)

                    EO = col1.selectbox("**Longitud:**", ["W", "E"], index=0)
                    lon_degrees = col2.number_input(label="Grados", min_value=0, value=73)
                    lon_minutes = col3.number_input(label="Minutos", min_value=0, value=7)
                    lon_seconds = col4.number_input(label="Segundos", min_value=0.0, format="%.4f", value=16.4316)

            elif coordinate_options == select_coordinate_options[1]:
                col1, col2 = st.columns(2)

                lat_input = col1.number_input('Ingrese la latitud:', min_value=-90.0, max_value=90.0, step=0.000001, format="%.6f", value=7.142056)
                lon_input = col2.number_input('Ingrese la longitud:', min_value=-180.0, max_value=180.0, step=0.000001, format="%.6f", value=-73.121231)

        with st.container(border=True):
            st.markdown("🗓️ **:blue[{0}:]**".format("Estampa de tiempo"))

            col1, col2 = st.columns(2)

            date_ini = col1.date_input("Fecha de Inicio:")
            date_end = col2.date_input("Fecha Final:")

    elif data_entry_options == select_data_entry_options[1]:
        with st.container(border=True):
            uploaded_file_yaml = st.file_uploader(label="Sube tu archivo YAML", type=["yaml", "yml"])
        
    options = fun_app2.get_expander_params(list_show_output=[key for key in dict_parameters])
            
    app_submitted = st.button("Aceptar")

    if app_submitted: 
        dict_params = None

        if data_entry_options == select_data_entry_options[0]:
            if coordinate_options == select_coordinate_options[0]:
        
                dict_data = {
                    "lat_NS": NS,
                    "lat_degrees": lat_degrees,
                    "lat_minutes": lat_minutes,
                    "lat_seconds": lat_seconds,
                    "lon_EO": EO,
                    "lon_degrees": lon_degrees,
                    "lon_minutes": lon_minutes,
                    "lon_seconds": lon_seconds,
                    "date_ini": date_ini,
                    "date_end": date_end,
                }

                dict_params = fun_app2.GMS_2_GD(dict_data)
        
            elif coordinate_options == select_coordinate_options[1]:

                dict_params = {
                    "latitude": lat_input,
                    "longitude": lon_input,
                    "start": date_ini,
                    "end": date_end
                }

        elif data_entry_options == select_data_entry_options[1]:
            if uploaded_file_yaml is not None:
                try:
                    dict_params = yaml.safe_load(uploaded_file_yaml)
                except:
                    st.error("Error al cargar archivo **YAML** (.yaml)", icon="🚨")
            else:
                st.warning("Cargar archivo **YAML** (.yaml)", icon="⚠️")

        if dict_params is not None:
            cal_rows = fun_app2.cal_rows(dict_params["start"], dict_params["end"], steps=60)

            if len(options) != 0:
                if cal_rows > 0:
                    parameters = fun_app2.get_parameters_NASA_POWER(options, dict_parameters)
                    
                    data = fun_app2.get_dataframe_NASA_POWER(dict_params,
                                                             parameters,
                                                             dict_parameters)
                    
                    data = fun_app2.add_column_dates(dataframe=data,
                                                     date_ini=dict_params["start"],
                                                     rows=cal_rows,
                                                     steps=60)
                    
                    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📋 Parámetros", "📈 Gráficas", "💾 Descargas"])

                    with sub_tab1:
                        with st.container(border=True):
                            st.dataframe(data)

                    with sub_tab2:
                        with st.container(border=True):
                            fun_app2.view_dataframe_information(data)

                    with sub_tab3:
                        excel = to_excel(data)
                        buffer_params = fun_app2.get_bytes_yaml(dictionary=dict_params)

                        with st.container(border=True):
                            st.download_button(
                                label="📄 Descargar **:blue[Datos climaticos y potencial energético del sitio]** del sitio **XLSX**",
                                data=excel,
                                file_name=fun_app2.name_file_head(name="PES_params.xlsx"),
                                mime="xlsx")
                            
                            st.download_button(
                                label="📌 Descargar **:blue[archivo de datos]** del sitio **YAML**",
                                data=buffer_params,
                                file_name=fun_app2.name_file_head(name="PES_data.yaml"),
                                mime="text/yaml"
                                )
                    
                else:
                    if cal_rows == 0:
                        st.warning("La {0} debe ser diferente a la {1}".format(":blue[Fecha de Inicio]", ":blue[Fecha final]"), icon="⚠️")
                    if cal_rows < 0:
                        st.warning("La {0} debe ser menor a la {1}".format(":blue[Fecha de Inicio]", ":blue[Fecha final]"), icon="⚠️")
            else:
                st.warning("Ingrese por lo menos una opción en {0}".format(":blue[Seleccione los datos a cargar]"), icon="⚠️")
                    
with tab3:

    with st.container(border=True):
        label_Gef_Tamb = "Cargar archivo {0} y {1}".format("**Irradiancia efectiva** (m/s)", "**Temperatura ambiente** (°C).")
        archive_Gef_Tamb = st.file_uploader(label=label_Gef_Tamb, type={"xlsx"})

        fun_app2.get_download_button(**template)

    NOCT = fun_app2.get_widget_number_input(label=fun_app2.get_label_params(dict_param=dict_params["NOCT"]),
                                            variable=dict_params["NOCT"]["number_input"])
    
    app_submitted_2 = st.button("Aceptar", key="app_submitted_2")

    if app_submitted_2:
        if archive_Gef_Tamb is not None:
            check = False
            try:
                df_input = pd.read_excel(archive_Gef_Tamb)
                df_input, check, columns_options_sel = fun_app2.check_dataframe_input(dataframe=df_input, options=items_options_columns_df)
            except:
                st.error("Error al cargar archivo **Excel** (.xlsx)", icon="🚨")

            if check:
                df_output = fun_app2.get_column_Toper(dataframe=df_input,
                                                      options_sel=columns_options_sel,
                                                      NOCT=NOCT,
                                                      column_name=items_options_columns_df["Tamb"][0])
                
                sub_tab1, sub_tab2 = st.tabs(["📋 Parámetros", "💾 Descargas"])

                with sub_tab1:
                    with st.container(border=True):
                        st.dataframe(df_output)

                with sub_tab2:
                    excel = to_excel(df_output)

                    with st.container(border=True):
                        st.download_button(
                            label="📄 Descargar **:blue[Temperatura de operación del módulo]** del sitio **XLSX**",
                            data=excel,
                            file_name=fun_app2.name_file_head(name="PES_addToper.xlsx"),
                            mime="xlsx")

                
            else:
                st.error("Error al cargar archivo **Excel** (.xlsx)", icon="🚨")
        else:
            st.warning("Cargar archivo **Excel** (.xlsx)", icon="⚠️")
                
    