# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

from funtions import fun_app1


#%% global variables

dir_components = "files//[DATA] - Components.xlsx"

text_header = "Esta sección permite visualizar los componentes que pueden integrar su proyecto de generación eléctrica."

list_sel_components = ['🪟 Módulos fotovoltaicos',
                       '🖲️ Inversores ',
                       '🔋 Baterías',
                       '📶 Reguladores de carga',
                       '🪁 Aerogeneradores',
                       '⛽ Grupo electrógeno']

#%% main

st.markdown("# 🧩 Componentes")

tab1, tab2 = st.tabs(["📑 Marco teórico", "📝 Entrada de datos"]) 

with tab1: 
    st.markdown(text_header)

with tab2: 
    option_components = st.selectbox(label='Seleccionar componente', options=list_sel_components, index=None,
                                     placeholder='Seleccione una opción')
    
    if option_components is not None:
        df_database, selected_row = None, None
    
        if option_components == list_sel_components[0]:
            df_database = pd.read_excel(dir_components, sheet_name="PV")
            data_filter_pv = fun_app1.get_filtering_options_pv(df_database)
            df_database = fun_app1.get_filter_component_pv(df_database, **data_filter_pv)

        if df_database is not None:
            selected_row = fun_app1.dataframe_AgGrid(dataframe=df_database)
            
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
                    st.link_button("📑 Descargar **:blue[hoja de datos]** del panel fotovoltaico **PDF**", url_datasheet)

                    if option_components == list_sel_components[0]:
                        PV_data = fun_app1.get_dict_PV_data(selected_row=selected_row)
                        buffer_data = fun_app1.get_bytes_yaml(dictionary=PV_data)

                        st.download_button(
                            label="📑 Descargar **:blue[archivo de datos]** del panel fotovoltaico **YAML**",
                            data=buffer_data,
                            file_name=fun_app1.name_file_head(name="PV_data.yaml"),
                            mime="text/yaml"
                        )
                    

                    

                    
            

            st.text(selected_row)
            st.text(type(selected_row))

            st.text(selected_row.loc[0, "manufacturer"])
           

        


