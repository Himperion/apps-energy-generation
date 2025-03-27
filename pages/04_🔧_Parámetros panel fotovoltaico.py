# -*- coding: utf-8 -*-

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yaml
from scipy.special import lambertw
from scipy.optimize import root_scalar, fsolve

from funtions import general, fun_app4

#%% Funtions

#%% global variables

with open("files//[PV] - params.yaml", 'r') as archivo:
    dict_params = yaml.safe_load(archivo)

with open("files//[PV] - dict_replace.yaml", 'r') as archivo:
    dict_rename = yaml.safe_load(archivo)

with open("files//[PV] - celltype.yaml", 'r') as archivo:
    celltype = yaml.safe_load(archivo)

text = {  
     "subheader_1" : "El modelo circuital de los sistemas fotovoltaicos facilita la predicción de variables eléctricas como la tensión, corriente y potencia en diversas condiciones de operación. Esto es crucial para realizar un dimensionamiento completo y preciso del sistema.",
     "subheader_2" : "El modelo **Single diode** se fundamenta en los principios de los dispositivos semiconductores y proporciona una representación de las propiedades eléctricas de un módulo fotovoltaico.",
     "subheader_3" : "La expresión de la corriente del módulo en el circuito equivalente se convierte en la ecuación fundamental del modelo que posibilita una reconstrucción aproximada de la curva de corriente-voltaje (I-V) del panel fotovoltaico."
}

options_celltype = fun_app4.celltype_options(celltype)

selectDataEntryOptions = ["🪟 Datos del panel",
                          "💾 Cargar archivo de datos del panel fotovoltaico YAML"]

#%% main

st.markdown("# 🔧 Obtención de parámetros STC")

tab1, tab2 = st.tabs(["📑 Información", "📝 Entrada de datos"])

with tab1:
    with st.expander("**Marco teórico**"):
        st.markdown(text["subheader_1"])
        st.markdown(text["subheader_2"])
            
        col1, col2, col3 = st.columns( [0.25, 0.5, 0.25])

        with col1:
            st.write("")
        with col2:
            st.image("images//app4_img1.png")
        with col3:
            st.write("")

        st.markdown(text["subheader_3"])
        st.latex(r"""I=I_{ph}-I_{d}-I_{R_{p}}=I_{ph}-I_{sat}\cdot \left ( e\tfrac{V+I\cdot R_{s}}{N_{s}nv_{t}} -1\right )-\frac{V+I\cdot R_{s}}{R_{p}}""")

        st.markdown(general.getLabelParams(dict_param=dict_params["Iph"]))
        st.markdown(general.getLabelParams(dict_param=dict_params["n"]))
        st.markdown(general.getLabelParams(dict_param=dict_params["Vt"]))
        st.markdown(general.getLabelParams(dict_param=dict_params["cells_in_series"]))
        st.markdown(general.getLabelParams(dict_param=dict_params["Isat"]))
        st.markdown(general.getLabelParams(dict_param=dict_params["Rs"]))
        st.markdown(general.getLabelParams(dict_param=dict_params["Rp"]))

    with st.expander("**Ingreso de datos**"):
        st.markdown("Para esta sección, los datos pueden ingresarse de las siguientes maneras:")
        with st.container(border=True):
            st.markdown(f"**:blue[{selectDataEntryOptions[0]}:]**")
            st.markdown("Sí cuenta con los datos de la ficha técnica del panel fotovoltaico puede ingresar manualmente desde este apartado.")
            st.markdown(f"**:blue[{selectDataEntryOptions[1]}:]**")
            st.markdown("Este archivo **YAML** para el ingreso rápido de información es descargado en la sección de **🧩 Componentes**.")
    
with tab2:
    data_entry_options = st.selectbox(label="Opciones de ingreso de datos", options=selectDataEntryOptions,
                                      index=0, placeholder="Selecciona una opción")
    
    if data_entry_options == selectDataEntryOptions[0]:

        with st.container(border=True):
            st.markdown("🔌 **:blue[{0}:]**".format("Características eléctricas"))
            col1, col2 = st.columns(2)
            with col1:
                Vmpp = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=dict_params["Vmpp"], key="Vmpp", disabled=False))
                Voc = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=dict_params["Voc"], key="Voc", disabled=False))
            with col2:
                Impp = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=dict_params["Impp"], key="Impp", disabled=False))
                Isc = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=dict_params["Isc"], key="Isc", disabled=False))
                
        with st.container(border=True):
            st.markdown("🌡️ **:blue[{0}:]**".format("Características de temperatura"))
                
            Alfa = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=dict_params["alpha_sc"], key="Alfa", disabled=False))
            Beta = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=dict_params["beta_voc"], key="Beta", disabled=False))
            Delta = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=dict_params["gamma_pmp"], key="Delta", disabled=False))
            
        with st.container(border=True):
            st.markdown("🔧 **:blue[{0}:]**".format("Características mecánicas"))
                
            cell_type = st.selectbox("Tecnologia", options=options_celltype, index=4)

            Ns = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=dict_params["cells_in_series"], key="Ns", disabled=False))
            
    elif data_entry_options == selectDataEntryOptions[1]:
        with st.container(border=True):
            uploaded_file_yaml = st.file_uploader(label="Sube tu archivo YAML", type=["yaml", "yml"])
            
    app_5_submitted = st.button("Aceptar")

    if app_5_submitted:
        PV_data = None

        if data_entry_options == selectDataEntryOptions[0]:

            PV_data = {
                "celltype": fun_app4.for_options_get_celltype(cell_type),
                "v_mp": Vmpp,
                "i_mp": Impp,
                "v_oc": Voc,
                "i_sc": Isc,
                "alpha_sc": general.changeUnitsK(Alfa, Isc),
                "beta_voc": general.changeUnitsK(Beta, Voc),
                "gamma_pmp": Delta,
                "cells_in_series": Ns
            }

        elif data_entry_options == selectDataEntryOptions[1]:

            if uploaded_file_yaml is not None:
                PV_data = yaml.safe_load(uploaded_file_yaml)
            else:
                st.warning("Falta cargar archivo **YAML** (.yaml)", icon="⚠️")

        if PV_data is not None:
            PV_params = fun_app4.get_PV_params(**PV_data)
            SDE_params = fun_app4.from_PVparams_get_SDEparams(PV_params)
            v, i, p = fun_app4.get_values_curve_I_V_P(PV_data["v_oc"], SDE_params)

            df_curve_info = pd.DataFrame([PV_params]).rename(columns=dict_rename)

            sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(["📋 Parámetros STC",
                                                              "📈 Curva I-V",
                                                              "📉 Curva P-V",
                                                              "💾 Descargas"])

            with sub_tab1:
                head_column = ["", "Condiciones STC"]
                labels_output = ["Iph", "Isat", "Rs", "Rp", "nNsVt", "Ajuste_Isc"]

                general.getPrintParamsDataframe(df_curve_info, labels_output, dict_params, head_column)

            with sub_tab2:
                points = {
                    "Voc": (PV_data["v_oc"], 0),
                    "Isc": (0, PV_data["i_sc"]),
                    "MPP": (PV_data["v_mp"], PV_data["i_mp"]),
                    "Vmpp": (PV_data["v_mp"], 0),
                    "Impp": (0, PV_data["i_mp"])
                }

                lines = [
                    ("MPP", "Vmpp"),
                    ("Impp", "MPP")
                ]

                title = "Corriente-Voltaje (I-V)"
                xlabel = "Voltaje (V)"
                ylabel = "Corriente (A)"

                fun_app4.curve_x_y(v, i, points, lines, title, xlabel, ylabel)

            with sub_tab3:
                points = {
                    "Vmpp": (PV_data["v_mp"], 0),
                    "Pmax": (0, PV_data["v_mp"]*PV_data["i_mp"]),
                    "MPP": (PV_data["v_mp"], PV_data["v_mp"]*PV_data["i_mp"]),
                }

                lines = [
                    ("MPP", "Vmpp"),
                    ("Pmax", "MPP")
                ]

                title = "Potencia-Voltaje (P-V)"
                xlabel = "Voltaje (V)"
                ylabel = "Potencia (W)"

                fun_app4.curve_x_y(v, p, points, lines, title, xlabel, ylabel)

            with sub_tab4:
                buffer_data = general.getBytesYaml(dictionary=PV_data)
                buffer_params = general.getBytesYaml(dictionary=PV_params)

                with st.container(border=True):
                    
                    buttonDowmload2 = general.yamlDownloadButton(bytesFileYaml=buffer_data,
                                                                 file_name="PV_data",
                                                                 label="💾 Descargar **:blue[archivo de datos]** del panel fotovoltaico **YAML**")
                    
                    
                    buttonDowmload1 = general.yamlDownloadButton(bytesFileYaml=buffer_params,
                                                                 file_name="PV_params",
                                                                 label="💾 Descargar **:blue[archivo de parámetros]** del panel fotovoltaico **YAML**")
                    