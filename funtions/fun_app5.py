import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import streamlit as st
import pvlib

def changeUnitsK(K, Base):

    K_out = (Base*K)/100
    
    return K_out

def get_label_params(dict_param: dict) -> str:

    return f"**{dict_param['label']}:** {dict_param['description']} {dict_param['unit']}"

def celltype_options(celltype: dict):

    options = []
    for key, value in celltype.items():
        options.append(f"{key} ({value['label']})")

    return options

def for_options_get_celltype(option):

    key = option.split("(")[0][:-1]

    return key

def get_options_params(dict_params: dict, options_keys: list) -> list:

    dict_options_params = {}

    for key in options_keys:
        string_aux =  f"{dict_params[key]['label']}{dict_params[key]['unit']}: {dict_params[key]['description']}"
        dict_options_params[string_aux] = key
        
    return dict_options_params

def get_PV_params(celltype, v_mp, i_mp, v_oc, i_sc, alpha_sc, beta_voc, gamma_pmp, cells_in_series):

    I_L_ref, I_o_ref, R_s, R_sh_ref, a_ref, Adjust = pvlib.ivtools.sdm.fit_cec_sam(celltype, v_mp, i_mp, v_oc, i_sc, alpha_sc, beta_voc, gamma_pmp, cells_in_series)
    
    PV_params = {
        "alpha_sc": alpha_sc,
        "a_ref": a_ref,
        "I_L_ref": I_L_ref,
        "I_o_ref": I_o_ref,
        "R_sh_ref": R_sh_ref,
        "R_s": R_s,
        "Adjust": Adjust
    }

    return PV_params

def check_dataframe_input(dataframe: pd.DataFrame, options: list) -> bool:

    columns_options, columns_options_sel, columns_options_check = {}, {}, {}
    columns_options_drop, check = [], True

    header = dataframe.columns

    for key in options:
        list_options = options[key]
        columns_aux = []
        for column in header:
            if column in list_options:
                columns_aux.append(column)
        columns_options[key] = columns_aux

    for key in columns_options:
        list_columns_options = columns_options[key]
        if len(list_columns_options) != 0:
            columns_options_sel[key] = list_columns_options[0]
            columns_options_check[key] = True

            if len(list_columns_options) > 1:
                for i in range(1,len(list_columns_options),1):
                    columns_options_drop.append(options[i])

        else:
            columns_options_sel[key] = None
            columns_options_check[key] = False

    if len(columns_options_drop) != 0:
        dataframe = dataframe.drop(columns=columns_options_drop)

    for key in columns_options_check:
        check = check and columns_options_check[key]

    return dataframe, check, columns_options_sel

def get_dataframe_conditions(dataframe: pd.DataFrame, columns_options_sel: dict) -> pd.DataFrame:

    dict_rename = {value: key for key, value in columns_options_sel.items()}

    dataframe = dataframe.rename(columns=dict_rename)
    dataframe = dataframe.loc[:, [key for key in columns_options_sel]]

    return dataframe

#%% funtions streamlit

def get_widget_number_input(label: str, variable: dict):

    return st.number_input(label=label, **variable)

def get_download_button(directory: str, name_file: str, format_file: str, description: str):

    with open(f"{directory}/{name_file}.{format_file}", "rb") as content_xlsx:
                st.download_button(label=f"📄 Descargar plantilla **:red[{description}]**:",
                                   data=content_xlsx,
                                   file_name=name_file,
                                   mime=format_file)
                
    return

def get_expander_params(list_show_output):

    with st.expander(label="🪛 **{0}**".format("Personalizar parámetros de salida")): 
        show_output = st.multiselect(label="Seleccionar parámetros", options=list_show_output, default=list_show_output)

    return show_output