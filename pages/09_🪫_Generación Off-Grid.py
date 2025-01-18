# -*- coding: utf-8 -*-
import streamlit as st
import yaml

from funtions import fun_app9

#%%  global variables

with open("files//[COMP] - dict_components.yaml", 'r') as archivo:
    dict_components = yaml.safe_load(archivo)

with open("files//[PV] - params.yaml", 'r') as archivo:
    params_PV = yaml.safe_load(archivo)

with open("files//[PV] - dict_replace.yaml", 'r') as archivo:
    rename_PV = yaml.safe_load(archivo)

with open("files//[AERO] - params.yaml", 'r') as archivo:
    params_AERO = yaml.safe_load(archivo)

with open("files//[BAT] - params.yaml", 'r') as archivo:
    params_BAT = yaml.safe_load(archivo)

listGenerationOptions = ["Generación solar", "Generación eólica"]

#%% session state

#%% main

st.markdown("# 🪫 Generación Off-Grid")

tab1, tab2, tab3 = st.tabs(["📑 Marco teórico", "💾 Entrada de datos", "📝 Análisis"])

with tab2:
    with st.container(border=True):
        generationOptions = st.multiselect(label="Opciones de generación eléctrica", options=listGenerationOptions, default=listGenerationOptions[0])
        uploadedXlsxDATA = st.file_uploader(label="**Cargar archivo EXCEL**", type=["xlsx"], key='uploadedYamlDATA')

        if listGenerationOptions[1] in generationOptions:
            rho = fun_app9.get_widget_number_input(label=fun_app9.get_label_params(dict_param=params_AERO["rho"]),
                                                   variable=params_AERO["rho"]["number_input"], key="rho", disabled=False)
        else:
            rho = None

    with st.form("Off-Grid", border=False):

        validateEntries = {
                'check_DATA': False,
                'check_PV': False,
                'check_INV_PV': False,
                'check_AERO': False,
                'check_INV_AERO': False,
            }
        
        PVs, PVp = None, None

        if listGenerationOptions[0] in generationOptions:
            with st.container(border=True):
                st.markdown("☀️ **:blue[Generación de energía solar]**")
                with st.container(border=True):
                    st.markdown(f"{dict_components['PV']['emoji']} **:blue[{dict_components['PV']['name']}:]**")

                    uploadedYamlPV = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlPV')

                    st.markdown("🧑‍🔧 Conexión de los módulos")
                    col1, col2 = st.columns(2)

                    with col1:
                        PVs = fun_app9.get_widget_number_input(label=fun_app9.get_label_params(dict_param=params_PV["PVs"]),
                                                               disabled=False, key="PVs", variable=params_PV["PVs"]["number_input"])
                    with col2:
                        PVp = fun_app9.get_widget_number_input(label=fun_app9.get_label_params(dict_param=params_PV["PVp"]),
                                                               disabled=False, key="PVp", variable=params_PV["PVp"]["number_input"])
                
                with st.container(border=True):
                    st.markdown(f"{dict_components['INV_PV']['emoji']} **:blue[{dict_components['INV_PV']['name']}:]**")

                    uploadedYamlINV_PV = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlINV_PV')

                with st.container(border=True):
                    st.markdown("🔋 **:blue[Banco de baterías:]**")

                    uploadedYamlBAT_PV = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlBAT_PV')

                    st.markdown("🧑‍🔧 Conexión del banco de baterías")
                    col1, col2 = st.columns(2)

                    with col1:
                        Ns_PV = fun_app9.get_widget_number_input(label=fun_app9.get_label_params(dict_param=params_BAT["Ns"]),
                                                                 disabled=False, key="Ns_PV", variable=params_BAT["Ns"]["number_input"])
                    with col2:
                        Np_PV = fun_app9.get_widget_number_input(label=fun_app9.get_label_params(dict_param=params_BAT["Np"]),
                                                                 disabled=False, key="Np_PV", variable=params_BAT["Np"]["number_input"])

        if listGenerationOptions[1] in generationOptions:
            with st.container(border=True):
                st.markdown("🌀 **:green[Generación de energía eólica]**")
                with st.container(border=True):
                    st.markdown(f"{dict_components['AERO']['emoji']} **:green[{dict_components['AERO']['name']}:]**")

                    uploadedYamlAERO = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlAERO')

                with st.container(border=True):
                    st.markdown(f"{dict_components['INV_AERO']['emoji']} **:green[{dict_components['INV_AERO']['name']}:]**")

                    uploadedYamlINV_AERO = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlINV_AERO')

                with st.container(border=True):
                    st.markdown("🔋 **:blue[Banco de baterías:]**")

                    uploadedYamlBAT_AERO = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlBAT_AERO')

                    st.markdown("🧑‍🔧 Conexión del banco de baterías")
                    col1, col2 = st.columns(2)

                    with col1:
                        Ns_AERO = fun_app9.get_widget_number_input(label=fun_app9.get_label_params(dict_param=params_BAT["Ns"]),
                                                                   disabled=False, key="Ns_AERO", variable=params_BAT["Ns"]["number_input"])
                    with col2:
                        Np_AERO = fun_app9.get_widget_number_input(label=fun_app9.get_label_params(dict_param=params_BAT["Np"]),
                                                                   disabled=False, key="Np_AERO", variable=params_BAT["Np"]["number_input"])

        submitted = st.form_submit_button("Aceptar")

        if submitted:
            if listGenerationOptions[0] in generationOptions:
                st.text("Generación SolarOffGrid")

                """
                uploadedYamlPV
                PVs
                PVp
                uploadedYamlINV_PV
                uploadedYamlBAT_PV
                Ns_PV
                Np_PV
                """


        