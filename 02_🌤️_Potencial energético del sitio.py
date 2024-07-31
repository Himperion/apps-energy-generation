# -*- coding: utf-8 -*-

import folium, io, warnings
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium, folium_static
from pynasapower.get_data import query_power
from pynasapower.geometry import point, bbox
from datetime import datetime
from funtions import funtions, funtions_st

warnings.filterwarnings("ignore")

#%% main

dict_parameters = {
    "Irradiancia (W/m^2)" : ("ALLSKY_SFC_SW_DWN", "Gin(W/m²)"),
    "Velocidad del viento a 10 msnm (m/s)" : ("WS10M", "Vwind 10msnm(m/s)"),
    "Velocidad del viento a 50 msnm (m/s)" : ("WS50M", "Vwind 50msnm(m/s)"),
    "Temperatura ambiente a 2 msnm (°C)" : ("T2M", "Tamb 2msnm(°C)")
    }

options_multiselect = list(dict_parameters.keys())

st.markdown("# 🌤️ Datos climáticos y potencial energético del sitio")

with st.form("app_1"):
    data_dates = ""

    col1, col2 = st.columns( [0.5, 0.5])

    lat_input = col1.number_input('Ingrese la latitud:', min_value=-90.0, max_value=90.0, step=0.000001, format="%.6f", value=7.142056)
    lon_input = col2.number_input('Ingrese la longitud:', min_value=-180.0, max_value=180.0, step=0.000001, format="%.6f", value=-73.121231)

    date_ini = col1.date_input("Fecha de Inicio:")
    date_end = col2.date_input("Fecha Final:")

    options = st.multiselect("Seleccione los datos a cargar: ",
                             options=options_multiselect,
                             placeholder="Seleccione una opción")

    m = folium.Map(location=[lat_input, lon_input], zoom_start=17)

    folium.Marker([lat_input, lon_input],
                  popup=f'Latitud: {lat_input}, Longitud: {lon_input}',
                  draggable=False).add_to(m)

    st_data = st_folium(m, width=725, height=400)

    app_1_submitted = st.form_submit_button("Aceptar")

    if app_1_submitted:
        cal_rows = funtions.cal_rows(date_ini, date_end, steps=60)

        if len(options) != 0:
            if cal_rows > 0:
                parameters = funtions.get_parameters_NASA_POWER(options)

                data = funtions.get_dataframe_NASA_POWER(latitude=lat_input,
                                                         longitude=lon_input,
                                                         start=date_ini,
                                                         end=date_end,
                                                         parameters=parameters)
                        
                data_dates = funtions.add_column_dates(dataframe=data,
                                                       date_ini=date_ini,
                                                       rows=cal_rows,
                                                       steps=60)
                
                with st.container(border=True):
                    funtions_st.view_dataframe_information(data_dates)

                excel_bytes_io = io.BytesIO()
                data_dates.to_excel(excel_bytes_io, index=False)
                excel_bytes_io.seek(0)

                st.download_button(label="Descargar archivo",
                                   data= excel_bytes_io.read(),
                                   file_name=funtions.name_file_head("ALLSKY_SFC_SW_DWN.xlsx"))
            else:
                if cal_rows == 0:
                    st.warning("La {0} debe ser diferente a la {1}".format(":blue[Fecha de Inicio]", ":blue[Fecha final]"), icon="⚠️")
                if cal_rows < 0:
                    st.warning("La {0} debe ser menor a la {1}".format(":blue[Fecha de Inicio]", ":blue[Fecha final]"), icon="⚠️")
        else:
            st.warning("Ingrese por lo menos una opción en {0}".format(":blue[Seleccione los datos a cargar]"), icon="⚠️")
            
