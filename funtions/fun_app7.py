# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px


from funtions import general

#%% funtions general

def get_param_gp(dict_param: dict, dict_phases: dict):

    numPhases = dict_phases[dict_param["phases"]]["Num"]
    
    In = round((dict_param["Pnom"]*1000)/(np.sqrt(numPhases)*dict_param["Vpc"]*dict_param["FP"]), 6)
    Ra = round((dict_param["Voc"] - dict_param["Vpc"]) / In, 6)

    dict_pu = {
        "Sb": dict_param["Pnom"]/dict_param["FP"],
        "Vb": dict_param["Vpc"],
        "Ib": In,
        "Zb": round(dict_param["Vpc"]/In, 6),
        "Ea": dict_param["Voc"]/dict_param["Vpc"],
        "Ra": round((dict_param["Voc"]/dict_param["Vpc"]) - 1, 6)
    }

    return In, Ra, dict_pu

def get_df_option_characteristic_curve(dict_pu: dict, dict_param: dict) -> pd.DataFrame:

    df_GE = pd.DataFrame(np.arange(start=0, stop=1.01, step=0.01), columns=["Load(p.u.)"])
    df_GE["Load(kW)"] = df_GE["Load(p.u.)"]*dict_pu["Sb"]*dict_param["FP"]

    return df_GE

def getRootsQuadraticEcuation(a: float, b: float, c: float):

    x1 = (-b + np.sqrt((b**2)-4*a*c))/(2*a)
    x2 = (-b - np.sqrt((b**2)-4*a*c))/(2*a)

    return x1, x2

def getParamsIaVtGE(load, dict_pu, dict_param):

    load_PU = load/(dict_pu["Sb"]*dict_param["FP"])
    Ia_PU = getRootsQuadraticEcuation(a=dict_pu["Ra"], b=(-1)*dict_pu["Ea"], c=load_PU)[1]
    Vt_PU = dict_pu["Ea"] - Ia_PU*dict_pu["Ra"]
    consumption = ((dict_param["C100"] - dict_param["C0"])*load_PU) + dict_param["C0"]
    efficiency = (load/(consumption*dict_param["PE_fuel"]))*100

    return Ia_PU, Vt_PU, consumption, efficiency

def getDataframeGE(dataframe: pd.DataFrame, dict_pu: dict, dict_param: dict, columnsOptionsSel: dict) -> pd.DataFrame:

    dataframe["Ia_GE(A)"] = 0.0
    dataframe["Vt_GE(V)"] = 0.0
    dataframe["Consumo_GE(l/h)"] = 0.0
    dataframe["Eficiencia_GE(%)"] = 0.0

    if "swLoad(t)" in dataframe.columns:
        for index, row in dataframe.iterrows():
            if row["swLoad(t)"] == 3:
                load = row[columnsOptionsSel["Load"]]
                Ia_PU, Vt_PU, consumption, efficiency = getParamsIaVtGE(load, dict_pu, dict_param)

                dataframe.loc[index, "Ia_GE(A)"] = Ia_PU*dict_pu["Ib"]
                dataframe.loc[index, "Vt_GE(V)"] = Vt_PU*dict_pu["Vb"]
                dataframe.loc[index, "Consumo_GE(l/h)"] = consumption
                dataframe.loc[index, "Eficiencia_GE(%)"] = efficiency
    else:
        for index, row in dataframe.iterrows():
            load = row[columnsOptionsSel["Load"]]
            Ia_PU, Vt_PU, consumption, efficiency = getParamsIaVtGE(load, dict_pu, dict_param)

            dataframe.loc[index, "Ia_GE(A)"] = Ia_PU*dict_pu["Ib"]
            dataframe.loc[index, "Vt_GE(V)"] = Vt_PU*dict_pu["Vb"]
            dataframe.loc[index, "Consumo_GE(l/h)"] = consumption
            dataframe.loc[index, "Eficiencia_GE(%)"] = efficiency

    return dataframe

def getDataAnalysisGE(df_timeLapse: pd.DataFrame, GE_data: dict, deltaMinutes: int, timeLapse: str, date) -> dict:

    # Plantear hacer una distribución normal de los valores de P, V, I, n

    dataAnalysis = {
        f"dates (Y-M-D hh:mm:ss)": date,
        f"Pdem_prom(kW/{timeLapse})": df_timeLapse["Load(kW)"].mean(),
        f"Pdem_max(kW/{timeLapse})": df_timeLapse["Load(kW)"].max(),
        f"Pdem_min(kW/{timeLapse})": df_timeLapse["Load(kW)"].min(),
        f"Vdem_prom(kW/{timeLapse})": df_timeLapse["Vt_GE(V)"].mean(),
        f"Vdem_max(V/{timeLapse})": df_timeLapse["Vt_GE(V)"].max(),
        f"Vdem_min(V/{timeLapse})": df_timeLapse["Vt_GE(V)"].min(),
        f"Idem_prom(A/{timeLapse})": df_timeLapse["Ia_GE(A)"].mean(),
        f"Idem_max(A/{timeLapse})": df_timeLapse["Ia_GE(A)"].max(),
        f"Idem_min(A/{timeLapse})": df_timeLapse["Ia_GE(A)"].min(),
        f"EficienciaProm_GE(%/{timeLapse})": df_timeLapse["Eficiencia_GE(%)"].mean(),
        f"EficienciaMax_GE(%/{timeLapse})": df_timeLapse["Eficiencia_GE(%)"].max(),
        f"EficienciaMin_GE(%/{timeLapse})": df_timeLapse["Eficiencia_GE(%)"].min(),
        f"OperGE(h/{timeLapse})": df_timeLapse["Load(kW)"].count(),
        f"OperGEmaxNom(h/{timeLapse})": (df_timeLapse["Load(kW)"] >= GE_data["Pnom"]).sum()*(deltaMinutes/60),
        f"OperGEminNom(h/{timeLapse})": (df_timeLapse["Load(kW)"] < GE_data["Pnom"]).sum()*(deltaMinutes/60),
        f"Consumo_GE(l/{timeLapse})": df_timeLapse["Consumo_GE(l/h)"].sum()*(deltaMinutes/60),
    }
     
    return dataAnalysis

def getNodeParametersGE(df_datatime: pd.DataFrame, round_decimal: int, label_systems: str) -> dict:

    nodesLabelsColumns = {
        "node1": ["Load(kW)", "Vt_GE(V)", "Ia_GE(A)"]
    }

    nodesPosition = {
        "GE": {"node1": [618, 145]}
    }

    dict_position = nodesPosition[label_systems]

    dictNodes = {}
    for key in dict_position:
        position = tuple(dict_position[key])
        listLabelColumns = nodesLabelsColumns[key]
        num_node = int(key.split("node")[1])

        dictNodes[key] = general.getDictNodeParams(df_datatime, listLabelColumns, round_decimal, num_node, position)
    
    return dictNodes

def getAnalysisInTime(df_data: pd.DataFrame, GE_data: dict, deltaMinutes: int, timeLapse: str) -> pd.DataFrame:
     
    result = []

    for date, group in df_data.groupby(df_data["dates (Y-M-D hh:mm:ss)"].dt.to_period(timeLapse[0].upper())):
        if general.getTimeDimensionCheck(group, deltaMinutes, timeLapse, date):
            dataAnalysis =getDataAnalysisGE(group, GE_data, deltaMinutes, timeLapse, date)

            result.append(dataAnalysis)

    if len(result) != 0:
        return pd.DataFrame(result)
             
    return None

#%% funtions streamlit

def get_download_button(directory: str, name_file: str, format_file: str, description: str):
    
    with open(f"{directory}/{name_file}.{format_file}", "rb") as content_xlsx:
                st.download_button(label=f"📄 Descargar plantilla **:red[{description}]**:",
                                   data=content_xlsx,
                                   file_name=f"{name_file}.{format_file}",
                                   mime=format_file)
                
    return

def getGraphConsumptionEfficiency(dataframe: pd.DataFrame):

    fig, ax1 = plt.subplots()

    ax1.set_xlabel("Load (kW)")
    ax1.set_ylabel("Tasa de consumo (l/h)", color="tab:blue")
    ax1.plot(dataframe["Load(kW)"], dataframe["Consumo_GE(l/h)"], color="tab:blue")
    ax1.grid(True)
    

    ax2 = ax1.twinx()

    ax2.set_ylabel("Eficiencia de conversión (%)", color="tab:red")
    ax2.plot(dataframe["Load(kW)"], dataframe["Eficiencia_GE(%)"], color="tab:red")

    st.pyplot(fig)

    return

def getGraphLoadCharacteristic(dataframe: pd.DataFrame):

    fig, ax1 = plt.subplots()

    ax1.set_xlabel("Load (kW)")
    ax1.set_ylabel("Tensión (V)", color="tab:red")
    ax1.plot(dataframe["Load(kW)"], dataframe["Vt_GE(V)"], color="tab:red")
    ax1.grid(True)

    st.pyplot(fig)

def displayResultCurrent(df_current: pd.DataFrame, time_info: dict, timeLapse: str):

    columnsCurrent = df_current.columns.to_list()

    return

def displayResultDatatime(df_datatime, PARAMS_data, time_info, label_systems, xrsv):


    return

def displayDailyResults(df_data, df_dailyAnalysis, PARAMS_data, pf_date, label_systems):

    time_info ={"name": "Hora", "label": "Hora del día", "strftime": "%H:%M", "description_current": "diaria",
                "description_previus": "horaria"}
    
    timeLapse_current = "day"
    xt, xrsv = -45, False

    df_current = df_dailyAnalysis[df_dailyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.date == pf_date]
    df_datatime = df_data[df_data["dates (Y-M-D hh:mm:ss)"].dt.date == pf_date]
    df_datatime = df_datatime.copy()
    df_datatime[time_info["name"]] = df_datatime["dates (Y-M-D hh:mm:ss)"].dt.strftime(time_info["strftime"])


    #st.dataframe(df_datatime)

    

    dictIG = {
        "column_name": ["Load(kW)", "Vt_GE(V)", "Ia_GE(A)", "Consumo_GE(l/h)"],
        "value_label": ["Potencia (kW)", "Tensión (V)", "Corriente (A)", "Consumo de combustible (L/h)"],
        "color": ["deeppink", "yellowgreen", "darkturquoise", "gold"],
        "xt": [-45, -45, -45, -45],
        "xrsv": [False, False, False, False],
        "icon": ["💡", "🔋", "🔌", "⛽"]
    }

    dictReorderIG = general.reorderDictForindividualGraph(dictIG)

    with st.expander(f"**:red[Parámetros de operación {time_info['description_previus']} del grupo electrógeno]**", icon="🕛"):
        dictTabs = general.valueLabelGetTabs(dictIG)
        for key, value in dictReorderIG.items():
            with dictTabs[key]:
                general.individualGraph(df_datatime, time_info, key, **value)

    

    
    

    
    
    return