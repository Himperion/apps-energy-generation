# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

from funtions import fun_app5

#%%

dict_phases = {
    "Monofásico": {"Num": 1, "label": "1️⃣ Monofásico"},
    "Trifásico": {"Num": 3, "label": "3️⃣ Trifásico"}
}

dict_months = {1: "enero",
               2: "febrero",
               3: "marzo",
               4: "abril",
               5: "mayo",
               6: "junio",
               7: "julio",
               8: "agosto",
               9: "septiembre",
               10: "octubre",
               11: "noviembre",
               12: "diciembre"}

#%% funtions general

def name_file_head(name: str) -> str:
    now = datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def to_excel(df: pd.DataFrame):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")

    return output.getvalue()

def get_label_params(dict_param: dict) -> str:

    return f"**{dict_param['label']}:** {dict_param['description']} {dict_param['unit']}"

def getTimeData(df_data: pd.DataFrame) -> dict:

    timeInfo = {}
    numberRows = df_data.shape[0]

    if "dates (Y-M-D hh:mm:ss)" in df_data.columns:
        time_0 = df_data.loc[0, "dates (Y-M-D hh:mm:ss)"].to_pydatetime()
        time_1 = df_data.loc[1, "dates (Y-M-D hh:mm:ss)"].to_pydatetime()

        timeInfo["deltaMinutes"] = (time_1 - time_0).total_seconds()/60
        timeInfo["dateIni"] = time_0
        timeInfo["dateEnd"] = df_data.loc[df_data.index[-1], "dates (Y-M-D hh:mm:ss)"].to_pydatetime()
        timeInfo["deltaDays"] = (numberRows*timeInfo["deltaMinutes"])/1440
        timeInfo["years"] = df_data['dates (Y-M-D hh:mm:ss)'].dt.year.unique().tolist()

        listAuxMonth, listAuxDayYear = [], []
        for year in timeInfo["years"]:
            df_year = df_data[df_data["dates (Y-M-D hh:mm:ss)"].dt.year == year]

            list_month = df_year["dates (Y-M-D hh:mm:ss)"].dt.month.unique().tolist()
            listAuxMonth.append(list_month)

            listAuxDay = []
            for i in range(0,len(list_month),1):
                df_month = df_year[df_year["dates (Y-M-D hh:mm:ss)"].dt.month == list_month[i]]
                listAuxDay.append(df_month["dates (Y-M-D hh:mm:ss)"].dt.day.unique().tolist())

            listAuxDayYear.append(listAuxDay)

        timeInfo["months"] = listAuxMonth
        timeInfo["days"] = listAuxDayYear

    return timeInfo

def solarGenerationOnGrid(df_data: pd.DataFrame, PV_data: dict, INV_data: dict, PVs: int, PVp: int, V_PCC: float, columnsOptionsData: list, params_PV: dict, rename_PV: dict, show_output: list):
    
    conditions = fun_app5.get_dataframe_conditions(df_data, columnsOptionsData)
    PV_params = fun_app5.get_PV_params(**PV_data)

    dict_replace = fun_app5.get_dict_replace(dict_rename=rename_PV, dict_params=params_PV)
    df_pv = fun_app5.get_singlediode(conditions, PV_params, PVs, PVp)

    df_pv = fun_app5.get_final_dataframe(df_pv=df_pv,
                                         df_input=df_data,
                                         dict_replace=dict_replace,
                                         dict_conditions=columnsOptionsData,
                                         list_output=show_output)
    
    numberPhases = dict_phases[INV_data['phases']]['Num']
    
    df_pv.rename(columns={'Impp(A)': 'I_PV(A)', 'Vmpp(V)': 'V_PV(V)', 'Pmpp(kW)': 'Pgen_PV(kW)'}, inplace=True)
    df_pv['Pgen_AC(kW)'] = df_pv['Pgen_PV(kW)']*INV_data['efficiency_max']/100
    df_pv['Pdem(kW)'] = df_pv['Load(kW)'] - df_pv['Pgen_AC(kW)']
    df_pv['V_INV(V)'] = V_PCC
    df_pv['I_INV(A)'] = (df_pv['Pgen_AC(kW)']*1000)/(np.sqrt(numberPhases)*V_PCC)
    df_pv['V_LOAD(V)'] = V_PCC
    df_pv['I_LOAD(A)'] = (df_pv['Load(kW)']*1000)/(np.sqrt(numberPhases)*V_PCC)
    df_pv['V_DEM(V)'] = V_PCC
    df_pv['I_DEM(A)'] = (df_pv['Pdem(kW)']*1000)/(np.sqrt(numberPhases)*V_PCC)
    
    return df_pv

def getFullReport(df_pv: pd.DataFrame, timeInfo: dict):

    for i in range(0,len(timeInfo["years"]),1):
        for j in range(0,len(timeInfo["months"][i]),1):

            df_aux = df_pv[(df_pv["dates (Y-M-D hh:mm:ss)"].dt.year == timeInfo["years"][i]) & (df_pv["dates (Y-M-D hh:mm:ss)"].dt.month == timeInfo["months"][i][j])]
            
            print(timeInfo["years"][i], dict_months[timeInfo["months"][i][j]])
            print(df_aux["Load(kW)"].sum()*(timeInfo["deltaMinutes"]/60))

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