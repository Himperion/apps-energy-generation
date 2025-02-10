# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import yaml

from funtions import fun_app9

#%%  global variables

with open("files//[COMP] - dict_components.yaml", 'r') as archivo:
    dict_components = yaml.safe_load(archivo)

with open("files//[AERO] - params.yaml", 'r') as archivo:
    params_AERO = yaml.safe_load(archivo)

with open("files//[BAT] - params.yaml", 'r') as archivo:
    params_BAT = yaml.safe_load(archivo)

with open("files//[RC] - params.yaml", 'r') as archivo:
    params_RC = yaml.safe_load(archivo)

params_PV, rename_PV, showOutputPV = fun_app9.getGlobalVariablesPV()

listGenerationOptions = ["Generación solar", "Generación eólica", "Respaldo grupo electrógeno"]

itemsOptionsColumnsDf = {
    "DATA": {
        "Dates": ("dates (Y-M-D hh:mm:ss)"),
        "Load" : ("Load(kW)")
    },
    "PV" : {
        "Geff" : ["Gef(W/m^2)", "Gef(W/m²)", "Gin(W/m²)", "Gin(W/m^2)"],
        "Toper" : ["Toper(°C)"]
    },
    "AERO" : {
        "Vwind" : ["Vwind(m/s)", "Vwind 10msnm(m/s)", "Vwind 50msnm(m/s)"]
    }
}

optKeysGE = [
    "C0",
    "C100",
    "Combustible",
    "FP",
    "PE_fuel",
    "Pnom",
    "Voc",
    "Vpc",
    "phases"
]

selectDataEntryOptions = ["📝 Ingresar datos del proyecto",
                          "💾 Cargar archivo de datos del proyecto XLSX"]

#%% session state

if 'dictDataOffGrid' not in st.session_state:
    st.session_state['dictDataOffGrid'] = None

#%% main

st.markdown("# 🪫 Generación Off-Grid")

tab1, tab2, tab3 = st.tabs(["📑 Marco teórico", "💾 Entrada de datos", "📝 Análisis"])

with tab1:
    st.session_state['dictDataOffGrid'] = None

with tab2:
    generationOptions = None

    with st.container(border=True):
        projectDataEntry = st.selectbox(label="Opciones de ingreso de datos", options=selectDataEntryOptions,
                                        index=None, placeholder="Selecciona una opción")
        
        if projectDataEntry == selectDataEntryOptions[0]:
            PVs, PVp, Ns_PV, Np_PV, Ns_AERO, Np_AERO, rho = None, None, None, None, None, None, None
            validateEntries = {
                    "check_DATA": False,
                    "check_PV": False,
                    "check_INVPV": False,
                    "check_BATPV": False,
                    "check_RCPV": False,
                    "check_AERO": False,
                    "check_INVAERO": False,
                    "check_BATAERO": False,
                    "check_RCAERO": False,
                    "check_GE": False
                }
            
            generationOptions = st.multiselect(label="Opciones de generación eléctrica", options=listGenerationOptions, default=listGenerationOptions[0])

            with st.container(border=True):
                st.markdown("📋 **:blue[Datos de carga, temperatura de operación y potencial energetico del sitio:]**")
                uploadedXlsxDATA = st.file_uploader(label="**Cargar archivo EXCEL**", type=["xlsx"], key="uploadedXlsxDATA")

                if listGenerationOptions[1] in generationOptions:
                    rho = fun_app9.get_widget_number_input(label=fun_app9.get_label_params(dict_param=params_AERO["rho"]),
                                                           variable=params_AERO["rho"]["number_input"], key="rho", disabled=False)
                else:
                    rho = None

        with st.form("Off-Grid", border=False):

            if projectDataEntry == selectDataEntryOptions[0]:

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

                    with st.container(border=True):
                        st.markdown("🪫 **:blue[Regulador de carga:]**")
                        uploadedYamlRC_PV = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlRC_PV')

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
                            st.markdown("🔋 **:green[Banco de baterías:]**")
                            uploadedYamlBAT_AERO = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlBAT_AERO')

                            st.markdown("🧑‍🔧 Conexión del banco de baterías")
                            col1, col2 = st.columns(2)
                            with col1:
                                Ns_AERO = fun_app9.get_widget_number_input(label=fun_app9.get_label_params(dict_param=params_BAT["Ns"]),
                                                                           disabled=False, key="Ns_AERO", variable=params_BAT["Ns"]["number_input"])
                            with col2:
                                Np_AERO = fun_app9.get_widget_number_input(label=fun_app9.get_label_params(dict_param=params_BAT["Np"]),
                                                                           disabled=False, key="Np_AERO", variable=params_BAT["Np"]["number_input"])
                        
                        with st.container(border=True):
                            st.markdown("🪫 **:green[Regulador de carga:]**")
                            uploadedYamlRC_AERO = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlRC_AERO')

                if listGenerationOptions[2] in generationOptions:
                    with st.container(border=True):
                        st.markdown("⛽ **:red[Respaldo grupo electrógeno]**")
                        uploadedYamlGE = st.file_uploader(label="**Cargar archivo YAML**", type=["yaml", "yml"], key='uploadedYamlGE')

            if projectDataEntry == selectDataEntryOptions[1]:
                with st.container(border=True):
                    st.markdown("💾 **Cargar archivo de datos del proyecto**")
                    uploadedXlsxPROJECT = st.file_uploader(label="**Cargar archivo XLSX**", type=["xlsx"], key="uploadedXlsxPROJECT")
        
            submitted = st.form_submit_button("Aceptar")

            if submitted:
                if projectDataEntry == selectDataEntryOptions[0]:
                    if uploadedXlsxDATA is not None:
                        validateEntries['check_DATA'], df_data, columnsOptionsData = fun_app9.getDataValidation(uploadedXlsxDATA, generationOptions, itemsOptionsColumnsDf, listGenerationOptions)
                    else:
                        st.error("Cargar **Datos de carga, temperatura de operación y potencial energetico del sitio**", icon="🚨")

                    if len(generationOptions) != 0:
                        PV_data, INVPV_data, BATPV_data, RCPV_data = None, None, None, None
                        AERO_data, INVAERO_data, BATAERO_data, RCAERO_data = None, None, None, None
                        GE_data = None

                        if listGenerationOptions[0] in generationOptions:   # Generación PV
                            validateEntries, PV_data, INVPV_data, BATPV_data, RCPV_data = fun_app9.getDataOffGridValidation(uploadedYamlPV, uploadedYamlINV_PV, uploadedYamlBAT_PV, uploadedYamlRC_PV, validateEntries, "PV")

                        if listGenerationOptions[1] in generationOptions:   # Generación AERO
                            validateEntries, AERO_data, INVAERO_data, BATAERO_data, RCAERO_data = fun_app9.getDataOffGridValidation(uploadedYamlAERO, uploadedYamlINV_AERO, uploadedYamlBAT_AERO, uploadedYamlRC_AERO, validateEntries, "AERO")

                        if listGenerationOptions[2] in generationOptions:   # Generación GE
                            if uploadedYamlGE is not None:
                                validateEntries["check_GE"], GE_data = fun_app9.getCompValidation(uploadedYamlGE, optKeysGE)
                            else:
                                st.error("Cargar **Datos del Grupo electrógeno**", icon="🚨")
                    else:
                        st.error("Ingresar **Opciones de generación eléctrica**", icon="🚨")

                    if fun_app9.getConditionValidateEntriesOffGrid(validateEntries):
                        numberPhases = fun_app9.getNumberPhasesOffGrid(INVPV_data, INVAERO_data, GE_data)

                        if numberPhases is not None:
                            st.session_state['dictDataOffGrid'] = {
                                'df_data': df_data,
                                'PV_data': PV_data,
                                'INVPV_data': INVPV_data,
                                'BATPV_data': BATPV_data,
                                'RCPV_data': RCPV_data,
                                'AERO_data': AERO_data,
                                'INVAERO_data': INVAERO_data,
                                'BATAERO_data': BATAERO_data,
                                'RCAERO_data': RCAERO_data,
                                'rho': rho,
                                'PVs': PVs,
                                'PVp': PVp,
                                'Ns_PV': Ns_PV,
                                'Np_PV': Np_PV,
                                'Ns_AERO': Ns_AERO,
                                'Np_AERO': Np_AERO,
                                'columnsOptionsData': columnsOptionsData,
                                'numberPhases': numberPhases,
                                'validateEntries': validateEntries
                            }

                if projectDataEntry == selectDataEntryOptions[1]:
                    st.text("Echeeeeeeeeeeeeeeeee")

    if st.session_state['dictDataOffGrid'] is not None:

        #fun_app9.processComponentData(st.session_state['dictDataOffGrid'])


        uniqueColumnsOptionsData = fun_app9.getUniqueDictColumnsOptionsData(columnsOptionsData=st.session_state["dictDataOffGrid"]["columnsOptionsData"])
            

        #fun_app9.generationOffGrid(**st.session_state['dictDataOffGrid'])

        

                  

                    

                    


            


        