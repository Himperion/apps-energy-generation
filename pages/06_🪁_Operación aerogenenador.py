# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import yaml
from io import BytesIO
from funtions import fun_app6

from funtions import general

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

selectDataEntryOptions = ["🪁 Datos del aerogenerador",
                          "💾 Cargar archivo de datos del aerogenerador YAML"]

#%% main

st.markdown("# 🪁 Operación aerogenerador")

tab1, tab2 = st.tabs(["📑 Información", "📝 Entrada de datos"])  

with tab1:
    with st.expander("**Marco teórico**"): 
        st.markdown("Marco teórico")
    with st.expander("**Ingreso de datos**"):
        st.markdown("Para esta sección, los datos pueden ingresarse de las siguientes maneras:")
        with st.container(border=True):
            st.markdown(f"**:blue[{selectDataEntryOptions[0]}:]**")
            st.markdown("Sí cuenta con los datos de la ficha técnica del aerogenerador puede ingresar manualmente desde este apartado.")
            st.markdown(f"**:blue[{selectDataEntryOptions[1]}:]**")
            st.markdown("Este archivo **YAML** para el ingreso rápido de información es descargado en la sección de **🧩 Componentes**.")
    
with tab2:
    data_entry_options = st.selectbox(label="Opciones de ingreso de datos", options=selectDataEntryOptions,
                                      index=0, placeholder="Selecciona una opción")
    
    if data_entry_options == selectDataEntryOptions[0]:
        with st.container(border=True):
            st.markdown("⚙️ **:blue[{0}:]**".format("Parámetros del aerogenerador"))
            Pnom = general.widgetNumberImput(dictParam=dict_params["P_nom"], key="Pnom", disabled=False)
            D = general.widgetNumberImput(dictParam=dict_params["D"], key="D", disabled=False)

        with st.form("formWind"):
            st.markdown("🍃 **:blue[{0}:]**".format("Características de velocidad del viento"))

            col1, col2, col3 = st.columns(3)

            with col1:
                Vin = general.widgetNumberImput(dictParam=dict_params["V_in"], key="Vin", disabled=False)
            with col2:
                Vnom = general.widgetNumberImput(dictParam=dict_params["V_nom"], key="Vnom", disabled=False)
            with col3:
                Vmax = general.widgetNumberImput(dictParam=dict_params["V_max"], key="Vmax", disabled=False)

            submittedFormWind = st.form_submit_button("Validar parámetros")

            if submittedFormWind:
                if Vin < Vnom < Vmax:
                    st.success("Parámetros validos", icon="✅")
                else:
                    st.error("Parámetros incompatibles", icon="🚨")  

    elif data_entry_options == selectDataEntryOptions[1]:
        with st.container(border=True):
            uploaded_file_yaml = st.file_uploader(label="Sube tu archivo YAML", type=["yaml", "yml"])

    with st.container(border=True):
        st.markdown("📌 **:blue[{0}:]**".format("Datos del sitio"))
        
        rho = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=dict_params["rho"], key="rho", disabled=False))

        archive_Vwind = st.file_uploader("Cargar archivo **Velocidad del viento** (m/s)", type={"xlsx"})
            
        fun_app6.get_download_button(**template)
       
    app_submitted = st.button("Aceptar")

    if app_submitted:
        params_turbine, df_turbine = None, None

        if data_entry_options == selectDataEntryOptions[0]:
            if Vin < Vnom < Vmax:
                params_turbine = {
                    "D" : D, 
                    "V_in" : Vin, 
                    "V_nom" : Vnom, 
                    "V_max" : Vmax, 
                    "P_nom" : Pnom
                    }
            else: 
                st.error("Características de velocidad del viento incompatiobles", icon="🚨")
        
        elif data_entry_options == selectDataEntryOptions[1]:

            if uploaded_file_yaml is not None:
                params_turbine = yaml.safe_load(uploaded_file_yaml)
            else:
                st.warning("Falta cargar archivo **YAML** (.yaml)", icon="⚠️")

        if archive_Vwind is not None and params_turbine is not None:
            check = False
            try:
                df_input = pd.read_excel(archive_Vwind)
                df_turbine, check, columns_options_sel = general.checkDataframeInput(dataframe=df_input, options=items_options_columns_df)
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
                                                                  "📈 Curva de potencia del  aerogenerador",
                                                                  "📉 Curva de eficiencia del aerogenerador",
                                                                  "💾 Descargas"])
                
                with sub_tab1:
                    with st.container(border=True):
                        st.dataframe(df_powerTurbine)

                with sub_tab2:
                    xval = df_values["V_wind"]
                    y1val = df_values["P_gen"]
                    y2val = df_values["n_turbine"]

                    points_y1 = {
                        "Vnom": (params_turbine["V_nom"], 0),
                        "Pnom": (0, params_turbine["P_nom"]),
                        "Nom": (params_turbine["V_nom"], params_turbine["P_nom"])
                        }

                    lines_y1 = [
                        ("Nom", "Vnom"),
                        ("Pnom", "Nom")
                        ]

                    title = "Curva aerogenerador (Paero-Vwind)"
                    xlabel = "Velocidad de viento (m/s)"
                    y1_label = "Potencia del aerogenerador (kW)"
                    y2_label = "Eficiencia del aerogenerador (%)"

                    #fun_app6.curve_x_y(xval, yval, points, lines, title, xlabel, ylabel)

                    fun_app6.curve_x_yy(x=xval,
                                        y1=y1val, y2=y2val,
                                        points_y1=points_y1, points_y2={},
                                        lines_y1=lines_y1, lines_y2=[],
                                        x_label=xlabel, y1_label=y1_label, y2_label=y2_label, title=title)

                with sub_tab3:
                    xval = df_values["V_wind"]
                    yval = df_values["n_turbine"]

                    points, lines = {}, []

                    title = "Curva de eficiencia"
                    xlabel = "Velocidad de viento (m/s)"
                    ylabel = "Eficiencia (%)"

                    fun_app6.curve_x_y(xval, yval, points, lines, title, xlabel, ylabel)

                    y1 = df_values["P_ideal"]
                    y2 = df_values["P_betz"]
                    y3 = df_values["P_gen"]

                    label_Y = ["P_ideal(kW)", "P_betz(kW)", "P_gen(kW)"]

                    title = "Curva de potencias"
                    xlabel = "Velocidad de viento (m/s)"
                    ylabel = "Potencia (kW)"

                    fun_app6.curve_x_yyy(xval, y1, y2, y3, title, xlabel, ylabel, label_Y)

                with sub_tab4:
                    bufferData = general.getBytesYaml(dictionary=params_turbine)
                    excel = to_excel(df_powerTurbine)

                    with st.container(border=True):

                        buttonYaml = general.yamlDownloadButton(bytesFileYaml=bufferData,
                                                                file_name="AERO_data",
                                                                label="💾 Descargar **:blue[archivo de datos]** del aerogenerador **YAML**") 
                    
                        st.download_button(
                            label="📄 Descargar **:blue[Potencias]** del aerogenerador **XLSX**",
                            data=excel,
                            file_name=general.nameFileHead(name="AERO_windTurbinePower.xlsx"),
                            mime="xlsx")
        else:
            if archive_Vwind is None:
                st.warning("Falta cargar archivo **Excel** (.xlsx)", icon="⚠️")
