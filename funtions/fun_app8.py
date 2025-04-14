# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplcursors
from datetime import datetime
import plotly.express as px

from funtions import general

#%%

dict_phases = {
    "Monofásico": {"Num": 1, "label": "1️⃣ Monofásico"},
    "Trifásico": {"Num": 3, "label": "3️⃣ Trifásico"}
}

dict_reportParams = {
        "E_load" : {"label": "Energía de la carga"},
        "E_gen" : {"label": "Energía generada"},
        "E_gen_percent" : {"label": "Energía generada"},
        "E_imp" : {"label": "Energía de importación"},
        "E_exp" : {"label": "Energía de exportación"},
        "E_auto" : {"label": "Energía de autoconsumo"},
        "E_ext1" : {"label": "Excedentes tipo 1"},
        "E_ext2" : {"label": "Excedentes tipo 2"}
    }

#%% funtions general

def getParametersINV_data(INV_data: dict) -> dict:

    if INV_data is not None:
        INV_data['Iac_nom'] = round(float((INV_data['Pac_max']*1000)/(np.sqrt(dict_phases[INV_data['phases']]['Num'])*INV_data['Vac_nom'])), 4)
        INV_data['Rinv'] = round(float((INV_data['Vac_max'] - INV_data['Vac_nom'])/INV_data['Iac_nom']), 4)

    return INV_data

def processComponentDataOnGrid(PV_data: dict, INVPV_data: dict, AERO_data: dict, INVAERO_data: dict,
                               rho: float, PVs: int, PVp: int, V_PCC: float,
                               columnsOptionsData: dict, numberPhases: int, componentInTheProject: dict,
                               generationType):

    TOTAL_data = {}

    if componentInTheProject["generationGE"]:
        TOTAL_data = general.proccesComponentData(TOTAL_data, PV_data, INVPV_data, None, "PV", generationType)
        TOTAL_data["PVs"] = PVs
        TOTAL_data["PVp"] = PVp

    if componentInTheProject["generationAERO"]:
        TOTAL_data = general.proccesComponentData(TOTAL_data, AERO_data, INVAERO_data, None, "AERO", generationType)
        TOTAL_data["rho"] = rho

    if columnsOptionsData is not None:
        TOTAL_data = general.getAddUniqueColumnsOptionsData(TOTAL_data, columnsOptionsData)

    TOTAL_data["V_PCC"] = V_PCC
    TOTAL_data["numberPhases"] = numberPhases
    TOTAL_data["generationType"] = generationType

    return TOTAL_data

def generationOnGrid(df_data: pd.DataFrame,
                     PV_data: dict,
                     INVPV_data: dict,
                     AERO_data: dict,
                     INVAERO_data: dict,
                     rho: float,
                     PVs: int,
                     PVp: int,
                     V_PCC: float,
                     columnsOptionsData: dict,
                     numberPhases: int,
                     componentInTheProject: dict,
                     generationType: str):
    
    params_PV, rename_PV, showOutputPV =  general.getGlobalVariablesPV()
    timeInfo = general.getTimeData(df_data)

    df_onGrid = df_data.copy()
    df_onGrid = general.initializeDataFrameColumns(df_onGrid, generationType)
    
    if componentInTheProject["generationPV"]:       # PV
        df_onGrid = general.getDataframePV(df_onGrid, PV_data, INVPV_data, PVs, PVp, columnsOptionsData, params_PV, rename_PV, showOutputPV, numberPhases)

        df_onGrid["PinvAC_PV(kW)"] =  df_onGrid["Pgen_PV(kW)"]*INVPV_data["efficiency_max"]/100
        df_onGrid["VinvAC_PV(V)"] = V_PCC
        df_onGrid["IinvAC_PV(A)"] = (df_onGrid["PinvAC_PV(kW)"]*1000)/(np.sqrt(numberPhases)*V_PCC)

    if componentInTheProject["generationAERO"]:     # AERO
        df_onGrid = general.getDataframeAERO(df_onGrid, AERO_data, INVAERO_data, rho, columnsOptionsData)

        df_onGrid["PinvAC_AERO(kW)"] =  df_onGrid["Pgen_AERO(kW)"]*INVAERO_data["efficiency_max"]/100
        df_onGrid["VinvAC_AERO(V)"] = V_PCC
        df_onGrid["IinvAC_AERO(A)"] = (df_onGrid["PinvAC_AERO(kW)"]*1000)/(np.sqrt(numberPhases)*V_PCC)

    df_onGrid["Vload(V)"] = V_PCC
    df_onGrid["Iload(A)"] = (df_onGrid['Load(kW)']*1000)/(np.sqrt(numberPhases)*V_PCC)

    df_onGrid["Pdem(kW)"] = df_onGrid["Load(kW)"] - df_onGrid["PinvAC_PV(kW)"] - df_onGrid["PinvAC_AERO(kW)"]
    df_onGrid["Vdem(V)"] = V_PCC
    df_onGrid["Idem(A)"] = df_onGrid["Iload(A)"] - df_onGrid["IinvAC_PV(A)"] - df_onGrid["IinvAC_AERO(A)"]

    return df_onGrid

def getDictParams(COMP_data: dict):

    dictCheck = {
        "PV_data": {},
        "INVPV_data": {},
        "AERO_data": {},
        "INVAERO_data": {}
    }

    dictVar = {
        "PVs": None,
        "PVp": None,
        "V_PCC": None
    }

    for key, value in COMP_data.items():
        for label, dictValue in dictCheck.items():
            if f"[{label}]" == key[:key.find("]")+1]:
                dictValue[key[key.find(']')+2:]] = value

        for keyVar in dictVar:
            if keyVar == key:
                dictVar[key] = value

    PV_data, INVPV_data, AERO_data, INVAERO_data = dictCheck["PV_data"], dictCheck["INVPV_data"], dictCheck["AERO_data"], dictCheck["INVAERO_data"]
    PVs, PVp, V_PCC = dictVar["PVs"], dictVar["PVp"], dictVar["V_PCC"]

    return PV_data, INVPV_data, AERO_data, INVAERO_data, PVs, PVp, V_PCC

def getDataAnalysisOnGrid(df_timeLapse: pd.DataFrame, deltaMinutes: int, timeLapse: str, date) -> dict:

    Egen = (df_timeLapse["PinvAC_PV(kW)"].sum()+df_timeLapse["PinvAC_AERO(kW)"].sum())*(deltaMinutes/60)
    Eimp = df_timeLapse.loc[df_timeLapse["Pdem(kW)"] > 0, "Pdem(kW)"].sum()*(deltaMinutes/60)
    Eexp = df_timeLapse.loc[df_timeLapse["Pdem(kW)"] < 0, "Pdem(kW)"].sum()*(deltaMinutes/60)*(-1)

    if Eexp < Eimp:
        Eexct1 = Eexp
    else:
        Eexct1 = Eimp

    if Eexp > Eimp:
        Eexct2 = Eexp - Eimp
    else:
        Eexct2 = 0

    dataAnalysis = {
        f"dates (Y-M-D hh:mm:ss)": date,
        f"Eload(kWh/{timeLapse})": df_timeLapse["Load(kW)"].sum()*(deltaMinutes/60),
        f"Egen_PV(kWh/{timeLapse})": df_timeLapse["Pgen_PV(kW)"].sum()*(deltaMinutes/60),
        f"Egen_INVPV(kWh/{timeLapse})": df_timeLapse["PinvAC_PV(kW)"].sum()*(deltaMinutes/60),
        f"Egen_AERO(kWh/{timeLapse})": df_timeLapse["Pgen_AERO(kW)"].sum()*(deltaMinutes/60),
        f"Egen_INVAERO(kWh/{timeLapse})": df_timeLapse["PinvAC_AERO(kW)"].sum()*(deltaMinutes/60),
        f"Egen(kWh/{timeLapse})": Egen,
        f"Edem(kWh/{timeLapse})": df_timeLapse["Pdem(kW)"].sum()*(deltaMinutes/60),
        f"Eimp(kWh/{timeLapse})": Eimp,
        f"Eexp(kWh/{timeLapse})": Eexp,
        f"Eauto(kWh/{timeLapse})": Egen - Eexp,
        f"Exct1(kWh/{timeLapse})": Eexct1,
        f"Exct2(kWh/{timeLapse})": Eexct2
        }

    return dataAnalysis

def processComponentsDataOnGrid(PV_data: dict, INVPV_data: dict, AERO_data: dict, INVAERO_data: dict,
                                rho: float, PVs: int, PVp: int, V_PCC: float,
                                columnsOptionsData: dict, numberPhases: int, componentInTheProject: dict,
                                generationType: str):

    TOTAL_data = {}

    if componentInTheProject["generationPV"]:
        TOTAL_data = general.proccesComponentData(TOTAL_data, PV_data, INVPV_data, None, "PV", generationType)
        TOTAL_data["PVs"] = PVs
        TOTAL_data["PVp"] = PVp

    if componentInTheProject["generationAERO"]:
        TOTAL_data = general.proccesComponentData(TOTAL_data, AERO_data, INVAERO_data, None, "AERO", generationType)
        TOTAL_data["rho"] = rho

    TOTAL_data["V_PCC"] = V_PCC

    if columnsOptionsData is not None:
        TOTAL_data = general.getAddUniqueColumnsOptionsData(TOTAL_data, columnsOptionsData)

    TOTAL_data["numberPhases"] = numberPhases

    if componentInTheProject is not None:
        for key, value in componentInTheProject.items():
            TOTAL_data[f"[componentInTheProject] {key}"] = value

    TOTAL_data["generationType"] = generationType

    return TOTAL_data

def getBytesFileExcelProjectOnGrid(dictDataOnGrid: dict, dataKeyList: list):

    dictOutput = general.getImputProcessComponentData(dictDataOnGrid, dataKeyList)
    TOTAL_data = processComponentsDataOnGrid(**dictOutput)
    bytesFileExcel = general.toExcelResults(df=dictDataOnGrid["df_data"], dictionary=TOTAL_data,
                                            df_sheetName="Data", dict_sheetName="Params")

    return TOTAL_data, bytesFileExcel

def getSizesForPieChart(df: pd.DataFrame, list_params: list) -> list:

    return [df.loc[df.index[0], list_params[i]] for i in range(0,len(list_params),1)]

def fromParametersGetLabels(list_params: list):

    dict_replace_param = {
        "Eauto": "Autoconsumo",
        "Eexp": "Exportación",
        "Eimp": "Importación",
        "Exct1": "Excedentes tipo 1",
        "Exct2": "Excedentes tipo 2",
        "Egen_INVPV": "Fotovoltaica",
        "Egen_INVAERO": "Eólica"
    }

    dict_replace_date = {
        "day": "día"
    }

    list_out = list_params.copy()

    for i in range(0,len(list_params),1):
        for key, value in dict_replace_param.items():
            if key in list_params[i]: 
                list_out[i] = list_params[i].replace(key, value)

    for i in range(0,len(list_out),1):
        for key, value in dict_replace_date.items():
            if key in list_out[i]: 
                list_out[i] = list_out[i].replace(key, value)

    for i in range(0,len(list_out),1):
        if list_out[i].count("(") == 1 and list_out[i].count(")"):
            list_out[i] = list_out[i].replace("(", " (")

    return list_out

def get_df_plot(df: pd.DataFrame, time_info: dict, params_info: dict):

    dict_plot ={
        **{time_info["name"]: df["dates (Y-M-D hh:mm:ss)"].dt.strftime(time_info["strftime"])},
        **{value["label"]: df[key] for key, value in params_info.items()}
    }

    df_plot = pd.DataFrame(dict_plot)
    df_long = df_plot.melt(id_vars=time_info["name"], var_name="Serie", value_name="Value")

    return df_long

def get_color_discrete_map(params_info: dict):

    return {params_info[key]["label"]: params_info[key]["color"] for key in params_info}


#%% funtions streamlit

def pieChartVisualizationStreamlit(sizes: list, labels: list, legend_title: str, colors: list, pull: list):
    
    fig = px.pie(
        names=labels,
        values=sizes
        )

    fig.update_traces(
        hovertemplate="%{label}: %{value:.2f} (%{percent})",
        marker=dict(colors=colors),
        pull=pull
        )
    fig.update_layout(
        legend_title_text=legend_title,
        legend=dict(orientation="h")
        )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    return

def plotVisualizationStreamlit(x, dict_y:dict, xlabel: str, ylabel: str, set_ylim0: bool):

    col1, col2, col3 = st.columns([0.1, 0.8, 0.1], vertical_alignment="bottom")

    with col2:
        fig, ax = plt.subplots()

        ax.plot(x, dict_y["value"][0], label=dict_y["label"][0], linestyle=dict_y["linestyle"][0])
        ax.plot(x, dict_y["value"][1], label=dict_y["label"][1], linestyle=dict_y["linestyle"][1])
        ax.plot(x, dict_y["value"][2], label=dict_y["label"][2], linestyle=dict_y["linestyle"][2])

        ax.set_xticks(range(len(x)))
        ax.set_xticklabels(x, rotation=90)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if set_ylim0:
            ax.set_ylim(bottom=0)
        ax.legend()
        ax.grid()
        
        st.pyplot(fig, use_container_width=True)

    return

def displayInstantResults(df_data: pd.DataFrame, analyzeDate: datetime.date, optionTimeRange: str):

    analizeTime = general.getAnalizeTime(analyzeDate=analyzeDate, optionTimeRange=optionTimeRange)
    df_dataFilter = df_data[df_data["dates (Y-M-D hh:mm:ss)"] == analizeTime]
    dictNode = general.getNodeParametersOnGrid(df_dataFilter=df_dataFilter)

    col1, col2, col3, col4 = st.columns(4, vertical_alignment="top")
    with col1:
        general.getNodeVisualization(dictNode=dictNode["node1"], nodeNum=1)
    with col2:
        general.getNodeVisualization(dictNode=dictNode["node2"], nodeNum=2)
    with col3:
        general.getNodeVisualization(dictNode=dictNode["node3"], nodeNum=3)
    with col4:
        general.getNodeVisualization(dictNode=dictNode["node4"], nodeNum=4)

    col1, col2, col3 = st.columns(3, vertical_alignment="top")

    with col1:
        general.getNodeVisualization(dictNode=dictNode["node5"], nodeNum=5)
    with col2:
        general.getNodeVisualization(dictNode=dictNode["node6"], nodeNum=6)
    with col3:
        general.getNodeVisualization(dictNode=dictNode["node7"], nodeNum=7)
    
    return

def displayDailyResults(df_data: pd.DataFrame, df_dailyAnalysis: pd.DataFrame, day):

    df_dailyAnalysisFilter = df_dailyAnalysis[df_dailyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.date == day]
    df_DataDaily = df_data[df_data["dates (Y-M-D hh:mm:ss)"].dt.date == day]
    df_DataDaily = df_DataDaily.copy()
    df_DataDaily.loc[:, "Pgen(kW)"] = df_DataDaily.loc[:, "PinvAC_PV(kW)"] + df_DataDaily.loc[:, "PinvAC_AERO(kW)"]
    
    with st.expander("**Generación diaria**", icon="🍰"):
    
        col1, col2 = st.columns([0.5, 0.5])

        with col1:
            list_params = ["Eauto(kWh/day)", "Eexp(kWh/day)"]
            sizes = getSizesForPieChart(df=df_dailyAnalysisFilter, list_params=list_params)
            labels = fromParametersGetLabels(list_params)
            legend_title = "Tipo de generación"
            colors = ["magenta", "gold"]
            pull = [0.1, 0]

            pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)
            

        with col2:
            list_params = ["Eauto(kWh/day)", "Exct1(kWh/day)", "Exct2(kWh/day)"]
            sizes = getSizesForPieChart(df=df_dailyAnalysisFilter, list_params=list_params)
            labels = fromParametersGetLabels(list_params)
            legend_title = "Tipo de generación"
            colors = ["magenta", "turquoise", "violet"]
            pull = [0.1, 0, 0]

            pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)
        
    with st.expander("**Atención de la carga**", icon="🍰"):
        list_params = ["Eimp(kWh/day)", "Eauto(kWh/day)"]
        sizes = getSizesForPieChart(df=df_dailyAnalysisFilter, list_params=list_params)
        labels = fromParametersGetLabels(list_params)
        legend_title = "Tipo de atención"
        colors = ["purple", "magenta"]
        pull = [0.1, 0, 0]

        pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)

    with st.expander(f"**Interacción entre demanda y generación - :blue[{day}]**", icon="📊"):

        time_info ={
            "name": "Hora",
            "label": "Hora del día",
            "strftime": "%H:%M"
        }
        params_info ={
            "Pgen(kW)": {"label": "Generación (kW)", "color": "turquoise"},
            "Load(kW)": {"label": "Demanda de la carga (kW)", "color": "teal"}
        }

        value_label, serie_label = "Potencia (kW)", "Tipo de interacción"

        df_long = get_df_plot(df_DataDaily, time_info, params_info)


        fig = px.bar(
            df_long,
            x=time_info["name"], y="Value", color="Serie", barmode="group",
            labels={
                time_info["name"]: time_info["label"],
                "Value": value_label,
                "Serie": serie_label
            },
            color_discrete_map=get_color_discrete_map(params_info),
            hover_data={
                "Value": ":.3",
                time_info["name"]: True,
                "Serie": True
            }
        )

        fig.update_layout(xaxis_tickangle=-90,
                          legend=dict(orientation="h",
                                      y=10,
                                      yanchor="bottom"))
        
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with st.expander(f"**Producción diaria - :blue[{day}]**", icon="📊"):
        df_plot = pd.DataFrame({
            "Hora": df_DataDaily["dates (Y-M-D hh:mm:ss)"].dt.strftime('%H:%M'),
            "Fotovoltaica (kW)": df_DataDaily["PinvAC_PV(kW)"],
            "Eólica (kW)": df_DataDaily["PinvAC_AERO(kW)"]
        })

        df_long = df_plot.melt(id_vars="Hora", var_name="Serie", value_name="Value")

        tab1, tab2 = st.tabs(["🍰 Diagrama de torta", "📊 Gráfico de barras"])

        with tab1:
            list_params = ["Egen_INVPV(kWh/day)", "Egen_INVAERO(kWh/day)"]
            sizes = getSizesForPieChart(df=df_dailyAnalysisFilter, list_params=list_params)
            labels = fromParametersGetLabels(list_params)
            legend_title = "Tipo de fuente de generación"
            colors=["royalblue", "green"]
            pull = [0.1, 0]

            pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)

        with tab2:
            fig = px.bar(
                df_long,
                x="Hora", y="Value", color="Serie", barmode="group",
                labels={
                    "Hora": "Hora del día",
                    "Value": "Potencia (kW)",
                    "Serie": "Tipo de fuente de generación"
                },
                color_discrete_map={
                    "Fotovoltaica (kW)": "royalblue",
                    "Eólica (kW)": "green"
                },
                hover_data={
                    "Value": ":.3",
                    "Hora": True,
                    "Serie": True
                }
            )

            fig.update_layout(xaxis_tickangle=-90)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with st.expander(f"**Demanda diaria - :blue[{day}]**", icon="📊"):
        df_plot = pd.DataFrame({
            "Hora": df_DataDaily["dates (Y-M-D hh:mm:ss)"].dt.strftime('%H:%M'),
            "Pdem(kW)": df_DataDaily["Pdem(kW)"]
        })

        df_plot["Exportación (kW)"], df_plot["Importación (kW)"] = 0.0, 0.0
        df_plot.loc[df_plot["Pdem(kW)"] < 0.0, "Exportación (kW)"] = df_plot["Pdem(kW)"]
        df_plot.loc[df_plot["Pdem(kW)"] > 0.0, "Importación (kW)"] = df_plot["Pdem(kW)"]
        df_plot.drop(columns=["Pdem(kW)"], inplace=True)
        df_long = df_plot.melt(id_vars="Hora", var_name="Serie", value_name="Value")

        tab1, tab2 = st.tabs(["🍰 Diagrama de torta", "📊 Gráfico de barras"])

        with tab1:
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                list_params = ["Eimp(kWh/day)", "Eexp(kWh/day)"]
                sizes = getSizesForPieChart(df=df_dailyAnalysisFilter, list_params=list_params)
                labels = fromParametersGetLabels(list_params)
                legend_title = "Tipo de demanda"
                colors = ["red", "orange"]
                pull = [0.1, 0]

                pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)

            with col2:
                list_params = ["Eimp(kWh/day)", "Exct1(kWh/day)", "Exct2(kWh/day)"]
                sizes = getSizesForPieChart(df=df_dailyAnalysisFilter, list_params=list_params)
                labels = fromParametersGetLabels(list_params)
                legend_title = "Tipo de demanda"
                colors = ["red", "gold", "olive"]
                pull = [0.1, 0, 0]

                pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)

        with tab2:
            fig = px.bar(
                df_long,
                x="Hora", y="Value", color="Serie", barmode="relative",
                labels={
                    "Hora": "Hora del día",
                    "Value": "Potencia (kW)",
                    "Serie": "Tipo de demanda"
                },
                color_discrete_map={
                    "Exportación (kW)": "red",
                    "Importación (kW)": "orange"
                },
                hover_data={
                    "Value": ":.3",
                    "Hora": True,
                    "Serie": True
                }
            )

            fig.update_layout(xaxis_tickangle=-90)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with st.expander(f"**Curva potencia generada :blue[{day}]**", icon="📈"):
        x = df_DataDaily["dates (Y-M-D hh:mm:ss)"].dt.strftime('%H:%M')
        
        dict_y = {
            "value": [df_DataDaily["PinvAC_PV(kW)"], df_DataDaily["PinvAC_AERO(kW)"], df_DataDaily["Pgen(kW)"]],
            "label": ["Pgen_PV(kW)", "Pgen_AERO(kW)", "Pgen(kW)"],
            "linestyle": ["-", "-", "--"]
        }

        plotVisualizationStreamlit(x, dict_y=dict_y, xlabel="Hour", ylabel="Power (kW)", set_ylim0=True)

    columnsPrint = df_dailyAnalysisFilter.drop("dates (Y-M-D hh:mm:ss)", axis=1).columns.tolist()
    general.printData(dataframe=df_dailyAnalysisFilter, columns_print=columnsPrint)

    return

def displayMonthlyResults(df_data: pd.DataFrame, df_dailyAnalysis: pd.DataFrame, df_monthlyAnalysis: pd.DataFrame, optionYearRange, optionMonthRange):

    monthIndex = general.fromMonthGetIndex(month=optionMonthRange)
    df_monthlyAnalysisFilter = df_monthlyAnalysis[(df_monthlyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.year == optionYearRange) & (df_monthlyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.month == monthIndex)]

    df_DataMonthly = df_data[df_data["dates (Y-M-D hh:mm:ss)"].dt.month == monthIndex]
    df_DataMonthly = df_DataMonthly.copy()
    df_DataMonthly.loc[:, "Pgen(kW)"] = df_DataMonthly.loc[:, "PinvAC_PV(kW)"] + df_DataMonthly.loc[:, "PinvAC_AERO(kW)"]

    df_dailyAnalysisFilter = df_dailyAnalysis[df_dailyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.month == monthIndex]

    with st.expander("**Distribución de energía generada en autoconsumo y excedentes**", icon="📊"):
        labels = ["Eauto(kWh/month)", "Exct1(kWh/month)", "Exct2(kWh/month)"]
        sizes = [df_monthlyAnalysisFilter.loc[df_monthlyAnalysisFilter.index[0], labels[i]] for i in range(0,len(labels),1)]

        pieChartVisualizationStreamlit(sizes=sizes, labels=labels)

    with st.expander("**Distribución de energía generada**", icon="📊"):
        labels = ["Egen_PV(kWh/month)", "Egen_AERO(kWh/month)"]
        sizes = [df_monthlyAnalysisFilter.loc[df_monthlyAnalysisFilter.index[0], labels[i]] for i in range(0,len(labels),1)]

        pieChartVisualizationStreamlit(sizes=sizes, labels=labels)

    with st.expander(f"**Curva de energías :blue[{optionYearRange}-{optionMonthRange}]**", icon="📈"):
        x = df_dailyAnalysisFilter["dates (Y-M-D hh:mm:ss)"].dt.strftime("%d")
        dict_y = {
            "value": [df_dailyAnalysisFilter["Edem(kWh/day)"],
                      df_dailyAnalysisFilter["Egen(kWh/day)"],
                      df_dailyAnalysisFilter["Eload(kWh/day)"]],
            "label": ["Edem(kWh/day)", "Egen(kWh/day)", "Eload(kWh/day)"],
            "linestyle": ["-", "-", "-"]
        }

        plotVisualizationStreamlit(x, dict_y=dict_y, xlabel="Day", ylabel="Energy (kWh/day)", set_ylim0=False)

    with st.expander(f"**Curva energía generada :blue[{optionYearRange}-{optionMonthRange}]**", icon="📈"):
        x = df_dailyAnalysisFilter["dates (Y-M-D hh:mm:ss)"].dt.strftime("%d")

        dict_y = {
            "value": [df_dailyAnalysisFilter["Egen_INVPV(kWh/day)"],
                      df_dailyAnalysisFilter["Egen_INVAERO(kWh/day)"],
                      df_dailyAnalysisFilter["Egen(kWh/day)"]],
            "label": ["Egen_PV(kWh/day)", "Egen_AERO(kWh/day)", "Egen(kWh/day)"],
            "linestyle": ["-", "-", "--"]
        }

        plotVisualizationStreamlit(x, dict_y=dict_y, xlabel="Day", ylabel="Energy (kWh/day)", set_ylim0=True)

    with st.expander(f"**Curva energía exportada :blue[{optionYearRange}-{optionMonthRange}]**", icon="📈"):
        x = df_dailyAnalysisFilter["dates (Y-M-D hh:mm:ss)"].dt.strftime("%d")

        dict_y = {
            "value": [df_dailyAnalysisFilter["Exct1(kWh/day)"],
                      df_dailyAnalysisFilter["Exct2(kWh/day)"],
                      df_dailyAnalysisFilter["Eexp(kWh/day)"]],
            "label": ["Exct1(kWh/day)", "Exct2(kWh/day)", "Eexp(kWh/day)"],
            "linestyle": ["-", "-", "--"]
        }

        plotVisualizationStreamlit(x, dict_y=dict_y, xlabel="Day", ylabel="Energy (kWh/day)", set_ylim0=True)

    columnsPrint = df_monthlyAnalysisFilter.drop("dates (Y-M-D hh:mm:ss)", axis=1).columns.tolist()
    general.printData(dataframe=df_monthlyAnalysisFilter, columns_print=columnsPrint)

    return

def displayAnnualResults(df_monthlyAnalysis: pd.DataFrame, df_annualAnalysis: pd.DataFrame, optionYearRange):
    
    df_annualAnalysisFilter = df_annualAnalysis[df_annualAnalysis["dates (Y-M-D hh:mm:ss)"].dt.year == optionYearRange]
    df_monthlyAnalysisFilter = df_monthlyAnalysis[df_monthlyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.year == optionYearRange]

    with st.expander("**Distribución de energía generada en autoconsumo y excedentes**", icon="📊"):
        labels = ["Eauto(kWh/year)", "Exct1(kWh/year)", "Exct2(kWh/year)"]
        sizes = [df_annualAnalysisFilter.loc[df_annualAnalysisFilter.index[0], labels[i]] for i in range(0,len(labels),1)]

        pieChartVisualizationStreamlit(sizes=sizes, labels=labels)

    with st.expander("**Distribución de energía generada**", icon="📊"):
        labels = ["Egen_PV(kWh/year)", "Egen_AERO(kWh/year)"]
        sizes = [df_annualAnalysisFilter.loc[df_annualAnalysisFilter.index[0], labels[i]] for i in range(0,len(labels),1)]

        pieChartVisualizationStreamlit(sizes=sizes, labels=labels)

    with st.expander(f"**Curva de energías :blue[{optionYearRange}]**", icon="📈"):
        x = df_monthlyAnalysisFilter["dates (Y-M-D hh:mm:ss)"].dt.strftime("%m")
        
        dict_y = {
            "value": [df_monthlyAnalysisFilter["Edem(kWh/month)"],
                      df_monthlyAnalysisFilter["Egen(kWh/month)"],
                      df_monthlyAnalysisFilter["Eload(kWh/month)"]],
            "label": ["Edem(kWh/month)", "Egen(kWh/month)", "Eload(kWh/month)"],
            "linestyle": ["-", "-", "-"]
        }

        plotVisualizationStreamlit(x, dict_y=dict_y, xlabel="Month", ylabel="Energy (kWh/month)", set_ylim0=False)

    with st.expander(f"**Curva energía generada :blue[{optionYearRange}]**", icon="📈"):
        x = df_monthlyAnalysisFilter["dates (Y-M-D hh:mm:ss)"].dt.strftime("%m")

        dict_y = {
            "value": [df_monthlyAnalysisFilter["Egen_INVPV(kWh/month)"],
                      df_monthlyAnalysisFilter["Egen_INVAERO(kWh/month)"],
                      df_monthlyAnalysisFilter["Egen(kWh/month)"]],
            "label": ["Egen_PV(kWh/month)", "Egen_AERO(kWh/month)", "Egen(kWh/month)"],
            "linestyle": ["-", "-", "--"]
        }

        plotVisualizationStreamlit(x, dict_y=dict_y, xlabel="Month", ylabel="Energy (kWh/month)", set_ylim0=True)

    with st.expander(f"**Curva energía exportada :blue[{optionYearRange}]**", icon="📈"):
        x = df_monthlyAnalysisFilter["dates (Y-M-D hh:mm:ss)"].dt.strftime("%m")
        y1 = df_monthlyAnalysisFilter["Exct1(kWh/month)"]
        y2 = df_monthlyAnalysisFilter["Exct2(kWh/month)"]
        y3 = df_monthlyAnalysisFilter["Eexp(kWh/month)"]

        dict_y = {
            "value": [df_monthlyAnalysisFilter["Exct1(kWh/month)"],
                      df_monthlyAnalysisFilter["Exct2(kWh/month)"],
                      df_monthlyAnalysisFilter["Eexp(kWh/month)"]],
            "label": ["Exct1(kWh/month)", "Exct2(kWh/month", "Eexp(kWh/month)"],
            "linestyle": ["-", "-", "--"]
        }

        plotVisualizationStreamlit(x, dict_y=dict_y, xlabel="Month", ylabel="Energy (kWh/month)", set_ylim0=True)

    columnsPrint = df_annualAnalysisFilter.drop("dates (Y-M-D hh:mm:ss)", axis=1).columns.tolist()
    general.printData(dataframe=df_annualAnalysisFilter, columns_print=columnsPrint)

    return





