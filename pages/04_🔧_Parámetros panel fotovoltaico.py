import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yaml
from scipy.special import lambertw
from scipy.optimize import root_scalar, fsolve
from funtions import funtions, funtions_st

#%% Funtions

#%% global variables

with open("files/[PV] - values_Egap.yaml", 'r') as archivo:
    dict_value_Egap = yaml.safe_load(archivo)

with open("files//[PV] - params.yaml", 'r') as archivo:
    dict_params = yaml.safe_load(archivo)

with open("files//[PV] - dict_replace.yaml", 'r') as archivo:
    dict_rename = yaml.safe_load(archivo)

text = {  
     "subheader_1" : "El modelo circuital de los sistemas fotovoltaicos facilita la predicción de variables eléctricas como la tensión, corriente y potencia en diversas condiciones de operación. Esto es crucial para realizar un dimensionamiento completo y preciso del sistema.",
     "subheader_2" : "El modelo **Single diode** se fundamenta en los principios de los dispositivos semiconductores y proporciona una representación de las propiedades eléctricas de un módulo fotovoltaico.",
     "subheader_3" : "La expresión de la corriente del módulo en el circuito equivalente se convierte en la ecuación fundamental del modelo que posibilita una reconstrucción aproximada de la curva de corriente-voltaje (I-V) del panel fotovoltaico."
}

#%% main

st.markdown("# 🔧 Obtención de parámetros STC")

tab1, tab2 = st.tabs(["📑 Marco teórico", "📝 Entrada de datos"])

with tab1:
    st.markdown(text["subheader_1"])
    st.markdown(text["subheader_2"])
        
    col1, col2, col3 = st.columns( [0.25, 0.5, 0.25])

    with col1:
        st.write("")
    with col2:
        st.image("images//app1_img1.png")
    with col3:
        st.write("")

    st.markdown(text["subheader_3"])
    st.latex(r"""I=I_{ph}-I_{d}-I_{R_{p}}=I_{ph}-I_{sat}\cdot \left ( e\tfrac{V+I\cdot R_{s}}{N_{s}nv_{t}} -1\right )-\frac{V+I\cdot R_{s}}{R_{p}}""")

    st.markdown(funtions.get_label_params(dict_param=dict_params["Iph"]))
    st.markdown(funtions.get_label_params(dict_param=dict_params["n"]))
    st.markdown(funtions.get_label_params(dict_param=dict_params["Vt"]))
    st.markdown(funtions.get_label_params(dict_param=dict_params["Ns"]))
    st.markdown(funtions.get_label_params(dict_param=dict_params["Isat"]))
    st.markdown(funtions.get_label_params(dict_param=dict_params["Rs"]))
    st.markdown(funtions.get_label_params(dict_param=dict_params["Rp"]))

with tab2:
    with st.container(border=True):
        st.markdown("**:blue[{0}:]**".format("Características eléctricas"))
        col1, col2 = st.columns(2)
        with col1:
            Vmpp = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["Vmpp"]),
                                                       variable=dict_params["Vmpp"]["number_input"])
            
            Voc = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["Voc"]),
                                                      variable=dict_params["Voc"]["number_input"])
            
        with col2:
            Impp = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["Impp"]),
                                                       variable=dict_params["Impp"]["number_input"])
            
            Isc = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["Isc"]),
                                                      variable=dict_params["Isc"]["number_input"])
            
    with st.container(border=True):
        st.markdown("**:blue[{0}:]**".format("Características de temperatura"))
            
        NOCT = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["NOCT"]),
                                                   variable=dict_params["NOCT"]["number_input"])
            
        Alfa = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["Alfa"]),
                                                   variable=dict_params["Alfa"]["number_input"])
            
        Beta = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["Beta"]),
                                                   variable=dict_params["Beta"]["number_input"])
            
        Delta = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["Delta"]),
                                                    variable=dict_params["Delta"]["number_input"])
        
    with st.container(border=True):
        st.markdown("**:blue[{0}:]**".format("Características mecánicas"))
            
        cell_type = st.selectbox("Tecnologia", options=list(dict_value_Egap.keys()), index=6)

        Ns = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["Ns"]),
                                                 variable=dict_params["Ns"]["number_input"])
        
    app_5_submitted = st.button("Aceptar")

    if app_5_submitted:
        data_pv, param_pv, SDE_params = funtions.get_STD_params(Voc, Isc, Vmpp, Impp, Alfa, Beta, Delta, NOCT, Ns, cell_type, dict_value_Egap)

        df_curve_info = pd.concat([pd.DataFrame([param_pv]), pd.DataFrame([data_pv])], axis=1)
        df_curve_info["Pmax"] = df_curve_info["Vmpp"]*df_curve_info["Impp"]

        v, i, p = funtions.get_values_curve_I_V(df_curve_info, SDE_params)

        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📋 Parámetros STC", "📈 Curva I-V", "📉 Curva P-V"])

        with sub_tab1:

            head_column = ["", "Condiciones STC"]
            labels_output = ["Iph", "Isat", "Rs", "Rp", "nNsVt", "n", "Vt", "C"]
            
            funtions_st.get_print_params_dataframe(df_curve_info, labels_output, dict_params, head_column)

        with sub_tab2:
            
            points = {
                "Voc": (df_curve_info.loc[0, "Voc"], 0),
                "Isc": (0, df_curve_info.loc[0, "Isc"]),
                "MPP": (df_curve_info.loc[0, "Vmpp"], df_curve_info.loc[0, "Impp"]),
                "Vmpp": (df_curve_info.loc[0, "Vmpp"], 0),
                "Impp": (0, df_curve_info.loc[0, "Impp"])
            }

            lines = [
                ("MPP", "Vmpp"),
                ("Impp", "MPP")
            ]

            title = "Corriente-Voltaje (I-V)"
            xlabel = "Voltaje (V)"
            ylabel = "Corriente (A)"

            funtions_st.curve_x_y(v, i, points, lines, title, xlabel, ylabel)

        with sub_tab3:

            points = {
                "Vmpp": (df_curve_info.loc[0, "Vmpp"], 0),
                "Pmax": (0, df_curve_info.loc[0, "Pmax"]),
                "MPP": (df_curve_info.loc[0, "Vmpp"], df_curve_info.loc[0, "Pmax"]),
            }

            lines = [
                ("MPP", "Vmpp"),
                ("Pmax", "MPP")
            ]

            title = "Potencia-Voltaje (P-V)"
            xlabel = "Voltaje (V)"
            ylabel = "Potencia (W)"

            funtions_st.curve_x_y(v, p, points, lines, title, xlabel, ylabel)
