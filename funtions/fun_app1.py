import streamlit as st
import pandas as pd
import datetime as dt
import yaml
from io import BytesIO
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode

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

def changeUnitsK(K, Base):

    K_out = (Base*K)/100
    
    return K_out

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
            "alpha_sc": changeUnitsK(general.selectedRowColumn(selected_row, params_PV, "alpha_sc"), i_sc),
            "beta_voc": changeUnitsK(general.selectedRowColumn(selected_row, params_PV, "beta_voc"), v_oc),
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

def getDataComponent(sheetLabel: str, dir: str, onLine: bool) -> pd.DataFrame:

    if onLine:
        sheetUrl = general.getGoogleSheetUrl(sheetName=sheetLabel)
        df_data = pd.read_csv(sheetUrl)
    else:
        df_data = pd.read_excel(dir, sheet_name=sheetLabel)

    return df_data

def celltype_options(celltype: dict):

    options = []
    for key, value in celltype.items():
        options.append(f"{key} ({value['label']})")

    return options

#%% funtions streamlit

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