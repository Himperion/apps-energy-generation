import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium, io
from streamlit_folium import st_folium, folium_static

from functions import functions, functions_st

text_subheader1 = "El modelo circuital de los sistemas fotovoltaicos facilita la predicción de variables eléctricas como la tensión, corriente y potencia en diversas condiciones de operación. Esto es crucial para realizar un dimensionamiento completo y preciso del sistema."
text_subheader2 = "El modelo **Single diode** se fundamenta en los principios de los dispositivos semiconductores y proporciona una representación de las propiedades eléctricas de un módulo fotovoltaico."
text_subheader3 = "La expresión de la corriente del módulo en el circuito equivalente se convierte en la ecuación fundamental del modelo que posibilita una reconstrucción aproximada de la curva de corriente-voltaje (I-V) del panel fotovoltaico."

dict_value_Egap = {
    'monoSi (Silicio monocristalino)': 1.124,
    'multiSi (Silicio multicristalino)': 1.124,
    'polySi (Silicio policristalino)': 1.124,
    'CIS (Sulfuro de Cobre-Indio)': 1.04,
    'CIGS (Seleniuro de Cobre-Indio-Galio)': 1.08,
    'CdTe (Telururo de Cadmio)': 1.5,
    'amorphous (Silicio amorfo)': 1.7
}

dict_value_Egap = {
    'monoSi (Silicio monocristalino)': {'EgRef': 1.121, 'dEgdT': -0.0002677},
    'multiSi (Silicio multicristalino)': {'EgRef': 1.121, 'dEgdT': -0.0002677},
    'polySi (Silicio policristalino)': {'EgRef': 1.121, 'dEgdT': -0.0002677},
    'CIS (Sulfuro de Cobre-Indio)': {'EgRef': 1.010, 'dEgdT': -0.00011},
    'CIGS (Seleniuro de Cobre-Indio-Galio)': {'EgRef': 1.15, 'dEgdT': None},
    'CdTe (Telururo de Cadmio)':  {'EgRef': 1.475, 'dEgdT': -0.0003},
    'amorphous (Silicio amorfo)': {'EgRef': 1.7, 'dEgdT': None}
}

dir_image_1 = file_name_database = "app/apps/images/model_single_diode.png"

options_photovoltaic = ["☀️ Obtención de datos de irradiancia",
                        "📝 Obtención de parámetros STC",
                        "🔩 Ajuste de parámetros"]

def page_apps_main(title):

    st.header(title, divider="red")
    
    with st.expander(options_photovoltaic[0]):
        with st.form("app_1_option_1"):
            data_dates = ""

            col1, col2 = st.columns( [0.5, 0.5])

            lat_input = col1.number_input('Ingrese la latitud:', min_value=-90.0, max_value=90.0, step=0.000001, format="%.6f", value=7.142056)
            lon_input = col2.number_input('Ingrese la longitud:', min_value=-180.0, max_value=180.0, step=0.000001, format="%.6f", value=-73.121231)

            date_ini = col1.date_input("Fecha de inicio:")
            date_end = col2.date_input("Fecha Final:")

            m = folium.Map(location=[lat_input, lon_input], zoom_start=17)

            folium.Marker([lat_input, lon_input],
                          popup=f'Latitud: {lat_input}, Longitud: {lon_input}',
                          draggable=False).add_to(m)

            st_data = st_folium(m, width=725, height=400)

            app_1_option_1_submitted = st.form_submit_button("Aceptar")

            if app_1_option_1_submitted:
                cal_rows = functions.cal_rows(date_ini, date_end, steps=60)
                
                if cal_rows > 0:
                    data = functions.get_dataframe_NASA_POWER(latitude=lat_input,
                                                              longitude=lon_input,
                                                              start=date_ini,
                                                              end=date_end,
                                                              parameters=["ALLSKY_SFC_SW_DWN"])
                    
                    data_dates = functions.add_column_dates(dataframe=data,
                                                            date_ini=date_ini,
                                                            rows=cal_rows,
                                                            steps=60)
                    
                    with st.container(border=True):
                        functions_st.view_dataframe_information(data_dates)

                    st.session_state.app_1_option_1_var_flagAccept = True

        if st.session_state.app_1_option_1_var_flagAccept and isinstance(data_dates, pd.DataFrame):
            
            
            excel_bytes_io = io.BytesIO()
            data_dates.to_excel(excel_bytes_io, index=False)
            excel_bytes_io.seek(0)

            st.download_button(label="Descargar archivo",
                               data= excel_bytes_io.read(),
                               file_name='large_df.xlsx')
            
                         
    with st.expander(options_photovoltaic[1]):
        tab1, tab2 = st.tabs(["Marco teórico", "Entrada de datos"])

        with tab1:
            st.markdown(text_subheader1)
            st.markdown(text_subheader2)
        
            col1, col2, col3 = st.columns( [0.25, 0.5, 0.25])

            with col1:
                st.write("")
            with col2:
                st.image("images\\app1_2_img1.png")
            with col3:
                st.write("")

            st.markdown(text_subheader3)
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
                    data_pv, param_pv, SDE_params = functions.get_STD_params(Voc, Isc, Vmpp, Impp, Alfa, Beta, Delta, NOCT, Ns, cell_type, dict_value_Egap)

                    v, i, p = functions.get_values_curve_I_V(SDE_params)
                    data_pv['Pmax'] = np.max(p)

                    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Parametros STC", "Curva I-V", "Curva P-V"])

                    with sub_tab1:
                        functions_st.get_print_params(params=SDE_params, 
                                                      params_label=["Iph", "Isat", "Rs", "Rp", "nNsVt"])
                            
                    with sub_tab2:
                        p_x = [data_pv['Voc'], 0, data_pv['Vmpp'], 0, data_pv['Vmpp']]
                        p_y = [0, data_pv['Isc'], data_pv['Impp'], data_pv['Impp'], 0]
                        p_label = ['Voc', 'Isc', 'MPP', 'Imp', 'Vmp']
                        p_line = [(4, 2), (3, 2)]
                        title = "Corriente-Voltaje (I-V)"
                        xlabe = "Voltaje (V)"
                        ylabe = "Corriente (A)"

                        functions_st.curve_x_y(v, i, p_x, p_y, p_label, p_line, title, xlabe, ylabe)

                    with sub_tab3:
                        p_x = [0, data_pv['Vmpp'], data_pv['Vmpp']]
                        p_y = [data_pv['Pmax'], 0, data_pv['Pmax']]
                        p_label = ['Pmp', 'Vmpp', 'Pmax']
                        p_line = [(1, 2), (0, 2)]
                        title = "Potencia-Voltaje (P-V)"
                        xlabe = "Voltaje (V)"
                        ylabe = "Potencia (W)"

                        functions_st.curve_x_y(v, p, p_x, p_y, p_label, p_line, title, xlabe, ylabe)

    with st.expander(options_photovoltaic[2]):
        tab1, tab2 = st.tabs(["Marco teórico", "Entrada de datos"])  

        with tab2:      
            label_params_1 = "**Iph:** Corriente fotoinducida (A):"
            label_params_2 = "**Isat:** Corriente de saturación del diodo (A):"
            label_params_3 = "**Rs:** Resistencia serie (Ohm):"
            label_params_4 = "**Rp:** Resistencia en paralelo (Ohm):"
            label_params_5 = "**nNsVth:** Producto del factor de idealida, el número de celdas en serie y el voltaje térmico en condiciones STC:"
            label_params_6 = "**Gef:** Irradiancia efectiva (W/m^2):"
            label_params_7 = "**Toper:** Temperatura de operación del módulo (°C):"
            label_params_8 = "**Módulos conectados en serie:**"
            label_params_9 = "**Ramas en paralelo:**"

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
                    STD_params = {'photocurrent': Iph,
                                  'saturation_current': Isat,
                                  'resistance_series': Rs,
                                  'resistance_shunt': Rp,
                                  'nNsVth': nNsVth
                                  }
                    
                    conditions, corr_param_pv = functions.get_calcparams_desoto(Geff, Toper, Alfa, STD_params, cell_type, dict_value_Egap, array_serie, array_parallel)
                    curve_info, v, i, p = functions.get_values_curve_I_V_version2(SDE_params=corr_param_pv)

                    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Parametros Ajustados", "Curva I-V", "Curva P-V"])

                    with sub_tab1:
                        functions_st.get_print_params(params=corr_param_pv, 
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
                        functions_st.curveMulti_x_y(conditions, v, i, curve_info, option="current")
                    
                    with sub_tab3:
                        functions_st.curveMulti_x_y(conditions, v, p, curve_info, option="power")
                        
    return
