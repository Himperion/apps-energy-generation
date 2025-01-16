# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import yaml

from funtions import fun_app1


#%% global variables

with open("files//[PV] - params.yaml", 'r') as archivo:
    params_PV = yaml.safe_load(archivo)

with open("files//[INV_PV] - params.yaml", 'r') as archivo:
    params_INV_PV = yaml.safe_load(archivo)

with open("files//[AERO] - params.yaml", 'r') as archivo:
    params_AERO = yaml.safe_load(archivo)

with open("files//[BAT] - params.yaml", 'r') as archivo:
    params_BAT = yaml.safe_load(archivo)

with open("files//[GE] - params.yaml", 'r') as archivo:
    params_GE = yaml.safe_load(archivo)

with open("files//[PV] - celltype.yaml", 'r') as archivo:
    celltype_PV = yaml.safe_load(archivo)

with open("files//[GE] - PE.yaml", 'r') as archivo:
    typefuel_GE = yaml.safe_load(archivo)

with open("files//[COMP] - dict_components.yaml", 'r') as archivo:
    dict_components = yaml.safe_load(archivo)

dict_phases = {
    "Monofásico": {"Num": 1, "label": "1️⃣ Monofásico"},
    "Trifásico": {"Num": 3, "label": "3️⃣ Trifásico"}
}

options_celltype = fun_app1.celltype_options(celltype_PV)
options_batteryType = ["GEL", "Lithium Ion", "AGM"]

dir_components = "files//[DATA] - Components.xlsx"

text_header = "Esta sección permite visualizar los componentes que pueden integrar su proyecto de generación eléctrica."

list_key_components = [key for key in dict_components]
list_sel_components = [value["label"] for value in dict_components.values()]
list_sheet_components = [value["sheet_label"] for key, value in dict_components.items()]

#%% main

if 'component_dict' not in st.session_state:
    st.session_state['component_dict'] = None

if 'component_description' not in st.session_state:
    st.session_state['component_description'] = None

st.markdown("# 🧩 Componentes")

tab1, tab2, tab3 = st.tabs(["📑 Marco teórico", "📝 Entrada de datos", "📂 Listado de componentes"]) 

with tab1:

    st.session_state['component_dict'] = None
    st.session_state['component_description'] = None

    st.markdown(text_header)

with tab2:
    submitted_general, submitted_PV, submitted_AERO, submitted_GE, submitted_GE = False, False, False, False, False

    components_tab2 = st.selectbox(label='Seleccionar componente', options=list_sel_components, index=None,
                                   placeholder='Seleccione una opción', key="components_tab2")
    
    st.text([key for key in dict_components])
    
    if components_tab2 is not None:    
        dict_key = list_key_components[list_sel_components.index(components_tab2)]   
        title = f"{dict_components[dict_key]['emoji']} Parámetros del **:blue[{dict_components[dict_key]['name']}:]**"
       
        if dict_key == "PV":
            with st.form("PV"):
                st.markdown(title)
                with st.container(border=True):
                    st.markdown("🔌 **:blue[{0}:]**".format("Características eléctricas"))
                    col1, col2 = st.columns(2)
                    with col1:
                        Vmpp = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_PV["Vmpp"]),
                                                                disabled=False, variable=params_PV["Vmpp"]["number_input"])
                        Voc = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_PV["Voc"]),
                                                               disabled=False, variable=params_PV["Voc"]["number_input"])
                    with col2:
                        Impp = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_PV["Impp"]),
                                                                disabled=False, variable=params_PV["Impp"]["number_input"])
                        Isc = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_PV["Isc"]),
                                                               disabled=False, variable=params_PV["Isc"]["number_input"])
                with st.container(border=True):
                    st.markdown("🌡️ **:blue[{0}:]**".format("Características de temperatura"))
                
                    alpha_sc = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_PV["alpha_sc"]),
                                                                disabled=False, variable=params_PV["alpha_sc"]["number_input"])
                    beta_voc = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_PV["beta_voc"]),
                                                                disabled=False, variable=params_PV["beta_voc"]["number_input"])
                    gamma_pmp = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_PV["gamma_pmp"]),
                                                                 disabled=False, variable=params_PV["gamma_pmp"]["number_input"])
                    
                with st.container(border=True):
                    st.markdown("🔧 **:blue[{0}:]**".format("Características mecánicas"))
                
                    cell_type = st.selectbox("Tecnologia", options=options_celltype, index=4)

                    cells_in_series = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_PV["cells_in_series"]),
                                                                       disabled=False, variable=params_PV["cells_in_series"]["number_input"])

                submitted = st.form_submit_button("Aceptar")

                if submitted:
                    st.session_state['component_dict'] = {
                        "celltype": fun_app1.for_options_get_celltype(cell_type),
                        "v_mp": Vmpp,
                        "i_mp": Impp,
                        "v_oc": Voc,
                        "i_sc": Isc,
                        "alpha_sc": fun_app1.changeUnitsK(alpha_sc, Isc),
                        "beta_voc": fun_app1.changeUnitsK(beta_voc, Voc),
                        "gamma_pmp": gamma_pmp,
                        "cells_in_series": cells_in_series
                        }
                    
                    st.session_state['component_description'] = ("PV", "Panel fotovoltaico")

        elif dict_key == "BAT":
            with st.form("BAT"):
                st.markdown(title)

                bat_type = st.selectbox("Tecnologia", options=options_batteryType, index=0)
                capacity = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_BAT["capacity"]),
                                                            disabled=False, variable=params_BAT["capacity"]["number_input"])
                V_max = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_BAT["V_max"]),
                                                         disabled=False, variable=params_BAT["V_max"]["number_input"])
                V_min = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_BAT["V_min"]),
                                                         disabled=False, variable=params_BAT["V_min"]["number_input"])
                I_max = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_BAT["I_max"]),
                                                         disabled=False, variable=params_BAT["I_max"]["number_input"])
                efficiency = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_BAT["efficiency"]),
                                                              disabled=False, variable=params_BAT["efficiency"]["number_input"])
                DOD = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_BAT["DOD"]),
                                                       disabled=False, variable=params_BAT["DOD"]["number_input"])

                submitted = st.form_submit_button("Aceptar")

                if submitted:
                    submitted_general, submitted_BAT = True, True

                    st.session_state['component_dict'] = {
                            "bat_type" : bat_type, 
                            "capacity" : capacity, 
                            "V_max" : V_max, 
                            "V_min" : V_min, 
                            "I_max" : I_max,
                            "efficiency": efficiency,
                            "DOD": DOD
                            }
                    
                    st.session_state['component_description'] = ("BAT", "Batería")

        elif dict_key == "AERO":
            with st.form("AERO"):
                st.markdown(title)
            
                D = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_AERO["D"]),
                                                     disabled=False, variable=params_AERO["D"]["number_input"])
                Vin = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_AERO["V_in"]),
                                                       disabled=False, variable=params_AERO["V_in"]["number_input"])
                Vnom = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_AERO["V_nom"]),
                                                        disabled=False, variable=params_AERO["V_nom"]["number_input"])
                Vmax = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_AERO["V_max"]),
                                                        disabled=False, variable=params_AERO["V_max"]["number_input"])
                Pnom = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_AERO["P_nom"]),
                                                        disabled=False, variable=params_AERO["P_nom"]["number_input"])
                
                submitted = st.form_submit_button("Aceptar")

                if submitted:
                    st.session_state['component_dict'] = {
                        "D" : D, 
                        "V_in" : Vin, 
                        "V_nom" : Vnom, 
                        "V_max" : Vmax, 
                        "P_nom" : Pnom
                        }
                    
                    st.session_state['component_description'] = ("AERO", "Aerogenerador")

        elif dict_key == "INV_PV":
            disabled_Vbb = False

            with st.container(border=True):
                st.markdown("🔌 **:blue[{0}:]**".format("Características eléctricas"))

                grid_type = st.selectbox(label="Sistema de conexión a red",
                                         options=["Off-Grid", "On-Grid"],
                                         index=0, placeholder="Selecciona una opción")
                
                phases = st.selectbox(label="Sistema de voltaje",
                                      options=["Monofásico", "Trifásico"],
                                      index=0, placeholder="Selecciona una opción")

                if grid_type == "On-Grid":
                    disabled_Vbb = True
                
            with st.form("INV_PV"):
                st.markdown("🔌 **:blue[{0}:]**".format("Datos eléctricos"))

                Pac_max = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_INV_PV["Pac_max"]),
                                                            disabled=False, variable=params_INV_PV["Pac_max"]["number_input"])
                
                Vac_nom = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_INV_PV["Vac_nom"]),
                                                            disabled=False, variable=params_INV_PV["Vac_nom"]["number_input"])
                
                Vac_max = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_INV_PV["Vac_max"]),
                                                            disabled=False, variable=params_INV_PV["Vac_max"]["number_input"])
                
                Vbb_nom = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_INV_PV["Vbb_nom"]),
                                                           disabled=disabled_Vbb, variable=params_INV_PV["Vbb_nom"]["number_input"])
                
                efficiency_max = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_INV_PV["efficiency_max"]),
                                                                  disabled=disabled_Vbb, variable=params_INV_PV["efficiency_max"]["number_input"])
                submitted = st.form_submit_button("Aceptar")

                if submitted:
                    submitted_general, submitted_INV = True, True

                    st.session_state['component_dict'] = {
                        'Pac_max': Pac_max,
                        'Vac_max': Vac_max,
                        'Vac_nom': Vac_nom,
                        'Vbb_nom': Vbb_nom,
                        'efficiency_max': efficiency_max,
                        'grid_type': grid_type,
                        'phases': phases
                    }

                    st.session_state['component_description'] = (dict_key, dict_components[dict_key]['name'])
                
        elif dict_key == "GE":
            with st.form("GE"):
                with st.container(border=True):
                    st.markdown("🔌 **:blue[{0}:]**".format("Datos eléctricos"))

                    Pnom = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_GE["Pnom"]),
                                                            disabled=False, variable=params_GE["Pnom"]["number_input"])
                
                    col1, col2 = st.columns(2)
                    with col1:
                        Voc = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_GE["Voc"]),
                                                               disabled=False, variable=params_GE["Voc"]["number_input"])
                        Fases = st.selectbox(label="**Fases:** sistema de corriente alterna",
                                            options=[value["label"] for value in dict_phases.values()],
                                            index=0, placeholder="Selecciona una opción")
                    with col2:
                        Vpc = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_GE["Vpc"]),
                                                               disabled=False, variable=params_GE["Vpc"]["number_input"])
                        FP = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_GE["FP"]),
                                                              disabled=False, variable=params_GE["FP"]["number_input"])
            
                with st.container(border=True):
                    st.markdown("🛢️ **:blue[{0}:]**".format("Datos de combustible"))

                    Combustible = st.selectbox(label="**Tipo de combustible:**",
                                               options=[key for key in typefuel_GE],
                                               index=0, placeholder="Selecciona una opción")

                    col1, col2 = st.columns(2)
                    with col1:
                        C100 = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_GE["C'100"]),
                                                                disabled=False, variable=params_GE["C'100"]["number_input"])
                    with col2:
                        C0 = fun_app1.get_widget_number_input(label=fun_app1.get_label_params(dict_param=params_GE["C'0"]),
                                                              disabled=False, variable=params_GE["C'0"]["number_input"])
                        
                submitted = st.form_submit_button("Aceptar")

                if submitted:
                    submitted_general, submitted_GE = True, True

                    st.session_state['component_dict'] = {
                        "Pnom": Pnom,
                        "Voc": Voc,
                        "Vpc": Vpc,
                        "Fases": fun_app1.from_value_label_get_key(dict_phases, "label", Fases),
                        "FP": FP,
                        "Combustible": Combustible,
                        "PE_fuel": typefuel_GE[Combustible]["PE"],
                        "C100": C100,
                        "C0": C0
                        }
                    
                    st.session_state['component_description'] = ("GE", "Grupo electrógeno")

    if st.session_state['component_dict'] is not None and st.session_state['component_description'] is not None:

        fun_app1.get_component_download_button(component_dict=st.session_state['component_dict'],
                                               component_description=st.session_state['component_description'])
                    
                    
                    
                

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
                    