# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

from funtions import fun_app1


#%% global variables

dir_components = "files//[DATA] - Components.xlsx"

text_header = "Esta sección permite visualizar los componentes que pueden integrar su proyecto de generación eléctrica."

dict_components = {
    "PV": {"label": "🪟 Módulo fotovoltaico", "sheet_label": "PV", "name": "Módulo fotovoltaico"},
    "INV": {"label": "🖲️ Inversor", "sheet_label": "INV", "name": "Inversor"},
    "BAT": {"label": "🔋 Baterías", "sheet_label": "BAT", "name": "Baterías"},
    "RC": {"label": "📶 Regulador de carga", "sheet_label": "RC", "name": "Regulador de carga"},
    "AERO": {"label": "🪁 Aerogenerador", "sheet_label": "AERO", "name": "Aerogenerador"},
    "GE": {"label": "⛽ Grupo electrógeno", "sheet_label": "GE", "name": "Grupo electrógeno"}
}

list_key_components = [key for key in dict_components]
list_sel_components = [value["label"] for value in dict_components.values()]
list_sheet_components = [value["sheet_label"] for key, value in dict_components.items()]

#%% main

st.markdown("# 🧩 Componentes")

tab1, tab2, tab3 = st.tabs(["📑 Marco teórico", "📝 Entrada de datos", "📂 Listado de componentes"]) 

with tab1: 
    st.markdown(text_header)

with tab2: 
    st.markdown("tab2")

with tab3: 
    df_data, selected_row = None, None

    option_components = st.selectbox(label='Seleccionar componente', options=list_sel_components, index=None,
                                     placeholder='Seleccione una opción')
    
    if option_components is not None:
        dict_key = list_key_components[list_sel_components.index(option_components)]

        df_data = fun_app1.get_data_component(dir=dir_components,
                                              sheet_label=dict_components[dict_key]["sheet_label"])
        
    if df_data is not None:
        selected_row = fun_app1.dataframe_AgGrid(dataframe=df_data)

    if selected_row is not None:
        selected_columns = selected_row.drop("datasheet", axis=1).columns.tolist()
        selected_row.reset_index(drop=True, inplace=True)

        with st.container(border=True):
            st.markdown('**:blue[{0}] {1}**'.format(selected_row.loc[0, "manufacturer"],
                                                    selected_row.loc[0, "name"]))
            
            sub_tab1, sub_tab2 = st.tabs(["📋 Datos", "💾 Descargas"])

            with sub_tab1:
                fun_app1.print_data(selected_row, selected_columns)

            with sub_tab2:
                url_datasheet = selected_row.loc[0, "datasheet"]
                label_button = dict_components[dict_key]["name"]
                st.link_button(f"📑 Descargar **:blue[hoja de datos]** del {label_button} **PDF**", url_datasheet)

                # components

                
                fun_app1.download_button_component(selected_row, dict_key, label_button)
                    