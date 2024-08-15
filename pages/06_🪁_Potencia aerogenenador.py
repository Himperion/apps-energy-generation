import streamlit as st
import pandas as pd
from io import BytesIO
from funtions import funtions, funtions_st

#%% funtions

@st.cache_data
def to_excel(df: pd.DataFrame):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    
    processed_data = output.getvalue()
        
    return processed_data

#%% global variables

parameters = {
    "D" : "Diámetro (m)",
    "rho" : "Densidad del aire (Kg/m³)",
    "V_in" : "Velocidad de arranque (m/s)",
    "V_nom" : "Velocidad nominal (m/s)",
    "V_max" : "Velocidad máxima (m/s)",
    "P_nom" : "Pontencia nominal (W)"
}

items_options_columns_df = {
    "Vwind" : ["Vwind(m/s)", "Vwind 10msnm(m/s)", "Vwind 50msnm(m/s)"]
}

template = {
    "directory": "files",
    "name_file": "[Plantilla] - Potencia aerogenerador",
    "format_file": "xlsx",
    "description": "Velocidad del viento"
}

#%% main

st.markdown("# 🪁 Potencia aerogenerador")

tab1, tab2 = st.tabs(["📑 Marco teórico", "📝 Entrada de datos"])  

with tab1:
    st.text("Ajaaaaaaaaaaaaa")

with tab2:
    with st.container(border=True):
        st.markdown("**:blue[{0}:]**".format("Parámetros del aerogenerador"))
        D = st.number_input(parameters["D"], min_value=0.0, max_value=80.0, step=None, format="%.3f", value=1.75)
        V_in = st.number_input(parameters["V_in"], min_value=2.0, max_value=6.0, step=None, format="%.3f", value=3.5)
        V_nom = st.number_input(parameters["V_nom"], min_value=9.0, max_value=16.0, step=None, format="%.3f", value=12.0)
        V_max = st.number_input(parameters["V_max"], min_value=30.0, max_value=80.0, step=None, format="%.3f", value=60.0)
        P_nom = st.number_input(parameters["P_nom"], min_value=400.0, max_value=550e3, step=None, format="%.3f", value=800.0)

    with st.container(border=True):
        st.markdown("**:blue[{0}:]**".format("Datos del sitio"))
        rho = st.number_input(parameters["rho"], min_value=0.4, max_value=1.4, step=None, format="%.3f", value=1.225)

        archive_Vwind = st.file_uploader("Cargar archivo **Velocidad del viento** (m/s)", type={"xlsx"})
            
        funtions_st.get_download_button(**template)
       
    app_6_submitted = st.button("Aceptar")

    if app_6_submitted:        
        if archive_Vwind is not None:
            df_input = pd.read_excel(archive_Vwind)
            
            df_turbine, check, columns_options_sel = funtions.check_dataframe_input(dataframe=df_input,
                                                                                    options=items_options_columns_df)

            if check:
                params_turbine = {
                    "D" : D, 
                    "rho" : rho, 
                    "V_in" : V_in, 
                    "V_nom" : V_nom, 
                    "V_max" : V_max, 
                    "P_nom" : P_nom
                    }
                
                df_powerTurbine = funtions.get_dataframe_power_wind_turbine(params=params_turbine,
                                                                            dataframe=df_turbine,
                                                                            column=columns_options_sel)
                
                df_values = funtions.get_values_curve_turbine(params=params_turbine)
                
                sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📋 Resultados", "📈 Curva de potencia", "📉 Curva de eficiencia"])

                with sub_tab1:
                    st.dataframe(df_powerTurbine)
                    
                    excel = to_excel(df_powerTurbine)
                    
                    st.download_button(label="📄 Descargar muestras",
                                       data=excel,
                                       file_name=funtions.name_file_head(name="powerTurbine.xlsx"),
                                       mime="xlsx")

                with sub_tab2:
                    column_xy = ("V_wind", "P_turbine")
                    label_xy = ("Velocidad de viento (m/s)", "Potencia del aerogenerador (W)")
                    label_title = "Curva aerogenerador"

                    funtions_st.curveTurbine(df_values, column_xy, label_xy, label_title, "blue")

                with sub_tab3:
                    column_xy = ("V_wind", "n_turbine")
                    label_xy = ("Velocidad de viento (m/s)", "Eficiencia")
                    label_title = "Curva de eficiencia"

                    funtions_st.curveTurbine(df_values, column_xy, label_xy, label_title, "red")
        else:
            st.warning("Falta cargar archivo **Velocidad del viento** (m/s)", icon="⚠️")
            
        