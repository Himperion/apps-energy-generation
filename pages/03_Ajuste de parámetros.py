import streamlit as st
import numpy as np
import yaml
from funtions import funtions, funtions_st

#%% global variables

with open('values_Egap.yaml', 'r') as archivo:
    dict_value_Egap = yaml.safe_load(archivo)

text = {
    "subheader_1" : "Los párametros de **Single diode** se calculan para un módulo fotovoltaico en condiciones **STC** de operación. Sí se desea hacer un análisis del panel fotovoltaico en condiciones distintas al **STC** es necesario aplicar ajustes a los parámetros para que reflejen un comportamiento acorde a los cambios en la operación.",
    "subheader_2" : "Este aplicativo web para efectuar la corrección de parámetros del módulo se logra mediante la librería **PVLIB** de Python que permite simular sistemas de energía fotovoltaicos." 
}

label_params_1 = "**Iph:** Corriente fotoinducida (A):"
label_params_2 = "**Isat:** Corriente de saturación del diodo (A):"
label_params_3 = "**Rs:** Resistencia serie (Ohm):"
label_params_4 = "**Rp:** Resistencia en paralelo (Ohm):"
label_params_5 = "**nNsVth:** Producto del factor de idealida, el número de celdas en serie y el voltaje térmico en condiciones STC:"
label_params_6 = "**Gef:** Irradciiana efectiva (W/m^2):"
label_params_7 = "**Toper:** Temperatura de operación del módulo (°C):"
label_params_8 = "**Módulos conectados en serie:**"
label_params_9 = "**Ramas en paralelo:**"

#%% main

st.markdown("# 🔩 Ajuste de parámetros")

tab1, tab2 = st.tabs(["Marco teórico", "Entrada de datos"])  

with tab1:   
    st.markdown(text["subheader_1"])

    col1, col2, col3 = st.columns( [0.25, 0.5, 0.25])

    with col1:
        st.write("")
    with col2:
        st.image("images\\app2_img1.png")
    with col3:
        st.write("")

    st.markdown(text["subheader_2"])

with tab2:      
    with st.form("app_1_option_3", border=False):

        with st.container(border=True):
            st.markdown("**:blue[{0}:]**".format("Parámetros del módulo"))
            Alfa = st.number_input("**Alfa:** Coeficiente de temperatura de la Isc (%/°C)", min_value=0.0, max_value=1.0, step=0.0001, format="%.4f", value=0.055)
            Iph = st.number_input(label_params_1, min_value=0.0, max_value=200.0, step=None, format="%.4f", value=8.09)
            Isat = st.number_input(label_params_2, min_value=0.0, max_value=200.0, step=None, format="%.17e", value=8.60373454419776e-10)
            Rs = st.number_input(label_params_3, min_value=0.0, max_value=1.0, step=None, format="%.6f", value=0.458303)
            Rp = st.number_input(label_params_4, min_value=0.0, max_value=800.0, step=None, format="%.6f", value=171.288822)
            nNsVth = st.number_input(label_params_5, min_value=0.0, max_value=10.0, step=None, format="%.6f", value=1.916018)
            cell_type = st.selectbox("**Tecnologia del módulo:**", options=list(dict_value_Egap.keys()))

        with st.container(border=True):
            st.markdown("**:blue[{0}:]**".format("Condiciones de operación del módulo"))
            col1, col2 = st.columns([0.50, 0.50])
            Geff = col1.number_input(label_params_6, min_value=0, max_value=1000, step=None, value=1000)
            Toper = col2.number_input(label_params_7, min_value=0, max_value=100, step=None, value=25)

        with st.container(border=True):
            st.markdown("**:blue[{0}:]**".format("Conexión de los módulos"))
            col1, col2 = st.columns([0.50, 0.50])
            array_serie = col1.number_input(label_params_8, min_value=1, max_value=100, step=None, value=1)
            array_parallel = col2.number_input(label_params_9, min_value=1, max_value=100, step=None, value=1)

        app_1_option_3_submitted = st.form_submit_button("Aceptar")

        if app_1_option_3_submitted:
            STD_params = {
                 'photocurrent': Iph,
                 'saturation_current': Isat,
                 'resistance_series': Rs,
                 'resistance_shunt': Rp,
                 'nNsVth': nNsVth
                 }
                    
            conditions, corr_param_pv = funtions.get_calcparams_desoto(Geff, Toper, Alfa, STD_params, cell_type, dict_value_Egap, array_serie, array_parallel)
            curve_info, v, i, p = funtions.get_values_curve_I_V_version2(SDE_params=corr_param_pv)

            sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Parametros Ajustados", "Curva I-V", "Curva P-V"])
            
            with sub_tab1:
                funtions_st.get_print_params(params=corr_param_pv, 
                                             params_label=["Iph", "Isat", "Rs", "Rp", "nNsVt"])

                col1, col2 = st.columns(2)
                col1.markdown("**:red[{0}:]**".format("Isc"))
                col1.markdown("**:red[{0}:]**".format("Voc"))
                col1.markdown("**:red[{0}:]**".format("Impp"))
                col1.markdown("**:red[{0}:]**".format("Vmpp"))
                col1.markdown("**:red[{0}:]**".format("Pmpp"))

                col2.markdown(np.round(curve_info.loc[1, "i_sc"], decimals=4))
                col2.markdown(np.round(curve_info.loc[1, "v_oc"], decimals=4))
                col2.markdown(np.round(curve_info.loc[1, "i_mp"], decimals=4))
                col2.markdown(np.round(curve_info.loc[1, "v_mp"], decimals=4))
                col2.markdown(np.round(curve_info.loc[1, "p_mp"], decimals=4))
            
            with sub_tab2:
                funtions_st.curveMulti_x_y(conditions, v, i, curve_info, option="current")
                    
            with sub_tab3:
                funtions_st.curveMulti_x_y(conditions, v, p, curve_info, option="power")
            

    