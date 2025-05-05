import streamlit as st
import pandas as pd
import yaml
import numpy as np

from funtions import general

#%% global variables

with open("files//[AERO] - params.yaml", 'r') as archivo:
    params_AERO = yaml.safe_load(archivo)

with open("files//[BAT] - params.yaml", 'r') as archivo:
    params_BAT = yaml.safe_load(archivo)

with open("files//[GE] - params.yaml", 'r') as archivo:
    params_GE = yaml.safe_load(archivo)

with open("files//[INVPV] - params.yaml", 'r') as archivo:
    params_INVPV = yaml.safe_load(archivo)

with open("files//[PV] - params.yaml", 'r') as archivo:
    params_PV = yaml.safe_load(archivo)

with open("files//[RC] - params.yaml", 'r') as archivo:
    params_RC = yaml.safe_load(archivo)

with open("files//[GE] - PE.yaml", 'r') as archivo:
    dict_fuel = yaml.safe_load(archivo)

#%% funtions general

def for_options_get_celltype(option):

    key = option.split("(")[0][:-1]

    return key

def get_dict_data(selected_row: pd.DataFrame, key: str) -> dict:

    dict_data = None

    if key == "PV":
        i_sc = general.selectedRowColumn(selected_row, params_PV, "Isc")
        v_oc = general.selectedRowColumn(selected_row, params_PV, "Voc")

        dict_data = {
            "celltype": general.selectedRowColumn(selected_row, params_PV, "celltype"),
            "v_mp": general.selectedRowColumn(selected_row, params_PV, "Vmpp"),
            "i_mp": general.selectedRowColumn(selected_row, params_PV, "Impp"),
            "v_oc": v_oc,
            "i_sc": i_sc,
            "alpha_sc": general.changeUnitsK(general.selectedRowColumn(selected_row, params_PV, "alpha_sc"), i_sc),
            "beta_voc": general.changeUnitsK(general.selectedRowColumn(selected_row, params_PV, "beta_voc"), v_oc),
            "gamma_pmp": general.selectedRowColumn(selected_row, params_PV, "gamma_pmp"),
            "cells_in_series": general.selectedRowColumn(selected_row, params_PV, "cells_in_series")
            }
        
    elif key == "INVPV":
        dict_data = {
            "Pac_max": general.selectedRowColumn(selected_row, params_INVPV, "Pac_max"),
            "Vac_nom": general.selectedRowColumn(selected_row, params_INVPV, "Vac_nom"),
            "Vac_max": general.selectedRowColumn(selected_row, params_INVPV, "Vac_max"),
            "efficiency_max": general.selectedRowColumn(selected_row, params_INVPV, "efficiency_max"),
            "grid_type": general.selectedRowColumn(selected_row, params_INVPV, "grid_type"),
            "phases": general.selectedRowColumn(selected_row, params_INVPV, "phases"),
        }

    elif key == "INVAERO":
        dict_data = {
            "Pac_max": general.selectedRowColumn(selected_row, params_INVPV, "Pac_max"),
            "Vac_nom": general.selectedRowColumn(selected_row, params_INVPV, "Vac_nom"),
            "Vac_max": general.selectedRowColumn(selected_row, params_INVPV, "Vac_max"),
            "efficiency_max": general.selectedRowColumn(selected_row, params_INVPV, "efficiency_max"),
            "grid_type": general.selectedRowColumn(selected_row, params_INVPV, "grid_type"),
            "phases": general.selectedRowColumn(selected_row, params_INVPV, "phases"),
        }

    elif key == "BAT":
        dict_data = {
            "DOD": general.selectedRowColumn(selected_row, params_BAT, "DOD"),
            "I_max": general.selectedRowColumn(selected_row, params_BAT, "I_max"),
            "I_min": general.selectedRowColumn(selected_row, params_BAT, "I_min"),
            "V_max": general.selectedRowColumn(selected_row, params_BAT, "V_max"),
            "V_min": general.selectedRowColumn(selected_row, params_BAT, "V_min"),
            "V_nom": general.selectedRowColumn(selected_row, params_BAT, "V_nom"),
            "bat_type": general.selectedRowColumn(selected_row, params_BAT, "bat_type"),
            "C": general.selectedRowColumn(selected_row, params_BAT, "capacity"),
            "bat_efficiency": general.selectedRowColumn(selected_row, params_BAT, "bat_efficiency"),
        }
    
    elif key == "GE":
        dict_data = {
            "Pnom": general.selectedRowColumn(selected_row, params_GE, "Pnom"),
            "Voc": general.selectedRowColumn(selected_row, params_GE, "Voc"),
            "Vpc": general.selectedRowColumn(selected_row, params_GE, "Vpc"),
            "phases": general.selectedRowColumn(selected_row, params_GE, "phases"),
            "FP": general.selectedRowColumn(selected_row, params_GE, "FP"),
            "Combustible": general.selectedRowColumn(selected_row, params_GE, "fuel_type"),
            "PE_fuel": dict_fuel[general.selectedRowColumn(selected_row, params_GE, "fuel_type")]["PE"],
            "C100": general.selectedRowColumn(selected_row, params_GE, "C'100"),
            "C0": general.selectedRowColumn(selected_row, params_GE, "C'0")
            }
        
    elif key == "AERO":
        dict_data = {
            "D" : general.selectedRowColumn(selected_row, params_AERO, "D"),
            "V_in" : general.selectedRowColumn(selected_row, params_AERO, "V_in"),
            "V_nom" : general.selectedRowColumn(selected_row, params_AERO, "V_nom"),
            "V_max" : general.selectedRowColumn(selected_row, params_AERO, "V_max"),
            "P_nom" : general.selectedRowColumn(selected_row, params_AERO, "P_nom"),
        }

    elif key == "RC":
        dict_data = {
            "Vdc_bb": general.selectedRowColumn(selected_row, params_RC, "Vdc_bb"),
            "rc_efficiency": general.selectedRowColumn(selected_row, params_RC, "rc_efficiency"),
            "SOC_0": general.selectedRowColumn(selected_row, params_RC, "SOC_0"),
            "SOC_min": general.selectedRowColumn(selected_row, params_RC, "SOC_min"),
            "SOC_max": general.selectedRowColumn(selected_row, params_RC, "SOC_max"),
            "SOC_ETP1": general.selectedRowColumn(selected_row, params_RC, "SOC_ETP1"),
            "SOC_ETP2": general.selectedRowColumn(selected_row, params_RC, "SOC_ETP2"),
            "SOC_conx": general.selectedRowColumn(selected_row, params_RC, "SOC_conx"),
        }

    return dict_data

def celltype_options(celltype: dict):

    options = []
    for key, value in celltype.items():
        options.append(f"{key} ({value['label']})")

    return options

def addParametersComponenetsDictionary(dict_components, params_PV, params_INVPV, params_AERO, params_BAT, params_GE, params_RC):

    dict_components["AERO"]["params"] = params_AERO
    dict_components["BAT"]["params"] = params_BAT
    dict_components["GE"]["params"] = params_GE
    dict_components["INVPV"]["params"] = params_INVPV
    dict_components["INVAERO"]["params"] = params_INVPV
    dict_components["PV"]["params"] = params_PV
    dict_components["RC"]["params"] = params_RC

    return dict_components

#%% funtions streamlit

def print_data(dataframe: pd.DataFrame, columns_print: list):

    with st.container(border=True):

        for i in range(0,len(columns_print),1):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**:blue[{columns_print[i]}:]**")
            with col2:
                st.markdown(dataframe.loc[0, columns_print[i]])

    return

def download_button_component(selected_row: pd.DataFrame, key: str, key_label: str):

    COMP_data = get_dict_data(selected_row=selected_row, key=key)

    if COMP_data is not None:
        bytesFileYaml = general.getBytesYaml(dictionary=COMP_data)
        file_name = f"[{key}]_{selected_row.loc[0, 'manufacturer']}-{selected_row.loc[0, 'name']}"
        label = f"📑 Descargar **:blue[archivo de datos]** del {key_label} **YAML**"

        buttonDownload = general.yamlDownloadButton(bytesFileYaml, file_name, label)

    return

def get_component_download_button(component_dict: dict, component_description: tuple):

    bytesFileYaml = general.getBytesYaml(dictionary=component_dict)
    file_name = f"{component_description[0]}_data"
    label = f"📑 Descargar **:blue[archivo de datos]** del {component_description[1]} **YAML**"
        
    buttonDownload = general.yamlDownloadButton(bytesFileYaml, file_name, label)

    return

def get_slider_range_filter(df: pd.DataFrame, params: dict) -> pd.DataFrame:

    if df.shape[0] != 0:
        param_name = "{0} {1}".format(params["label"], params["unit"]).rstrip()
        param_label = "{0} {1}".format(params["description"], params["unit"]).rstrip()

        if params["data_type"] == "float" and not df[param_name].dtype == "float64":
            df = df.copy()
            df[param_name] = df[param_name].str.replace(",", ".").astype(float)

        max_value, min_value = df[param_name].max(), df[param_name].min()

        if not (np.isnan(max_value) and np.isnan(min_value)):
            if max_value > min_value:
                values = st.slider(f"**{param_label}:**", max_value=max_value, min_value=min_value,
                                value=(min_value, max_value))
                
                df = df[(df[param_name] >= values[0]) & (df[param_name] <= values[1])]
                
    return df

def get_multiselect_filter(df: pd.DataFrame, params: dict) -> pd.DataFrame:

    param_name = "{0} {1}".format(params["label"], params["unit"]).rstrip()
    param_label = "{0} {1}".format(params["description"], params["unit"]).rstrip()

    options = df[param_name].unique().tolist()

    sel_options = st.multiselect(f"**{param_label}:**", options=options, default=options,
                                 placeholder="Seleccionar una opción")
    
    df = df[df[param_name].isin(sel_options)]

    return df

def get_component_filter(df: pd.DataFrame, comp: str, params: dict) -> pd.DataFrame:

    column_labels = df.columns.to_list()

    with st.expander("**Aplicar filtros**", icon="✂️"):

        if "manufacturer" in column_labels:
            manufacturer_options = df["manufacturer"].unique().tolist()
            
            op_manufacturer = st.multiselect("**Fabricante:**", options=manufacturer_options,
                                            default=manufacturer_options,
                                            placeholder="Seleccionar una opción")
            
            df = df[df["manufacturer"].isin(op_manufacturer)]

        if comp == "AERO":
            df = get_slider_range_filter(df, params=params["P_nom"])
        elif comp == "BAT":
            df = get_slider_range_filter(df, params=params["capacity"])
            df = get_multiselect_filter(df, params=params["bat_type"])
            df = get_multiselect_filter(df, params=params["V_nom"])
        elif comp == "GE":
            df = get_slider_range_filter(df, params=params["Pnom"])
            df = get_multiselect_filter(df, params=params["phases"])
            df = get_multiselect_filter(df, params=params["fuel_type"])
        elif comp == "INVPV":
            df = get_multiselect_filter(df, params=params["grid_type"])
            df = get_multiselect_filter(df, params=params["phases"])
        elif comp == "INVAERO":
            df = get_multiselect_filter(df, params=params["grid_type"])
            df = get_multiselect_filter(df, params=params["phases"])
        elif comp == "PV":
            df = get_slider_range_filter(df, params=params["Pmax"])
            df = get_multiselect_filter(df, params=params["celltype"])

    return df