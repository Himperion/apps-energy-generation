# -*- coding: utf-8 -*-

import streamlit as st
import yaml

from funtions import general, fun_app1

#%% global variables

with open("files//[PV] - params.yaml", 'r') as archivo:
    params_PV = yaml.safe_load(archivo)

with open("files//[INVPV] - params.yaml", 'r') as archivo:
    params_INVPV = yaml.safe_load(archivo)

with open("files//[AERO] - params.yaml", 'r') as archivo:
    params_AERO = yaml.safe_load(archivo)

with open("files//[BAT] - params.yaml", 'r') as archivo:
    params_BAT = yaml.safe_load(archivo)

with open("files//[GE] - params.yaml", 'r') as archivo:
    params_GE = yaml.safe_load(archivo)

with open("files//[RC] - params.yaml", 'r') as archivo:
    params_RC = yaml.safe_load(archivo)

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
options_VdcBB = [12, 24, 36, 48]

dir_components = "files//[DATA] - Components.xlsx"

text_header = "Esta sección permite visualizar los componentes que pueden integrar su proyecto de generación eléctrica."

list_key_components = [key for key in dict_components]
list_sel_components = [value["label"] for value in dict_components.values()]
list_sheet_components = [value["sheet_label"] for key, value in dict_components.items()]

listTabs = ["📑 Información", "📝 Entrada de datos", "📂 Listado de componentes"]

#%% session_state

if 'component_dict' not in st.session_state:
    st.session_state['component_dict'] = None

if 'component_description' not in st.session_state:
    st.session_state['component_description'] = None

#%% main

st.sidebar.link_button(":violet-badge[**Ir a la app de herramientas**]", "https://app-nasa-power.streamlit.app/", icon="🔧")

st.markdown("# 🧩 Componentes")

tab1, tab2, tab3 = st.tabs(listTabs) 

with tab1:
    st.session_state['component_dict'] = None
    st.session_state['component_description'] = None

    st.markdown("Este aplicativo para hacer rápido y sencillo el ingreso de datos permite la inserción de componentes por medio de archivos **YAML**.")
    st.markdown(f"Puede crear sus propios archivos de componentes **YAML** en la pestaña de **:red[{listTabs[1]}]** o puede descargarlos desde una selección predeterminada desde la pestaña **:red[{listTabs[2]}]**.")

    with st.expander(":blue-badge[**Infografía**]", icon="📝"):
        infographic_path = "files/infographic/01_COMPONENTS.pdf"
        infographic_label = "Componentes"
    
        general.infographicViewer(infographic_path, infographic_label)

with tab2:
    submitted_general, submitted_PV, submitted_AERO, submitted_GE, submitted_GE = False, False, False, False, False

    components_tab2 = st.selectbox(label='Seleccionar componente', options=list_sel_components, index=None,
                                   placeholder='Seleccione una opción', key="components_tab2")
    
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
                        Vmpp = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_PV["Vmpp"]),
                                                            disabled=False, variable=params_PV["Vmpp"]["number_input"],
                                                            key="Vmpp")
                        
                        Voc = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_PV["Voc"]),
                                                           disabled=False, variable=params_PV["Voc"]["number_input"],
                                                           key="Voc")
                    with col2:
                        Impp = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_PV["Impp"]),
                                                            disabled=False, variable=params_PV["Impp"]["number_input"],
                                                            key="Impp")
                        
                        Isc = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_PV["Isc"]),
                                                           disabled=False, variable=params_PV["Isc"]["number_input"],
                                                           key="Isc")
                        
                with st.container(border=True):
                    st.markdown("🌡️ **:blue[{0}:]**".format("Características de temperatura"))
                
                    alpha_sc = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_PV["alpha_sc"]),
                                                            disabled=False, variable=params_PV["alpha_sc"]["number_input"],
                                                            key="alpha_sc")
                    
                    beta_voc = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_PV["beta_voc"]),
                                                            disabled=False, variable=params_PV["beta_voc"]["number_input"],
                                                            key="beta_voc")
                    
                    gamma_pmp = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_PV["gamma_pmp"]),
                                                             disabled=False, variable=params_PV["gamma_pmp"]["number_input"],
                                                             key="gamma_pmp")
                    
                with st.container(border=True):
                    st.markdown("🔧 **:blue[{0}:]**".format("Características mecánicas"))
                
                    cell_type = st.selectbox("Tecnologia", options=options_celltype, index=4)

                    cells_in_series = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_PV["cells_in_series"]),
                                                                   disabled=False, variable=params_PV["cells_in_series"]["number_input"],
                                                                   key="cells_in_series")

                submitted = st.form_submit_button("Aceptar")

                if submitted:
                    
                    st.session_state["component_dict"] = {
                        "alpha_sc": general.changeUnitsK(alpha_sc, Isc),
                        "beta_voc": general.changeUnitsK(beta_voc, Voc),
                        "cells_in_series": cells_in_series,
                        "celltype": fun_app1.for_options_get_celltype(cell_type),
                        "gamma_pmp": gamma_pmp,
                        "i_mp": Impp,
                        "i_sc": Isc,
                        "v_mp": Vmpp,
                        "v_oc": Voc
                    }
                    
                    st.session_state['component_description'] = ("PV", "Panel fotovoltaico")

        elif dict_key == "BAT":
            with st.form("BAT"):
                st.markdown(title)

                bat_type = st.selectbox("Tecnologia", options=options_batteryType, index=0)
                
                capacity = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_BAT["capacity"], key="capacity", disabled=False))
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    V_min = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_BAT["V_min"], key="V_min", disabled=False))
                with col2:
                    V_max = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_BAT["V_max"], key="V_max", disabled=False))
                with col3:
                    V_nom = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_BAT["V_nom"], key="V_nom", disabled=False))
                
                col1, col2 = st.columns(2)
                with col1:
                    I_min = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_BAT["I_min"], key="I_min", disabled=False))
                with col2:    
                    I_max = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_BAT["I_max"], key="I_max", disabled=False))
                
                efficiency = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_BAT["bat_efficiency"], key="efficiency", disabled=False))
                DOD = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_BAT["DOD"], key="DOD", disabled=False))
                

                submitted = st.form_submit_button("Aceptar")

                if submitted:
                    submitted_general, submitted_BAT = True, True
                    
                    st.session_state["component_dict"] = {
                        "C": capacity,
                        "DOD": DOD,
                        "I_max": I_max,
                        "I_min": I_min,
                        "V_max": V_max,
                        "V_min": V_min,
                        "V_nom": V_nom,
                        "bat_type": bat_type,
                        "bat_efficiency": efficiency
                    }
                    
                    st.session_state['component_description'] = ("BAT", "Batería")

        elif dict_key == "AERO":
            with st.form("AERO"):
                st.markdown(title)

                D = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_AERO["D"]),
                                                 disabled=False, variable=params_AERO["D"]["number_input"],
                                                 key="D")
                
                Vin = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_AERO["V_in"]),
                                                   disabled=False, variable=params_AERO["V_in"]["number_input"],
                                                   key="Vin")
                
                Vnom = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_AERO["V_nom"]),
                                                    disabled=False, variable=params_AERO["V_nom"]["number_input"],
                                                    key="Vnom")
                
                Vmax = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_AERO["V_max"]),
                                                    disabled=False, variable=params_AERO["V_max"]["number_input"],
                                                    key="Vmax")
                
                Pnom = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_AERO["P_nom"]),
                                                    disabled=False, variable=params_AERO["P_nom"]["number_input"],
                                                    key="Pnom")
                
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

        elif dict_key == "INVPV":
            with st.form("INVPV"):
                st.markdown(title)
                with st.container(border=True):
                    st.markdown("🔌 **:blue[{0}:]**".format("Características eléctricas"))

                    grid_type = st.selectbox(label="Sistema de conexión a red",
                                            options=["Off-Grid", "On-Grid"],
                                            index=0, placeholder="Selecciona una opción")
                    
                    phases = st.selectbox(label="Sistema de voltaje",
                                        options=["Monofásico", "Trifásico"],
                                        index=0, placeholder="Selecciona una opción")

                with st.container(border=True):
                    st.markdown("🔌 **:blue[{0}:]**".format("Datos eléctricos"))

                    Pac_max = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_INVPV["Pac_max"]),
                                                        disabled=False, variable=params_INVPV["Pac_max"]["number_input"],
                                                        key="Pac_max")
                    
                    Vac_nom = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_INVPV["Vac_nom"]),
                                                        disabled=False, variable=params_INVPV["Vac_nom"]["number_input"],
                                                        key="Vac_nom")
                    
                    Vac_max = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_INVPV["Vac_max"]),
                                                        disabled=False, variable=params_INVPV["Vac_max"]["number_input"],
                                                        key="Vac_max")
                    
                    efficiency_max = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_INVPV["efficiency_max"]),
                                                                disabled=False, variable=params_INVPV["efficiency_max"]["number_input"],
                                                                key="efficiency_max")
                    
                submitted = st.form_submit_button("Aceptar")

                if submitted:
                    submitted_general, submitted_INV = True, True

                    st.session_state['component_dict'] = {
                        'Pac_max': Pac_max,
                        'Vac_max': Vac_max,
                        'Vac_nom': Vac_nom,
                        'efficiency_max': efficiency_max,
                        'grid_type': grid_type,
                        'phases': phases
                    }

                    st.session_state['component_description'] = (dict_key, dict_components[dict_key]['name'])

        elif dict_key == "INVAERO":
            with st.form("INVAERO"):
                st.markdown(title)
                with st.container(border=True):
                    st.markdown("🔌 **:blue[{0}:]**".format("Características eléctricas"))

                    grid_type = st.selectbox(label="Sistema de conexión a red",
                                            options=["Off-Grid", "On-Grid"],
                                            index=0, placeholder="Selecciona una opción")
                    
                    phases = st.selectbox(label="Sistema de voltaje",
                                        options=["Monofásico", "Trifásico"],
                                        index=0, placeholder="Selecciona una opción")
                    
                with st.container(border=True):
                    st.markdown("🔌 **:blue[{0}:]**".format("Datos eléctricos"))

                    Pac_max = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_INVPV["Pac_max"]),
                                                        disabled=False, variable=params_INVPV["Pac_max"]["number_input"],
                                                        key="Pac_max")
                    
                    Vac_nom = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_INVPV["Vac_nom"]),
                                                        disabled=False, variable=params_INVPV["Vac_nom"]["number_input"],
                                                        key="Vac_nom")
                    
                    Vac_max = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_INVPV["Vac_max"]),
                                                        disabled=False, variable=params_INVPV["Vac_max"]["number_input"],
                                                        key="Vac_max")
                    
                    efficiency_max = general.getWidgetNumberInput(label=general.getLabelParams(dict_param=params_INVPV["efficiency_max"]),
                                                                disabled=False, variable=params_INVPV["efficiency_max"]["number_input"],
                                                                key="efficiency_max")
                    
                submitted = st.form_submit_button("Aceptar")

                if submitted:
                    submitted_general, submitted_INV = True, True

                    st.session_state['component_dict'] = {
                        'Pac_max': Pac_max,
                        'Vac_max': Vac_max,
                        'Vac_nom': Vac_nom,
                        'efficiency_max': efficiency_max,
                        'grid_type': grid_type,
                        'phases': phases
                    }

                    st.session_state['component_description'] = (dict_key, dict_components[dict_key]['name'])
               
        elif dict_key == "GE":
            with st.form("GE"):
                st.markdown(title)
                with st.container(border=True):
                    st.markdown("🔌 **:blue[{0}:]**".format("Datos eléctricos"))

                    Pnom = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_GE["Pnom"], key="Pnom", disabled=False))
                
                    col1, col2 = st.columns(2)
                    with col1:
                        Voc = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_GE["Voc"], key="Voc", disabled=False))
                        
                        Fases = st.selectbox(label="**Fases:** sistema de corriente alterna",
                                            options=[value["label"] for value in dict_phases.values()],
                                            index=0, placeholder="Selecciona una opción")
                    with col2:
                        Vpc = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_GE["Vpc"], key="Vpc", disabled=False))

                        FP = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_GE["FP"], key="FP", disabled=False))
            
                with st.container(border=True):
                    st.markdown("🛢️ **:blue[{0}:]**".format("Datos de combustible"))

                    Combustible = st.selectbox(label="**Tipo de combustible:**",
                                               options=[key for key in typefuel_GE],
                                               index=0, placeholder="Selecciona una opción")

                    col1, col2 = st.columns(2)
                    with col1:
                        C100 = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_GE["C'100"], key="C100", disabled=False))
                    with col2:
                        C0 = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_GE["C'0"], key="C0", disabled=False))
                        
                submitted = st.form_submit_button("Aceptar")

                if submitted:
                    submitted_general, submitted_GE = True, True
                    
                    st.session_state["component_dict"] = {
                        "C0": C0,
                        "C100": C100,
                        "Combustible": Combustible,
                        "FP": FP,
                        "PE_fuel": typefuel_GE[Combustible]["PE"],
                        "Pnom": Pnom,
                        "Voc": Voc,
                        "Vpc": Vpc,
                        "phases": general.fromValueLabelGetKey(dict_phases, "label", Fases)
                    }
                    
                    st.session_state['component_description'] = ("GE", "Grupo electrógeno")

        elif dict_key == "RC":
            with st.form("RC"):
                st.markdown(title)
                with st.container(border=True):
                    st.markdown("🔌 **:blue[{0}:]**".format("Datos eléctricos"))

                    Vdc_bb = st.multiselect(label="Tensión nominal del banco de baterías (V)", options=options_VdcBB,
                                            key="Vdc_bb", default=[options_VdcBB[0]])

                    rc_efficiency = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_RC["rc_efficiency"], key="rc_efficiency", disabled=False))
                    
                with st.container(border=True):
                    st.markdown("🔋 **:blue[{0}:]**".format("Gestión del banco de baterías"))
                    
                    SOC_0 = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_RC["SOC_0"], key="SOC_0", disabled=False))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        SOC_min = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_RC["SOC_min"], key="SOC_min", disabled=False))
                    with col2:
                        SOC_max = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_RC["SOC_max"], key="SOC_max", disabled=False))
                        
                    col1, col2 = st.columns(2)
                    with col1:
                        SOC_ETP1 = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_RC["SOC_ETP1"], key="SOC_ETP1", disabled=False))
                    with col2:
                        SOC_ETP2 = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_RC["SOC_ETP2"], key="SOC_ETP2", disabled=False))
                        
                    SOC_conx = general.getWidgetNumberInput(**general.getParamsWidgetNumberInput(dictParam=params_RC["SOC_conx"], key="SOC_conx", disabled=False))
                    
                    submitted = st.form_submit_button("Aceptar")

                    if submitted:
                        submitted_general, submitted_RC = True, True

                        if SOC_min < SOC_max:
                            if SOC_ETP1 < SOC_ETP2:
                                st.session_state['component_dict'] = {
                                    "Vdc_bb": Vdc_bb,
                                    "rc_efficiency": rc_efficiency,
                                    "SOC_0": SOC_0,
                                    "SOC_min": SOC_min,
                                    "SOC_max": SOC_max,
                                    "SOC_ETP1": SOC_ETP1,
                                    "SOC_ETP2": SOC_ETP2,
                                    "SOC_conx": SOC_conx
                                    }

                                st.session_state['component_description'] = ("RC", "Regulador de carga")
                    
                            else:
                                st.error("Error: **El SOC_ETP2 debe ser mayor que el SOC_ETP1**", icon="🚨")
                        else:
                            st.error("Error: **El SOCmax debe ser mayor que el SOCmin**", icon="🚨")
  
    if st.session_state['component_dict'] is not None and st.session_state['component_description'] is not None:

        fun_app1.get_component_download_button(component_dict=st.session_state['component_dict'],
                                               component_description=st.session_state['component_description'])
                    
with tab3: 
    df_data, selected_row = None, None

    components_tab3 = st.selectbox(label='Seleccionar componente', options=list_sel_components, index=None,
                                   placeholder='Seleccione una opción', key="components_tab3")
    
    if components_tab3 is not None:
        dict_key = list_key_components[list_sel_components.index(components_tab3)]
        
        df_data = general.getDataComponent(sheetLabel=dict_components[dict_key]["sheet_label"],
                                           dir=dir_components, onLine=True)
        
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
                    