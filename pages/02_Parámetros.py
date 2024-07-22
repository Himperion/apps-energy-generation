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

with open('values_Egap.yaml', 'r') as archivo:
    dict_value_Egap = yaml.safe_load(archivo)

text = {  
     "subheader_1" : "El modelo circuital de los sistemas fotovoltaicos facilita la predicción de variables eléctricas como la tensión, corriente y potencia en diversas condiciones de operación. Esto es crucial para realizar un dimensionamiento completo y preciso del sistema.",
     "subheader_2" : "El modelo **Single diode** se fundamenta en los principios de los dispositivos semiconductores y proporciona una representación de las propiedades eléctricas de un módulo fotovoltaico.",
     "subheader_3" : "La expresión de la corriente del módulo en el circuito equivalente se convierte en la ecuación fundamental del modelo que posibilita una reconstrucción aproximada de la curva de corriente-voltaje (I-V) del panel fotovoltaico."
}

#%% main

st.markdown("# 📝 Obtención de parámetros STC")

tab1, tab2 = st.tabs(["Marco teórico", "Entrada de datos"])

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

    st.markdown("**Iph:** Corriente fotoinducida (A)")
    st.markdown("**n:** Factor de idealidad del diodo")
    st.markdown("**Vt:** Voltaje térmico (V)")
    st.markdown("**Ns:** Número de celdas en serie")
    st.markdown("**Isat:** Corriente de saturación del diodo (A)")
    st.markdown("**Rs:** Resistencia serie (Ohm)")
    st.markdown("**Rp:** Resistencia en paralelo (Ohm)")

with tab2:
    with st.form("app_1_option_2"):
                
        col1, col2 = st.columns(2)
        with col1:
            Vmpp = st.number_input("**Vmpp**: Voltaje de punto de máxima potencia (V)", min_value=0.0, max_value=200.0, step=None, format="%.3f", value=34.8)
            Impp = st.number_input("**Impp**: Corriente de punto de máxima potencia (A)", min_value=0.0, max_value=200.0, step=None, format="%.3f", value=7.47)
            Voc = st.number_input("**Voc**: Voltaje de circuito abierto (V)", min_value=0.0, max_value=200.0, step=0.1, format="%.3f", value=44.0)
            Isc = st.number_input("**Isc**: Corriente de cortocircuito (A)", min_value=0.0, max_value=200.0, step=None, format="%.3f", value=8.09)
            Alfa = st.number_input("Coeficiente de temperatura de la Isc (%/°C)", min_value=0.0, max_value=1.0, step=0.0001, format="%.4f", value=0.055)
            Beta = st.number_input("Coeficiente de temperatura de la Voc (%/°C)", min_value=-0.9999, max_value=0.0, step=0.0001, format="%.4f", value=-0.34)
            Delta = st.number_input("Coeficiente de temperatura de la Pmax (%/°C)", min_value=-0.9999, max_value=0.0, step=0.0001, format="%.4f", value=-0.47)
        with col2:
            cell_type = st.selectbox("Tecnologia", options=list(dict_value_Egap.keys()))
            Ns = st.number_input("**Ns**: Número de celdas en serie", min_value=1, max_value=200, step=None, value=72)
            NOCT = st.number_input("**NOCT**: Temperatura de operación nominal de la celda (°C)", min_value=1, max_value=90, step=None, value=45)

        app_1_option_2_submitted = st.form_submit_button("Aceptar")
                
        if app_1_option_2_submitted:
            data_pv, param_pv, SDE_params = funtions.get_STD_params(Voc, Isc, Vmpp, Impp, Alfa, Beta, Delta, NOCT, Ns, cell_type, dict_value_Egap)

            v, i, p = funtions.get_values_curve_I_V(SDE_params)
            data_pv['Pmax'] = np.max(p)

            sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Parametros STC", "Curva I-V", "Curva P-V"])

            with sub_tab1:
                funtions_st.get_print_params(params=SDE_params, 
                                             params_label=["Iph", "Isat", "Rs", "Rp", "nNsVt"])
            with sub_tab2:
                        p_x = [data_pv['Voc'], 0, data_pv['Vmpp'], 0, data_pv['Vmpp']]
                        p_y = [0, data_pv['Isc'], data_pv['Impp'], data_pv['Impp'], 0]
                        p_label = ['Voc', 'Isc', 'MPP', 'Imp', 'Vmp']
                        p_line = [(4, 2), (3, 2)]
                        title = "Corriente-Voltaje (I-V)"
                        xlabe = "Voltaje (V)"
                        ylabe = "Corriente (A)"

                        funtions_st.curve_x_y(v, i, p_x, p_y, p_label, p_line, title, xlabe, ylabe)
            
            with sub_tab3:
                p_x = [0, data_pv['Vmpp'], data_pv['Vmpp']]
                p_y = [data_pv['Pmax'], 0, data_pv['Pmax']]
                p_label = ['Pmp', 'Vmpp', 'Pmax']
                p_line = [(1, 2), (0, 2)]
                title = "Potencia-Voltaje (P-V)"
                xlabe = "Voltaje (V)"
                ylabe = "Potencia (W)"

                funtions_st.curve_x_y(v, p, p_x, p_y, p_label, p_line, title, xlabe, ylabe)

