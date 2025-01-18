import streamlit as st
import pandas as pd
import datetime as dt
import yaml
from io import BytesIO

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode

#%% global variables

with open("files//[AERO] - params.yaml", 'r') as archivo:
    params_AERO = yaml.safe_load(archivo)

with open("files//[BAT] - params.yaml", 'r') as archivo:
    params_BAT = yaml.safe_load(archivo)

with open("files//[GE] - params.yaml", 'r') as archivo:
    params_GE = yaml.safe_load(archivo)

with open("files//[INV_PV] - params.yaml", 'r') as archivo:
    params_INV_PV = yaml.safe_load(archivo)

with open("files//[PV] - params.yaml", 'r') as archivo:
    params_PV = yaml.safe_load(archivo)




with open("files//[GE] - PE.yaml", 'r') as archivo:
    dict_fuel = yaml.safe_load(archivo)

#%% funtions general

def name_file_head(name: str) -> str:
    now = dt.datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def from_value_label_get_key(dict_in: dict, key_label: str, value_label: str) -> str:

    for key, value in dict_in.items():
        if value[key_label] == value_label:
            return key

    return

def get_label_column(params: dict, key: str) -> str:

    if params[key]['unit'] == "":
        label_column = str(params[key]['label'])
    else:
        label_column = f"{params[key]['label']} {params[key]['unit']}"

    return label_column

def selected_row_column(selected_row: pd.DataFrame, params: dict, key: str):

    column_name = get_label_column(params, key)
    value = selected_row.loc[0, column_name]

    if value is None:
        output_value = None
    else:
        if params[key]["data_type"] == "int":
            output_value = int(value)
        elif params[key]["data_type"] == "float":
            output_value = float(value)
        elif params[key]["data_type"] == "str":
            output_value = str(value)
    
    return output_value

def changeUnitsK(K, Base):

    K_out = (Base*K)/100
    
    return K_out

def for_options_get_celltype(option):

    key = option.split("(")[0][:-1]

    return key

def get_dict_data(selected_row: pd.DataFrame, key: str) -> dict:

    dict_data = None

    if key == "PV":
        i_sc = selected_row_column(selected_row, params_PV, "Isc")
        v_oc = selected_row_column(selected_row, params_PV, "Voc")

        dict_data = {
            "celltype": selected_row_column(selected_row, params_PV, "celltype"),
            "v_mp": selected_row_column(selected_row, params_PV, "Vmpp"),
            "i_mp": selected_row_column(selected_row, params_PV, "Impp"),
            "v_oc": v_oc,
            "i_sc": i_sc,
            "alpha_sc": changeUnitsK(selected_row_column(selected_row, params_PV, "alpha_sc"), i_sc),
            "beta_voc": changeUnitsK(selected_row_column(selected_row, params_PV, "beta_voc"), v_oc),
            "gamma_pmp": selected_row_column(selected_row, params_PV, "gamma_pmp"),
            "cells_in_series": selected_row_column(selected_row, params_PV, "cells_in_series")
            }
        
    elif key == "INV_PV":
        dict_data = {
            "Pac_max": selected_row_column(selected_row, params_INV_PV, "Pac_max"),
            "Vac_nom": selected_row_column(selected_row, params_INV_PV, "Vac_nom"),
            "Vac_max": selected_row_column(selected_row, params_INV_PV, "Vac_max"),
            "Vbb_nom": selected_row_column(selected_row, params_INV_PV, "Vbb_nom"),
            "efficiency_max": selected_row_column(selected_row, params_INV_PV, "efficiency_max"),
            "grid_type": selected_row_column(selected_row, params_INV_PV, "grid_type"),
            "phases": selected_row_column(selected_row, params_INV_PV, "phases"),
        }

    elif key == "INV_AERO":
        dict_data = {
            "Pac_max": selected_row_column(selected_row, params_INV_PV, "Pac_max"),
            "Vac_nom": selected_row_column(selected_row, params_INV_PV, "Vac_nom"),
            "Vac_max": selected_row_column(selected_row, params_INV_PV, "Vac_max"),
            "Vbb_nom": selected_row_column(selected_row, params_INV_PV, "Vbb_nom"),
            "efficiency_max": selected_row_column(selected_row, params_INV_PV, "efficiency_max"),
            "grid_type": selected_row_column(selected_row, params_INV_PV, "grid_type"),
            "phases": selected_row_column(selected_row, params_INV_PV, "phases"),
        }

    elif key == "BAT":
        dict_data = {
            "DOD": selected_row_column(selected_row, params_BAT, "DOD"),
            "I_max": selected_row_column(selected_row, params_BAT, "I_max"),
            "V_max": selected_row_column(selected_row, params_BAT, "V_max"),
            "V_min": selected_row_column(selected_row, params_BAT, "V_min"),
            "bat_type": selected_row_column(selected_row, params_BAT, "bat_type"),
            "C": selected_row_column(selected_row, params_BAT, "capacity"),
            "efficiency": selected_row_column(selected_row, params_BAT, "efficiency"),
        }
    
    elif key == "GE":
        dict_data = {
            "Pnom": selected_row_column(selected_row, params_GE, "Pnom"),
            "Voc": selected_row_column(selected_row, params_GE, "Voc"),
            "Vpc": selected_row_column(selected_row, params_GE, "Vpc"),
            "Fases": selected_row_column(selected_row, params_GE, "phases"),
            "FP": selected_row_column(selected_row, params_GE, "FP"),
            "Combustible": selected_row_column(selected_row, params_GE, "fuel_type"),
            "PE_fuel": dict_fuel[selected_row_column(selected_row, params_GE, "fuel_type")]["PE"],
            "C100": selected_row_column(selected_row, params_GE, "C'100"),
            "C0": selected_row_column(selected_row, params_GE, "C'0")
            }
        
    elif key == "AERO":
        dict_data = {
            "D" : selected_row_column(selected_row, params_AERO, "D"),
            "V_in" : selected_row_column(selected_row, params_AERO, "V_in"),
            "V_nom" : selected_row_column(selected_row, params_AERO, "V_nom"),
            "V_max" : selected_row_column(selected_row, params_AERO, "V_max"),
            "P_nom" : selected_row_column(selected_row, params_AERO, "P_nom"),
        }

    # Quitar comonente RC, solo es necesario en valor de la eficiencia.

    return dict_data

def get_bytes_yaml(dictionary: dict):

    yaml_data = yaml.dump(dictionary, allow_unicode=True)

    buffer = BytesIO()
    buffer.write(yaml_data.encode('utf-8'))
    buffer.seek(0)

    return buffer

def get_data_component(dir: str, sheet_label: str) -> pd.DataFrame:

    df_data = pd.read_excel(dir, sheet_name=sheet_label)

    return df_data

def get_label_params(dict_param: dict) -> str:

    return f"**{dict_param['label']}:** {dict_param['description']} {dict_param['unit']}"

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
        buffer_data = get_bytes_yaml(dictionary=COMP_data)
        name = f"{selected_row.loc[0, 'manufacturer']}-{selected_row.loc[0, 'name']}"

        st.download_button(
            label=f"📑 Descargar **:blue[archivo de datos]** del {key_label} **YAML**",
            data=buffer_data,
            file_name=name_file_head(name=f"{key}_{name}.yaml"),
            mime="text/yaml"
            )

    return

def get_widget_number_input(label: str, disabled: bool, variable: dict):

    return st.number_input(label=label, disabled=disabled, **variable)

def get_component_download_button(component_dict: dict, component_description: tuple):

    buffer_data = get_bytes_yaml(dictionary=component_dict)

    with st.container(border=True):
        st.download_button(
            label=f"📑 Descargar **:blue[archivo de datos]** del {component_description[1]} **YAML**",
            data=buffer_data,
            file_name=name_file_head(name=f"{component_description[0]}_data.yaml"),
            mime="text/yaml"
            )

    return