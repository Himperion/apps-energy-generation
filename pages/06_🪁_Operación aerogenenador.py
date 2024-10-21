# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import yaml
from io import BytesIO
from funtions import fun_app6

#%% funtions

@st.cache_data
def to_excel(df: pd.DataFrame):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    
    processed_data = output.getvalue()
        
    return processed_data

#%% global variables

with open("files//[AERO] - params.yaml", 'r') as archivo:
    dict_params = yaml.safe_load(archivo)

items_options_columns_df = {
    "Vwind" : ["Vwind(m/s)", "Vwind 10msnm(m/s)", "Vwind 50msnm(m/s)"]
}

template = {
    "directory": "files",
    "name_file": "[Plantilla] - Potencia aerogenerador",
    "format_file": "xlsx",
    "description": "Velocidad del viento"
}

select_data_entry_options = ["🛠️ Datos del aerogenerador",
                             "💾 Cargar archivo de datos del aerogenerador YAML"]

#%% main

st.markdown("# 🪁 Operación aerogenerador")

tab1, tab2 = st.tabs(["📑 Marco teórico", "📝 Entrada de datos"])  

with tab1:
    st.text("Ajaaaaaaaaaaaaa")

with tab2:
    data_entry_options = st.selectbox(label="Opciones de ingreso de datos", options=select_data_entry_options,
                                      index=0, placeholder="Selecciona una opción")
    
    if data_entry_options == select_data_entry_options[0]:
        with st.container(border=True):
            st.markdown("⚙️ **:blue[{0}:]**".format("Parámetros del aerogenerador"))
            
            D = fun_app6.get_widget_number_input(label=fun_app6.get_label_params(dict_param=dict_params["D"]),
                                                 variable=dict_params["D"]["number_input"])
            Vin = fun_app6.get_widget_number_input(label=fun_app6.get_label_params(dict_param=dict_params["V_in"]),
                                                   variable=dict_params["V_in"]["number_input"])
            Vnom = fun_app6.get_widget_number_input(label=fun_app6.get_label_params(dict_param=dict_params["V_nom"]),
                                                    variable=dict_params["V_nom"]["number_input"])
            Vmax = fun_app6.get_widget_number_input(label=fun_app6.get_label_params(dict_param=dict_params["V_max"]),
                                                    variable=dict_params["V_max"]["number_input"])
            Pnom = fun_app6.get_widget_number_input(label=fun_app6.get_label_params(dict_param=dict_params["P_nom"]),
                                                    variable=dict_params["P_nom"]["number_input"])
            
    elif data_entry_options == select_data_entry_options[1]:
        with st.container(border=True):
            uploaded_file_yaml = st.file_uploader(label="Sube tu archivo YAML", type=["yaml", "yml"])

    with st.container(border=True):
        st.markdown("📌 **:blue[{0}:]**".format("Datos del sitio"))
    
        rho = fun_app6.get_widget_number_input(label=fun_app6.get_label_params(dict_param=dict_params["rho"]),
                                                  variable=dict_params["rho"]["number_input"])

        archive_Vwind = st.file_uploader("Cargar archivo **Velocidad del viento** (m/s)", type={"xlsx"})
            
        fun_app6.get_download_button(**template)
       
    app_submitted = st.button("Aceptar")

    if app_submitted:
        params_turbine, df_turbine = None, None 

        if data_entry_options == select_data_entry_options[0]:
            params_turbine = {
                "D" : D, 
                "V_in" : Vin, 
                "V_nom" : Vnom, 
                "V_max" : Vmax, 
                "P_nom" : Pnom
                }
        
        elif data_entry_options == select_data_entry_options[1]:

            if uploaded_file_yaml is not None:
                params_turbine = yaml.safe_load(uploaded_file_yaml)
            else:
                st.warning("Falta cargar archivo **YAML** (.yaml)", icon="⚠️")

        if archive_Vwind is not None and params_turbine is not None:
            check = False
            try:
                df_input = pd.read_excel(archive_Vwind)
                df_turbine, check, columns_options_sel = fun_app6.check_dataframe_input(dataframe=df_input,
                                                                                        options=items_options_columns_df)
            except:
                st.error("Error al cargar archivo **Excel** (.xlsx)", icon="🚨")

            if check:
                df_powerTurbine = fun_app6.get_dataframe_power_wind_turbine(params=params_turbine,
                                                                            rho=rho,
                                                                            dataframe=df_turbine,
                                                                            column=columns_options_sel)
                
                df_values = fun_app6.get_values_curve_turbine(params=params_turbine,
                                                              rho=rho)

                sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(["📋 Resultados",
                                                                  "📈 Curva característica del aerogenerador",
                                                                  "📉 Curva de potencia del aerogenerador",
                                                                  "💾 Descargas"])
                
                with sub_tab1:
                    with st.container(border=True):
                        st.dataframe(df_powerTurbine)

                with sub_tab2:
                    df_values = fun_app6.get_values_curve_turbine(params=params_turbine,
                                                                  rho=rho)

                    xval = df_values["V_wind"]
                    yval = df_values["P_gen"]

                    points = {
                        "Vnom": (params_turbine["V_nom"], 0),
                        "Pnom": (0, params_turbine["P_nom"]),
                        "Nom": (params_turbine["V_nom"], params_turbine["P_nom"])
                        }

                    lines = [
                        ("Nom", "Vnom"),
                        ("Pnom", "Nom")
                        ]

                    title = "Curva aerogenerador (Paero-Vwind)"
                    xlabel = "Velocidad de viento (m/s)"
                    ylabel = "Potencia del aerogenerador (kW)"

                    fun_app6.curve_x_y(xval, yval, points, lines, title, xlabel, ylabel)

                with sub_tab3:
                    xval = df_turbine[columns_options_sel["Vwind"]]
                    yval = df_turbine["Pgen(kW)"]

                    points, lines = {}, []

                    title = "Curva aerogenerador (Paero-Vwind)"
                    xlabel = "Velocidad de viento (m/s)"
                    ylabel = "Potencia del aerogenerador (kW)"

                    fun_app6.curve_x_y(xval, yval, points, lines, title, xlabel, ylabel)

                with sub_tab4:
                    buffer_data = fun_app6.get_bytes_yaml(dictionary=params_turbine)
                    excel = to_excel(df_powerTurbine)

                    with st.container(border=True):
                    
                        st.download_button(
                            label="📑 Descargar **:blue[archivo de datos]** del aerogenerador **YAML**",
                            data=buffer_data,
                            file_name=fun_app6.name_file_head(name="AERO_data.yaml"),
                            mime="text/yaml"
                            )
                    
                        st.download_button(
                            label="📄 Descargar **:blue[Potencias]** del aerogenerador **XLSX**",
                            data=excel,
                            file_name=fun_app6.name_file_head(name="AERO_windTurbinePower.xlsx"),
                            mime="xlsx")
        else:
            if archive_Vwind is None:
                st.warning("Falta cargar archivo **Excel** (.xlsx)", icon="⚠️")
