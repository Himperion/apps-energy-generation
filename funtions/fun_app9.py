# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd


#%% funtions general

def get_label_params(dict_param: dict) -> str:

    return f"**{dict_param['label']}:** {dict_param['description']} {dict_param['unit']}"

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
                    columns_options_drop.append(list_columns_options[i])

        else:
            columns_options_sel[key] = None
            columns_options_check[key] = False

    if len(columns_options_drop) != 0:
        dataframe = dataframe.drop(columns=columns_options_drop)

    for key in columns_options_check:
        check = check and columns_options_check[key]

    return dataframe, check, columns_options_sel

def checkDataframesOnGrid(df_data, generationOptions, itemsOptionsColumnsDf, listGenerationOptions):

    check_PV, check_AERO = False, False
    columnsOptionsData = {}

    df_data, check_DATA, columnsOptionsData["DATA"] = check_dataframe_input(df_data, itemsOptionsColumnsDf["DATA"])

    if len(generationOptions) != 0:
        if listGenerationOptions[0] in generationOptions:   # Generación PV
            df_data, check_PV, columnsOptionsData["PV"] = check_dataframe_input(df_data, itemsOptionsColumnsDf["PV"])

        if listGenerationOptions[1] in generationOptions:   # Generación AERO
            df_data, check_AERO, columnsOptionsData["AERO"] = check_dataframe_input(df_data, itemsOptionsColumnsDf["AERO"])

    return check_DATA, check_PV, check_AERO, columnsOptionsData


#%% funtions streamlit

def getDataValidation(uploadedXlsxDATA, generationOptions, itemsOptionsColumnsDf, listGenerationOptions):

    check_OUT, df_data, columnsOptionsData = False, None, None

    try:
        df_data = pd.read_excel(uploadedXlsxDATA)
        check_DATA, check_PV, check_AERO, columnsOptionsData = checkDataframesOnGrid(df_data, generationOptions, itemsOptionsColumnsDf, listGenerationOptions)
        check_OUT = check_DATA and (check_PV or check_AERO)

        if not check_OUT:
            st.error("Error al cargar archivo (pueden faltar variables para su ejecución) **EXCEL** (.xlsx)", icon="🚨")
    except:
        st.error("Error al cargar archivo **EXCEL** (.xlsx)", icon="🚨")

    return check_OUT, df_data, columnsOptionsData



#%% funtions streamlit

def get_widget_number_input(label: str, disabled: bool, key: str, variable: dict):

    return st.number_input(label=label, disabled=disabled, key=key, **variable)