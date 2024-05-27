import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pvlib, folium
from streamlit_folium import st_folium, folium_static

from functions import functions, functions_st, storage


def page_apps_main(title):

    st.header(title, divider="red")

    with st.expander("📝 Obtención de parámetros Baterías de litio"):
        tab1, tab2 = st.tabs(["Marco teórico", "Entrada de datos"])

        with tab1:
            st.latex(r"""V_{bat}(t)=V_{0}-Ri-K\frac{mQ(i)}{mQ(i)-it}+Ae^{-Bit}""")

        with tab2:
            with st.form("app_2_option_1"):

                st.image("images\\app2_1_img1.png")

                with st.container(border=True):
                    st.markdown("**:blue[{0}:]**".format("Párametros de la batería"))

                    col1, col2, col3 = st.columns(3)

                    Qnom = col1.number_input("Carga nominal (Ah):", min_value=0.0, max_value=2000.0, step=None, format="%.1f", value=1090.0)
                    Vnom = col2.number_input("Voltaje nominal (V):", min_value=0.0, max_value=100.0, step=None, format="%.3f", value=3.2)
                    Inom = col3.number_input("Corriente nominal (A):", min_value=0.0, max_value=1000.0, step=None, format="%.1f", value=100.0)
                
                with st.container(border=True):
                    st.markdown("**:blue[{0}:]**".format("Puntos gráfica i1"))
                    i1 = st.number_input("**i1 (A):**", min_value=0, max_value=1000, step=None, value=100)

                    col1, col2 = st.columns(2)

                    V1 = col1.number_input("Vfull (V):", min_value=0.0, max_value=100.0, step=None, format="%.3f", value=3.40)
                    V2 = col1.number_input("V2 (V):", min_value=0.0, max_value=100.0, step=None, format="%.3f", value=3.35)
                    V3 = col1.number_input("V3 (V):", min_value=0.0, max_value=100.0, step=None, format="%.3f", value=3.33)
                    V4 = col1.number_input("V4 (V):", min_value=0.0, max_value=100.0, step=None, format="%.3f", value=3.20)
                    V5 = col1.number_input("V5 (V):", min_value=0.0, max_value=100.0, step=None, format="%.3f", value=0.00)

                    Q1 = col2.number_input("Q1 (Ah):", min_value=0.0, max_value=1100.0, step=None, format="%.3f", value=0.00, disabled=True)
                    Q2 = col2.number_input("Q2 (Ah):", min_value=0.0, max_value=1100.0, step=None, format="%.3f", value=16.176)
                    Q3 = col2.number_input("Q3 (Ah):", min_value=0.0, max_value=1100.0, step=None, format="%.3f", value=32.352)
                    Q4 = col2.number_input("Q4 (Ah):", min_value=0.0, max_value=1100.0, step=None, format="%.3f", value=880.0)
                    Q5 = col2.number_input("Q5=Qi1 (Ah):", min_value=0.0, max_value=1100.0, step=None, format="%.3f", value=1086.8)

                with st.container(border=True):
                    st.markdown("**:blue[{0}:]**".format("Puntos gráfica i2"))
                    i2 = st.number_input("**i1 (A):**", min_value=0, max_value=1000, step=None, value=300)

                    col1, col2 = st.columns(2)

                    V6 = col1.number_input("V6 (V):", min_value=0.0, max_value=100.0, step=None, format="%.3f", value=3.226)
                    Q6 = col2.number_input("Q6 (Ah):", min_value=0.0, max_value=1100.0, step=None, format="%.3f", value=550.0)
                    Qi2 = col2.number_input("Qi2 (Ah):", min_value=0.0, max_value=1100.0, step=None, format="%.3f", value=1072.5)


                submitted = st.form_submit_button("Aceptar")
                
                if submitted:

                    params_nominal = {
                        "Qnom": Qnom,
                        "Vnom": Vnom,
                        "Inom": Inom
                    }
                    
                    battery_points = {
                         "P1": (Q1, V1),
                         "P2": (Q2, V2),
                         "P3": (Q3, V3),
                         "P4": (Q4, V4),
                         "P5": (Q5, V5),
                         "P6_i2": (Q6, V6),
                         "Qi": (Q5, Qi2),
                         "i": (i1, i2)
                    }

                    parameters = functions.get_battery_parameters(points=battery_points)

                    sub_tab1, sub_tab2 = st.tabs(["Parametros batería", "Curva V-Q"])

                    with sub_tab1:
                        functions_st.get_print_params(params=parameters,
                                                      params_label=list(parameters.keys()))
                        
                    with sub_tab2:
                        time_vector = functions.get_battery_graph(parameters, params_nominal, battery_points,
                                                                  SOC_0=1,
                                                                  it_0=0,
                                                                  time=5, 
                                                                  current=params_nominal["Inom"])

                        st.text(time_vector)
                    

   


            

    return