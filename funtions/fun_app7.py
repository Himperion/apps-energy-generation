# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime, date


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
        f"Eload(kWh/{timeLapse})": df_timeLapse["Load(kW)"].sum()*(deltaMinutes/60),
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

def getCompleteDataframeGE(dict_param: dict, dict_phases: dict) -> pd.DataFrame:

    In, Ra, dictPU = get_param_gp(dict_param, dict_phases)
    df_data = get_df_option_characteristic_curve(dictPU, dict_param)
    df_GE = getDataframeGE(dataframe=df_data,
                           dict_pu=dictPU,
                           dict_param=dict_param,
                           columnsOptionsSel={"Load": "Load(kW)"})
    
    return df_GE

#%% funtions streamlit

def get_download_button(directory: str, name_file: str, format_file: str, description: str):
    
    with open(f"{directory}/{name_file}.{format_file}", "rb") as content_xlsx:
                st.download_button(label=f"📄 Descargar plantilla **:red[{description}]**:",
                                   data=content_xlsx,
                                   file_name=f"{name_file}.{format_file}",
                                   mime=format_file)
                
    return

def get_dict_CE_LC(df: pd.DataFrame):

    x = round(float(df.iloc[0]["Load(kW)"]), 4)
    yc = round(float(df.iloc[0]["Consumo_GE(l/h)"]), 4)
    ye = round(float(df.iloc[0]["Eficiencia_GE(%)"]), 4)
    yv = round(float(df.iloc[0]["Vt_GE(V)"]), 4)

    dict_CE = {
        "Consumption":{
            "x": x,
            "y": yc,
            "marker": "x",
            "color": "darkblue",
            "label": f"Consumo (L/h) = {yc}"
        },
        "Efficiency":{
            "x": x,
            "y": ye,
            "marker": "x",
            "color": "darkred",
            "label": f"Eficiencia (%) = {ye}"
        }
    }

    dict_LC = {
        "x": x,
        "y": yv,
        "marker": "x",
        "color": "darkred",
        "label": f"Tensión (V) = {yv}"
    }

    return dict_CE, dict_LC

def getGraphConsumptionEfficiency(dataframe: pd.DataFrame, dict_CE=None):

    fig, ax1 = plt.subplots()

    ax1.set_xlabel("Carga (kW)")
    ax1.set_ylabel("Tasa de consumo (L/h)", color="tab:blue")
    ax1.plot(dataframe["Load(kW)"], dataframe["Consumo_GE(l/h)"], color="tab:blue")
    ax1.grid(True)

    ax2 = ax1.twinx()

    ax2.set_ylabel("Eficiencia de conversión (%)", color="tab:red")
    ax2.plot(dataframe["Load(kW)"], dataframe["Eficiencia_GE(%)"], color="tab:red")

    if dict_CE is not None:
        if "Consumption" in dict_CE:
            ax1.scatter(**dict_CE["Consumption"])
        if "Efficiency" in dict_CE:
            ax2.scatter(**dict_CE["Efficiency"])
            
        fig.legend()

    st.pyplot(fig)

    return

def getGraphLoadCharacteristic(dataframe: pd.DataFrame, dict_LC=None):

    fig, ax1 = plt.subplots()

    ax1.set_xlabel("Carga (kW)")
    ax1.set_ylabel("Tensión (V)", color="tab:red")
    ax1.plot(dataframe["Load(kW)"], dataframe["Vt_GE(V)"], color="tab:red")
    ax1.grid(True)

    if dict_LC is not None:
        ax1.scatter(**dict_LC)
        fig.legend()

    st.pyplot(fig)

def visualizeCurvesGE(df: pd.DataFrame, dict_CE=None, dict_LC=None):

    re_tab1, re_tab2 = st.tabs(["🛢️ Curva de consumo y eficiencia del GE", "📉 Curva de carga del generador"])

    with re_tab1:
        getGraphConsumptionEfficiency(df, dict_CE)
        
    with re_tab2:
        getGraphLoadCharacteristic(df, dict_LC)

    return

def displayResultPrevius(df_previus: pd.DataFrame, time_info: dict, timeLapse: str):

    dictAux = {
        "day": "día",
        "month": "mes"
    }

    tab1, tab2 = st.tabs([f"⚡ Energía demandada por la carga",
                          f"⛽ Consumo de combustible del grupo electrógeno"])

    with tab1:
        params_info ={
            f"Eload(kWh/{timeLapse})": {"label": "Demanda de la carga", "color": "deeppink"}
            }
        serie_label = "Descripción:"

        general.plotVisualizationPxStreamlit(df_previus, time_info, params_info, f"Energía (kWh/{dictAux[timeLapse]})", serie_label)

    with tab2:
        params_info ={
            f"Consumo_GE(l/{timeLapse})": {"label": "Consumo de combustible", "color": "turquoise"}
            }
        serie_label = "Descripción:"

        general.plotVisualizationPxStreamlit(df_previus, time_info, params_info, f"Consumo de combustible (L/{dictAux[timeLapse]})", serie_label)

    return

def displayDailyResults(df_data: pd.DataFrame, df_dailyAnalysis: pd.DataFrame, PARAMS_data: dict, pf_date, label_systems: str, dict_phases: dict):

    time_info ={"name": "Hora", "label": "Hora del día", "strftime": "%H:%M", "description_current": "diaria",
                "description_previus": "horaria"}
    xt, xrsv = -45, False

    df_current = df_dailyAnalysis[df_dailyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.date == pf_date]
    
    df_datatime = df_data[df_data["dates (Y-M-D hh:mm:ss)"].dt.date == pf_date]
    df_datatime = df_datatime.copy()
    df_datatime[time_info["name"]] = df_datatime["dates (Y-M-D hh:mm:ss)"].dt.strftime(time_info["strftime"])

    dictIG = {
        "column_name": ["Load(kW)", "Vt_GE(V)", "Ia_GE(A)", "Eficiencia_GE(%)", "Consumo_GE(l/h)"],
        "value_label": ["Potencia (kW)", "Tensión (V)", "Corriente (A)", "Eficiencia (%)", "Consumo de combustible (L/h)"],
        "color": ["deeppink", "yellowgreen", "darkturquoise", "green", "turquoise"],
        "xt": [xt, xt, xt, xt, xt],
        "xrsv": [xrsv, xrsv, xrsv, xrsv, xrsv],
        "icon": ["💡", "🔋", "🔌", "🚦", "⛽"]
        }
    
    dictReorderIG = general.reorderDictForindividualGraph(dictIG)

    with st.expander(f"**:red[Parámetros de operación horaria del grupo electrógeno]**", icon="🕛"):
        dictTabs = general.valueLabelGetTabs(dictIG)
        for key, value in dictReorderIG.items():
            with dictTabs[key]:
                general.individualGraph(df_datatime, time_info, key, **value)

    list_drop = ["dates (Y-M-D hh:mm:ss)"]

    general.printDataFloatResult(df_current, list_drop)
        
    return

def displayMonthlyResults(df_data: pd.DataFrame, df_dailyAnalysis: pd.DataFrame, df_monthlyAnalysis: pd.DataFrame, PARAMS_data: dict, pf_date, label_systems: str):

    time_info ={"name": "Día", "label": "Día del mes", "strftime": "%d",
                "description_current": "mensual", "description_previus": "diaria"}
    timeLapse = {"current": "month", "previus": "day"}
    xrsv = True

    df_current = df_monthlyAnalysis[(df_monthlyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.year == pf_date.year) & (df_monthlyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.month == pf_date.month)]
    
    df_previus = df_dailyAnalysis[(df_dailyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.year == pf_date.year) & (df_dailyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.month == pf_date.month)]
    df_previus = df_previus.copy()
    df_previus[time_info["name"]] = df_previus["dates (Y-M-D hh:mm:ss)"].dt.strftime(time_info["strftime"])
    
    df_datatime = df_data[(df_data["dates (Y-M-D hh:mm:ss)"].dt.year == pf_date.year) & (df_data["dates (Y-M-D hh:mm:ss)"].dt.month == pf_date.month)]
    df_datatime = df_datatime.copy()
    df_datatime[time_info["name"]] = df_datatime["dates (Y-M-D hh:mm:ss)"].dt.strftime("%d/%m/%y %H:%M")

    dictIG = {
        "column_name": ["Load(kW)", "Vt_GE(V)", "Ia_GE(A)", "Eficiencia_GE(%)", "Consumo_GE(l/h)"],
        "value_label": ["Potencia (kW)", "Tensión (V)", "Corriente (A)", "Eficiencia (%)", "Consumo de combustible (L/h)"],
        "color": ["deeppink", "yellowgreen", "darkturquoise", "green", "turquoise"],
        "xt": [-90, -90, -90, -90, -90],
        "xrsv": [xrsv, xrsv, xrsv, xrsv, xrsv],
        "icon": ["💡", "🔋", "🔌", "🚦", "⛽"]
        }
    
    dictReorderIG = general.reorderDictForindividualGraph(dictIG)

    with st.expander(f"**:red[Parámetros de operación horaria del grupo electrógeno]**", icon="🕛"):
        dictTabs = general.valueLabelGetTabs(dictIG)
        for key, value in dictReorderIG.items():
            with dictTabs[key]:
                general.individualGraph(df_datatime, time_info, key, **value)

    with st.expander(f"**:green[Parámetros de operación diaria del grupo electrógeno]**", icon="📅"):
        displayResultPrevius(df_previus, time_info, timeLapse["previus"])

    list_drop = ["dates (Y-M-D hh:mm:ss)"]

    general.printDataFloatResult(df_current, list_drop)

    return

def displayAnnualResults(df_monthlyAnalysis: pd.DataFrame, df_annualAnalysis: pd.DataFrame, PARAMS_data: dict, pf_date: date, label_systems: str):

    time_info = {"name": "Mes", "label": "Mes del año", "strftime": "%m",
                 "description_current": "anual", "description_previus": "mensual"}
    timeLapse = {"current": "year", "previus": "month"}
    xrsv = True

    df_current = df_annualAnalysis[df_annualAnalysis["dates (Y-M-D hh:mm:ss)"].dt.year == pf_date.year]

    df_previus = df_monthlyAnalysis[df_monthlyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.year == pf_date.year]
    df_previus = df_previus.copy()
    df_previus[time_info["name"]] = df_previus["dates (Y-M-D hh:mm:ss)"].dt.strftime(time_info["strftime"])

    with st.expander(f"**:green[Parámetros de operación mensual del grupo electrógeno]**", icon="📅"):
        displayResultPrevius(df_previus, time_info, timeLapse["previus"])

    list_drop = ["dates (Y-M-D hh:mm:ss)"]

    general.printDataFloatResult(df_current, list_drop)

    return