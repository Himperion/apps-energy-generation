import streamlit as st
import pandas as pd
import datetime as dt
import yaml
from io import BytesIO

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode

#%% funtions general

def name_file_head(name: str) -> str:
    now = dt.datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def changeUnitsK(K, Base):

    K_out = (Base*K)/100
    
    return K_out

def get_filtering_options_pv(dataframe):

    dict_data_filter_pv = {
        'min_p_max': dataframe["p_max (W)"].min(),
        'max_p_max': dataframe['p_max (W)'].max(),
        'min_v_oc': dataframe['v_oc (V)'].min(),
        'max_v_oc': dataframe['v_oc (V)'].max(),
        'min_i_sc': dataframe['i_sc (A)'].min(),
        'max_i_sc': dataframe['i_sc (A)'].max(),
        'list_celltype': list(dataframe['celltype'].unique()),
        'list_manufacturer': list(dataframe['manufacturer'].unique())
    }

    return dict_data_filter_pv

def get_dict_PV_data(selected_row: pd.DataFrame) -> dict:

    PV_data = {
        "celltype": selected_row.loc[0, "celltype"],
        "v_mp": selected_row.loc[0, "v_mp (V)"],
        "i_mp": selected_row.loc[0, "i_mp (A)"],
        "v_oc": selected_row.loc[0, "v_oc (V)"],
        "i_sc": selected_row.loc[0, "i_sc (A)"],
        "alpha_sc": changeUnitsK(selected_row.loc[0, "alpha_sc (%/°C)"], selected_row.loc[0, "i_sc (A)"]),
        "beta_voc": changeUnitsK(selected_row.loc[0, "beta_voc (%/°C)"], selected_row.loc[0, "v_oc (V)"]),
        "gamma_pmp": selected_row.loc[0, "gamma_pmp (%/°C)"],
        "cells_in_series": selected_row.loc[0, "cells_in_series"]
        }

    return PV_data

def get_bytes_yaml(dictionary: dict):

    yaml_data = yaml.dump(dictionary, allow_unicode=True)

    buffer = BytesIO()
    buffer.write(yaml_data.encode('utf-8'))
    buffer.seek(0)

    return buffer

#%% funtions streamlit

def get_filter_component_pv(dataframe, min_p_max, max_p_max, min_v_oc, max_v_oc, min_i_sc, max_i_sc, list_celltype, list_manufacturer):

    with st.expander('✂️ Opciones de filtrado'):
        with st.container(border=True):
            col1_1, col1_2 = st.columns([0.4, 0.6])

            checkbox_1 = col1_1.checkbox(label='Potencia máxima (Wp):', value=False)
            slider_1 = col1_2.slider('Seleccionar el rango:', min_p_max, max_p_max, (min_p_max, max_p_max),
                                     disabled=not checkbox_1, key='delta_Wp')
            
            if checkbox_1:
                condition1 = dataframe['p_max (W)'] >= slider_1[0]
                condition2 = dataframe['p_max (W)'] <= slider_1[1]

                dataframe = dataframe[condition1 & condition2]

        with st.container(border=True):
            col2_1, col2_2 = st.columns([0.4, 0.6])

            checkbox_2 = col2_1.checkbox(label='Tensión de circuito-abierto (V):', value=False) 
            slider_2 = col2_2.slider('Seleccionar el rango:', min_v_oc, max_v_oc, (min_v_oc, max_v_oc),
                                     disabled=not checkbox_2, key='delta_Voc')
            
            if checkbox_2:
                condition1 = dataframe['v_oc (V)'] >= slider_2[0]
                condition2 = dataframe['v_oc (V)'] <= slider_2[1]

                dataframe = dataframe[condition1 & condition2]

        with st.container(border=True):
            col3_1, col3_2 = st.columns([0.4, 0.6])

            checkbox_3 = col3_1.checkbox(label='Corriente de corto-circuito (A):', value=False)
            slider_3 = col3_2.slider('Seleccionar el rango:', min_i_sc, max_i_sc, (min_i_sc, max_i_sc),
                                     disabled=not checkbox_3, key='delta_Isc')
            
            if checkbox_3:
                condition1 = dataframe['Isc (A)'] >= slider_3[0]
                condition2 = dataframe['Isc (A)'] <= slider_3[1]

                dataframe = dataframe[condition1 & condition2]

        with st.container(border=True):
            col4_1, col4_2 = st.columns([0.4, 0.6])

            checkbox_4 = col4_1.checkbox(label='celltype:', value=False)
            selectbox_4 = col4_2.selectbox(label='Seleccione una opción', options=list_celltype, index=0,
                                           disabled=not checkbox_4)
            
            if checkbox_4:
                dataframe = dataframe[dataframe['celltype'] == selectbox_4]

        with st.container(border=True):
            col5_1, col5_2 = st.columns([0.4, 0.6])

            checkbox_5 = col5_1.checkbox(label='manufacturer:', value=False)
            selectbox_5 = col5_2.selectbox(label='Seleccione una opción', options=list_manufacturer, index=0,
                                           disabled=not checkbox_5)
            
            if checkbox_5:
                dataframe = dataframe[dataframe['manufacturer'] == selectbox_5]
       
    return dataframe

def dataframe_AgGrid(dataframe: pd.DataFrame) -> pd.DataFrame:

    gb = GridOptionsBuilder.from_dataframe(dataframe)
    gb.configure_selection(selection_mode="single", use_checkbox=True)
    gb.configure_side_bar()
    gridOptions = gb.build()

    data = AgGrid(dataframe,
                  gridOptions=gridOptions,
                  enable_enterprise_modules=True,
                  allow_unsafe_jscode=True,
                  update_mode=GridUpdateMode.SELECTION_CHANGED,
                  columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

    return data["selected_rows"]

def print_data(dataframe: pd.DataFrame, columns_print: list):

    with st.container(border=True):

        for i in range(0,len(columns_print),1):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**:blue[{columns_print[i]}:]**")

            with col2:
                st.markdown(dataframe.loc[0, columns_print[i]])



    return