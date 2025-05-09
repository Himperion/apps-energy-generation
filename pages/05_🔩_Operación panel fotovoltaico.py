# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import yaml
from io import BytesIO

from funtions import general, fun_app5

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

with open("files//[PV] - dict_replace.yaml", 'r') as archivo:
    dict_rename = yaml.safe_load(archivo)

with open("files//[PV] - celltype.yaml", 'r') as archivo:
    celltype = yaml.safe_load(archivo)

text = {
    "subheader_1" : "Los párametros de **Single diode** se calculan para un módulo fotovoltaico en condiciones **STC** de operación. Sí se desea hacer un análisis del panel fotovoltaico en condiciones distintas al **STC** es necesario aplicar ajustes a los parámetros para que reflejen un comportamiento acorde a los cambios en la operación.",
    "subheader_2" : "Este aplicativo web para efectuar la corrección de parámetros del módulo se logra mediante la librería **PVLIB** de Python que permite simular sistemas de energía fotovoltaicos.",
    "subheader_3" : "El aplicativo permite obtener los siguientes parámetros:"
}

options_celltype = fun_app5.celltype_options(celltype)

selectDataEntryOptions = ["🔧 Parámetros del panel",
                          "🪟 Datos del panel",
                          "💾 Cargar archivo de datos del panel fotovoltaico YAML",
                          "💾 Cargar archivo de parámetros del panel fotovoltaico YAML"]

optionsSelOper = ["📗 Única", "📚 Múltiple"]

items_options_columns_df = {
    "Geff" : ["Gef(W/m^2)", "Gef(W/m²)", "Gin(W/m²)", "Gin(W/m^2)"],
    "Toper" : ["Toper(°C)"]
}

columns_options_sel = {'Geff': 'Gin(W/m²)', 'Toper': 'Toper(°C)'}

template = {
    "directory": "files",
    "name_file": "[Plantilla] - Ajuste de parámetros del panel",
    "format_file": "xlsx",
    "description": "Irradiancia efectiva y Temperatura de operación del módulo"
}

keys_show_output, dict_show_output, list_show_output = fun_app5.get_show_output(dict_params)

#%% main

st.sidebar.link_button(":violet-badge[**Ir a la app de herramientas**]", "https://app-nasa-power.streamlit.app/", icon="🔧")

st.markdown("# 🔩 Operación panel fotovoltaico")

tab1, tab2 = st.tabs(["📑 Información", "📝 Entrada de datos"])  

with tab1:
    with st.expander(":violet-badge[**Marco teórico**]", icon="✏️"):
        st.subheader("Introducción", divider="violet")
        st.markdown(text["subheader_1"])

        col1, col2, col3 = st.columns( [0.25, 0.5, 0.25])
        with col2:
            st.image("images//app5_img1.png")

        st.subheader("Ingreso de datos", divider="blue")
        st.markdown("Para esta sección, los datos pueden ingresarse de las siguientes maneras:")

        with st.container(border=True):
            st.markdown(f"**:blue[{selectDataEntryOptions[0]}:]**")
            st.markdown("Sí ya cuenta con los parámetros del panel fotovoltaico **alpha_sc**, **Iph**, **Isat**, **Rs**, **Rp**, **nNsVt** y  **Ajuste_Isc** en condiciones STC puede ingresarlos manualmente en esta sección. (Los parámetros STC pueden ser obtenidos en la sección **🔧 Parámetros panel fotovoltaico**.)")
            st.markdown(f"**:blue[{selectDataEntryOptions[1]}:]**")
            st.markdown("Sí cuenta con los datos de la ficha técnica del panel fotovoltaico puede ingresar manualmente desde este apartado.")
            st.markdown(f"**:blue[{selectDataEntryOptions[2]}:]**")
            st.markdown("Este archivo **YAML** para el ingreso rápido de información es descargado en la sección de **🧩 Componentes**.")
            st.markdown(f"**:blue[{selectDataEntryOptions[3]}:]**")
            st.markdown("Este archivo YAML para el ingreso rápido de información puede ser descargado en la sección de resultados de **🔧 Parámetros panel fotovoltaico**.")

        st.subheader("Opciones de la sección", divider="green")
        st.markdown("Esta sección es posible seleccionar las opciones del ingreso de condiciones **Gef(Irradiancia efectiva en W/m^2)** y **Toper(Temperatura de operación del módulo en °C)**:")
        
        with st.container(border=True):
            st.markdown(f"**:green[{optionsSelOper[0]}:]**")
            st.markdown("Permite el ingreso manual de un único valor de **Gef** y **Toper**. como resultado se mostrará la comparación de la condición STC y de operación ingresada. Mediante valores y curvas características.")
            st.markdown(f"**:green[{optionsSelOper[1]}:]**")
            st.markdown("Permite el ingreso mediante un archivo **XLSX** de múltiples valores de **Gef** y **Toper**. Como resultado se podrá descargar un archivo **XLSX** de parámetros para cada par de puntos de operación del panel.")
            
    with st.expander(":blue-badge[**Infografía**]", icon="📝"):
        infographic_path = "files/infographic/05_OPER-PV.pdf"
        infographic_label = "Operación panel fotovoltaico"
    
        general.infographicViewer(infographic_path, infographic_label)
      
with tab2:   
    dataEntryOptions = st.selectbox(label="Opciones de ingreso de datos", options=selectDataEntryOptions,
                                    index=0, placeholder="Selecciona una opción")
    
    if dataEntryOptions == selectDataEntryOptions[0]:
        with st.container(border=True):
            st.markdown("⚙️ **:blue[{0}:]**".format("Parámetros del módulo en condiciones STC"))
            
            Alfa = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["alpha_sc"]),
                                                    variable=dict_params["alpha_sc"]["number_input"])
            Iph = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["Iph"]),
                                                   variable=dict_params["Iph"]["number_input"])
            Isat = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["Isat"]),
                                                    variable=dict_params["Isat"]["number_input"])
            Rs = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["Rs"]),
                                                  variable=dict_params["Rs"]["number_input"])
            Rp = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["Rp"]),
                                                  variable=dict_params["Rp"]["number_input"])
            nNsVt = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["nNsVt"]),
                                                     variable=dict_params["nNsVt"]["number_input"])
            Ajuste_Isc = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["Ajuste_Isc"]),
                                                          variable=dict_params["Ajuste_Isc"]["number_input"])

    elif dataEntryOptions == selectDataEntryOptions[1]:
        with st.container(border=True):
            st.markdown("🔌 **:blue[{0}:]**".format("Características eléctricas"))
            col1, col2 = st.columns(2)
            with col1:
                Vmpp = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["Vmpp"]),
                                                        variable=dict_params["Vmpp"]["number_input"])
                Voc = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["Voc"]),
                                                       variable=dict_params["Voc"]["number_input"])
            with col2:
                Impp = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["Impp"]),
                                                        variable=dict_params["Impp"]["number_input"])
                Isc = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["Isc"]),
                                                       variable=dict_params["Isc"]["number_input"])
            
        with st.container(border=True):
            st.markdown("🌡️ **:blue[{0}:]**".format("Características de temperatura"))
            
            Alfa = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["alpha_sc"]),
                                                    variable=dict_params["alpha_sc"]["number_input"])
            Beta = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["beta_voc"]),
                                                    variable=dict_params["beta_voc"]["number_input"])
            Delta = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["gamma_pmp"]),
                                                     variable=dict_params["gamma_pmp"]["number_input"])
        
        with st.container(border=True):
            st.markdown("🔧 **:blue[{0}:]**".format("Características mecánicas"))
            
            cell_type = st.selectbox("Tecnologia", options=options_celltype, index=4)

            Ns = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["cells_in_series"]),
                                                  variable=dict_params["cells_in_series"]["number_input"])
            
    elif dataEntryOptions == selectDataEntryOptions[2]:
        with st.container(border=True):
            st.markdown("💾 **:blue[Archivo de datos del panel fotovoltaico]**")
            uploadedYamlDATA = st.file_uploader(label="Cargar archivo YAML", type=["yaml", "yml"])

    elif dataEntryOptions == selectDataEntryOptions[3]:
        with st.container(border=True):
            st.markdown("💾 **:blue[Archivo de parámetros del panel fotovoltaico]**")
            uploadedYamlPARAMS = st.file_uploader(label="Cargar archivo YAML", type=["yaml", "yml"])
        
    with st.container(border=True):
        st.markdown("🧑‍🔧 **:blue[{0}:]**".format("Conexión de los módulos"))
        col1, col2 = st.columns(2)

        with col1:
            PVs = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["PVs"]),
                                                   variable=dict_params["PVs"]["number_input"])
        with col2:
            PVp = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["PVp"]),
                                                   variable=dict_params["PVp"]["number_input"])
            
    with st.container(border=True):
        st.markdown("🌞 **:blue[{0}:]**".format("Condiciones de operación del módulo"))

        optionSel = st.radio(label="Opciones para el ingreso de condiciones",
                              options=optionsSelOper,
                              captions=["Ingreso de una única condición de irradiancia y temperatura de operación.",
                                        "Ingreso de múltiples condiciones de irradiancia y temperatura de operación."])
        
        if optionSel == optionsSelOper[0]:
            col1, col2 = st.columns(2)
            with col1:
                Geff = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["Geff"]),
                                                           variable=dict_params["Geff"]["number_input"])
            with col2:
                Toper = fun_app5.get_widget_number_input(label=fun_app5.get_label_params(dict_param=dict_params["Toper"]),
                                                         variable=dict_params["Toper"]["number_input"])
                
        elif optionSel == optionsSelOper[1]:
            label_Gef_Toper = "Cargar archivo {0} y {1}".format("**Irradiancia efectiva** (m/s)", "**Temperatura de operación del módulo** (°C).")
            archive_Gef_Toper = st.file_uploader(label=label_Gef_Toper, type={"xlsx"})
                
            fun_app5.get_download_button(**template)            

    show_output = fun_app5.get_expander_params(list_show_output)
    app_submitted = st.button("Aceptar")

    if app_submitted:
        conditions, PV_params, PV_data = None, None, None

        if dataEntryOptions == selectDataEntryOptions[0]:
            PV_params = {
                "alpha_sc": Alfa,
                "a_ref": nNsVt,
                "I_L_ref": Iph,
                "I_o_ref": Isat,
                "R_sh_ref": Rp,
                "R_s": Rs,
                "Adjust": Ajuste_Isc
                }

        elif dataEntryOptions == selectDataEntryOptions[1]:
            PV_data = {
                "celltype": fun_app5.for_options_get_celltype(cell_type),
                "v_mp": Vmpp,
                "i_mp": Impp,
                "v_oc": Voc,
                "i_sc": Isc,
                "alpha_sc": general.changeUnitsK(Alfa, Isc),
                "beta_voc": general.changeUnitsK(Beta, Voc),
                "gamma_pmp": Delta,
                "cells_in_series": Ns
                }
            
            PV_params = fun_app5.get_PV_params(**PV_data)

        elif dataEntryOptions == selectDataEntryOptions[2]:
            try:
                PV_data = yaml.safe_load(uploadedYamlDATA)
                PV_params = fun_app5.get_PV_params(**PV_data)
            except:
                st.error("Error al cargar archivo **YAML** (.yaml)", icon="🚨")

        elif dataEntryOptions == selectDataEntryOptions[3]:
            try:
                PV_params = yaml.safe_load(uploadedYamlPARAMS)
            except:
                st.error("Error al cargar archivo **YAML** (.yaml)", icon="🚨")

        if optionSel == optionsSelOper[0]:
            conditions = pd.DataFrame([(1000, 25), (Geff, Toper)], columns=['Geff', 'Toper'])

        elif optionSel == optionsSelOper[1]:
            if archive_Gef_Toper is not None:
                check = False
                try:
                    df_input = pd.read_excel(archive_Gef_Toper)
                    df_pv, check, columns_options_sel = general.checkDataframeInput(dataframe=df_input, options=items_options_columns_df)
                except:
                    st.error("Error al cargar archivo **Excel** (.xlsx)", icon="🚨")

                if check:
                    conditions = fun_app5.get_dataframe_conditions(dataframe=df_pv, columns_options_sel=columns_options_sel)
                else:
                    st.error("Error al cargar archivo **Excel** (.xlsx)", icon="🚨")
            else:
                st.warning("Cargar archivo **Excel** (.xlsx)", icon="⚠️")

        if conditions is not None and PV_params is not None:
            
            dict_replace = fun_app5.get_dict_replace(dict_rename, dict_params)
            df_pv = fun_app5.get_singlediode(conditions, PV_params, PVs, PVp)

            if optionSel == optionsSelOper[0]:
                data_i_from_v = {
                        "voltage": np.linspace(0., df_pv['Voc'].values, 100),
                        "photocurrent": df_pv["Iph"].values,
                        "saturation_current": df_pv["Isat"].values,
                        "resistance_series": df_pv["Rs"].values,
                        "resistance_shunt": df_pv["Rp"].values,
                        "nNsVth": df_pv["nNsVt"].values,
                        "method": "lambertw"
                    }
                
                v, i, p = fun_app5.get_current_and_power_with_voltage(df=df_pv, **data_i_from_v)
                
                sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📋 Parámetros Ajustados", "📈 Curva I-V", "📉 Curva P-V"])

                with sub_tab1:
                    labels_output = fun_app5.get_labels_params_output(show_output, dict_show_output)
                    head_column = ["Parámetro", "Condiciones STC", "Ajuste de operación"]

                    general.getPrintParamsDataframe(df_pv, labels_output, dict_params, head_column)

                with sub_tab2:
                    fun_app5.curveMulti_x_y(conditions, v, i, df_pv, option="current")
                    
                with sub_tab3:
                    fun_app5.curveMulti_x_y(conditions, v, p, df_pv, option="power")

            elif optionSel == optionsSelOper[1]:

                df_pv = fun_app5.get_final_dataframe(df_pv=df_pv,
                                                     df_input=df_input,
                                                     dict_replace=dict_replace,
                                                     dict_conditions=columns_options_sel,
                                                     list_output=show_output)

                sub_tab1, sub_tab2 = st.tabs(["📋 Parámetros Ajustados", "💾 Descargas"])

                with sub_tab1:
                    with st.container(border=True):
                        st.dataframe(df_pv)

                with sub_tab2:
                    excel = to_excel(df_pv)

                    with st.container(border=True):
                        st.download_button(label="📄 Descargar **:blue[archivo de pámateros ajustados]** del panel fotovoltaico **XLSX**",
                                           data=excel,
                                           file_name=fun_app5.name_file_head(name="PV_paramsAjust.xlsx"),
                                           mime="xlsx")
