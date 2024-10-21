import streamlit as st
import pandas as pd
import datetime as dt
import yaml
from io import BytesIO

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode

#%% global variables

with open("files//[PV] - params.yaml", 'r') as archivo:
    params_PV = yaml.safe_load(archivo)

with open("files//[AERO] - params.yaml", 'r') as archivo:
    params_AERO = yaml.safe_load(archivo)

with open("files//[GE] - params.yaml", 'r') as archivo:
    params_GE = yaml.safe_load(archivo)

with open("files//[GE] - PE.yaml", 'r') as archivo:
    dict_fuel = yaml.safe_load(archivo)

#%% funtions general

def name_file_head(name: str) -> str:
    now = dt.datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def get_label_column(params: dict, key: str) -> str:

    if params[key]['unit'] == "":
        label_column = str(params[key]['label'])
    else:
        label_column = f"{params[key]['label']} {params[key]['unit']}"

    return label_column

def selected_row_column(selected_row: pd.DataFrame, params: dict, key: str):

    column_name = get_label_column(params, key)

    if params[key]["data_type"] == "int":
        output_value = int(selected_row.loc[0, column_name])
    elif params[key]["data_type"] == "float":
        output_value = float(selected_row.loc[0, column_name])
    elif params[key]["data_type"] == "str":
        output_value = str(selected_row.loc[0, column_name])
    
    return output_value

def changeUnitsK(K, Base):

    K_out = (Base*K)/100
    
    return K_out

def get_dict_data(selected_row: pd.DataFrame, key: str) -> dict:

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

    PV_data = get_dict_data(selected_row=selected_row, key=key)
    buffer_data = get_bytes_yaml(dictionary=PV_data)
    name = f"{selected_row.loc[0, 'manufacturer']}-{selected_row.loc[0, 'name']}"

    st.download_button(
        label=f"📑 Descargar **:blue[archivo de datos]** del {key_label} **YAML**",
        data=buffer_data,
        file_name=name_file_head(name=f"{key}_{name}.yaml"),
        mime="text/yaml"
        )

    return