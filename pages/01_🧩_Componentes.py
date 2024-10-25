# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import yaml

from funtions import fun_app1


#%% global variables

with open("files//[PV] - params.yaml", 'r') as archivo:
    params_PV = yaml.safe_load(archivo)

with open("files//[AERO] - params.yaml", 'r') as archivo:
    params_AERO = yaml.safe_load(archivo)

with open("files//[GE] - params.yaml", 'r') as archivo:
    params_GE = yaml.safe_load(archivo)

with open("files//[PV] - celltype.yaml", 'r') as archivo:
    celltype_PV = yaml.safe_load(archivo)

with open("files//[GE] - PE.yaml", 'r') as archivo:
    typefuel_GE = yaml.safe_load(archivo)

dict_phases = {
    "Monofásico": {"Num": 1, "label": "1️⃣ Monofásico"},
    "Trifásico": {"Num": 3, "label": "3️⃣ Trifásico"}
}


options_celltype = fun_app1.celltype_options(celltype_PV)

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
    submitted_general, submitted_PV, submitted_AERO, submitted_GE = False, False, False, False

    components_tab2 = st.selectbox(label='Seleccionar componente', options=list_sel_components, index=None,
                                   placeholder='Seleccione una opción', key="components_tab2")

    if components_tab2 is not None:    
        dict_key = list_key_components[list_sel_components.index(components_tab2)]   

        if dict_key == "PV":
            with st.form("PV"):
                with st.container(border=True):
                    st.markdown("🔌 **:blue[{0}:]**".format("Características eléctricas"))
                    col1, col2 = st.columns(2)
                    with col1:
                        Vmpp = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_PV["Vmpp"]),
                                                                variable=params_PV["Vmpp"]["number_input"])
                        Voc = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_PV["Voc"]),
                                                               variable=params_PV["Voc"]["number_input"])
                    with col2:
                        Impp = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_PV["Impp"]),
                                                                variable=params_PV["Impp"]["number_input"])
                        Isc = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_PV["Isc"]),
                                                               variable=params_PV["Isc"]["number_input"])
                with st.container(border=True):
                    st.markdown("🌡️ **:blue[{0}:]**".format("Características de temperatura"))
                
                    alpha_sc = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_PV["alpha_sc"]),
                                                                variable=params_PV["alpha_sc"]["number_input"])
                    beta_voc = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_PV["beta_voc"]),
                                                                variable=params_PV["beta_voc"]["number_input"])
                    gamma_pmp = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_PV["gamma_pmp"]),
                                                                 variable=params_PV["gamma_pmp"]["number_input"])
                    
                with st.container(border=True):
                    st.markdown("🔧 **:blue[{0}:]**".format("Características mecánicas"))
                
                    cell_type = st.selectbox("Tecnologia", options=options_celltype, index=4)

                    cells_in_series = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_PV["cells_in_series"]),
                                                                       variable=params_PV["cells_in_series"]["number_input"])


                submitted = st.form_submit_button("Aceptar")

                if submitted:
                    submitted_general, submitted_PV = True, True

        elif dict_key == "AERO":
            with st.form("PV"):
                st.markdown("⚙️ **:blue[{0}:]**".format("Parámetros del aerogenerador"))
            
                D = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_AERO["D"]),
                                                     variable=params_AERO["D"]["number_input"])
                Vin = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_AERO["V_in"]),
                                                       variable=params_AERO["V_in"]["number_input"])
                Vnom = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_AERO["V_nom"]),
                                                        variable=params_AERO["V_nom"]["number_input"])
                Vmax = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_AERO["V_max"]),
                                                        variable=params_AERO["V_max"]["number_input"])
                Pnom = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_AERO["P_nom"]),
                                                        variable=params_AERO["P_nom"]["number_input"])
                
                submitted = st.form_submit_button("Aceptar")

                if submitted:
                    submitted_general, submitted_AERO = True, True

        elif dict_key == "GE":
            
            with st.form("GE"):
                with st.container(border=True):
                    st.markdown("🔌 **:blue[{0}:]**".format("Datos eléctricos"))

                    Pnom = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_GE["Pnom"]),
                                                            variable=params_GE["Pnom"]["number_input"])
                
                    col1, col2 = st.columns(2)
                    with col1:
                        Voc = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_GE["Voc"]),
                                                            variable=params_GE["Voc"]["number_input"])
                        Fases = st.selectbox(label="**Fases:** sistema de corriente alterna",
                                            options=[value["label"] for value in dict_phases.values()],
                                            index=0, placeholder="Selecciona una opción")
                    with col2:
                        Vpc = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_GE["Vpc"]),
                                                            variable=params_GE["Vpc"]["number_input"])
                        FP = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_GE["FP"]),
                                                            variable=params_GE["FP"]["number_input"])
            
                with st.container(border=True):
                    st.markdown("🛢️ **:blue[{0}:]**".format("Datos de combustible"))

                    Combustible = st.selectbox(label="**Tipo de combustible:**",
                                            options=[key for key in typefuel_GE],
                                            index=0, placeholder="Selecciona una opción")

                    col1, col2 = st.columns(2)
                    with col1:
                        C100 = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_GE["C'100"]),
                                                                variable=params_GE["C'100"]["number_input"])
                    with col2:
                        C0 = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_GE["C'0"]),
                                                            variable=params_GE["C'0"]["number_input"])
                        
                submitted = st.form_submit_button("Aceptar")

                if submitted:
                    submitted_general, submitted_GE = True, True
                
                """
                
                """

        if submitted_general:
            if submitted_PV:
                st.text("PV")
            elif submitted_AERO:
                st.text("AERO")
            elif submitted_GE:
                GE_data = {
                    "Pnom": Pnom,
                    "Voc": Voc,
                    "Vpc": Vpc,
                    "Fases": fun_app1.from_value_label_get_key(dict_phases, Fases),
                    "FP": FP,
                    "Combustible": Combustible,
                    "PE_fuel": typefuel_GE[Combustible]["PE"],
                    "C100": C100,
                    "C0": C0
                    }
                
                buffer_data = fun_app1.get_bytes_yaml(dictionary=GE_data)
                
                with st.container(border=True):
                    st.download_button(
                        label="📑 Descargar **:blue[archivo de datos]** del grupo electrógeno **YAML**",
                        data=buffer_data,
                        file_name=fun_app1.name_file_head(name="GE_data.yaml"),
                        mime="text/yaml"
                        )

with tab3: 
    df_data, selected_row = None, None

    components_tab3 = st.selectbox(label='Seleccionar componente', options=list_sel_components, index=None,
                                   placeholder='Seleccione una opción', key="components_tab3")
    
    if components_tab3 is not None:
        dict_key = list_key_components[list_sel_components.index(components_tab3)]

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
                    