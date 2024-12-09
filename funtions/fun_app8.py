# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

from funtions import fun_app5

#%%




#%% funtions general

def get_label_params(dict_param: dict) -> str:

    return f"**{dict_param['label']}:** {dict_param['description']} {dict_param['unit']}"

def solarGenerationOnGrid(df_data: pd.DataFrame, PV_data: dict, INV_data: dict, PVs: int, PVp: int, v_PCC: float, columnsOptionsData: list, params_PV: dict, rename_PV: dict, show_output: list):

    conditions = fun_app5.get_dataframe_conditions(df_data, columnsOptionsData)
    PV_params = fun_app5.get_PV_params(**PV_data)

    dict_replace = fun_app5.get_dict_replace(dict_rename=rename_PV, dict_params=params_PV)
    df_pv = fun_app5.get_singlediode(conditions, PV_params, PVs, PVp)

    df_pv = fun_app5.get_final_dataframe(df_pv=df_pv,
                                         df_input=df_data,
                                         dict_replace=dict_replace,
                                         dict_conditions=columnsOptionsData,
                                         list_output=show_output)
    
    st.dataframe(df_pv)
    
    
    return


#%% funtions streamlit

def get_widget_number_input(label: str, disabled: bool, variable: dict):

    return st.number_input(label=label, disabled=disabled, **variable)

def check_dict_input(dictionary: dict, options) -> bool:

    return all([key in options for key in dictionary])

def check_dataframe_input(dataframe: pd.DataFrame, options: dict):

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