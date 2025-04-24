# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
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

#%% funtions streamlit


def displayInstantResults(df_data: pd.DataFrame, PARAMS_data: dict, pf_date: datetime.date, pf_time: datetime.time):

    pf_datetime = general.getAnalizeTime(data_date=pf_date, data_time=pf_time)
    df_dataFilter = df_data[df_data["dates (Y-M-D hh:mm:ss)"] == pf_datetime]
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

def printDataFloatResult(df_current: pd.DataFrame, list_drop: list):

    columnsPrint = df_current.drop(list_drop, axis=1).columns.tolist()
    columnsPrintRename = general.fromParametersGetLabels(list_params=columnsPrint)
    dict_replace = {columnsPrint[i]: columnsPrintRename[i] for i in range(0,len(columnsPrint),1)}
    df_current = df_current.rename(columns=dict_replace)

    general.printDataFloat(dataframe=df_current, columns_print=columnsPrintRename, round_int=3)

    return

def displayDailyResults(df_data: pd.DataFrame, df_dailyAnalysis: pd.DataFrame, day):

    time_info ={"name": "Hora", "label": "Hora del día", "strftime": "%H:%M"}
    value_label = "Potencia (kW)"

    df_dailyAnalysisFilter = df_dailyAnalysis[df_dailyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.date == day]
    df_DataDaily = df_data[df_data["dates (Y-M-D hh:mm:ss)"].dt.date == day]
    df_DataDaily = df_DataDaily.copy()
    df_DataDaily.loc[:, "Pgen(kW)"] = df_DataDaily.loc[:, "PinvAC_PV(kW)"] + df_DataDaily.loc[:, "PinvAC_AERO(kW)"]

    df_DataDaily["Exportación (kW)"], df_DataDaily["Importación (kW)"] = 0.0, 0.0
    df_DataDaily.loc[df_DataDaily["Pdem(kW)"] < 0.0, "Exportación (kW)"] = df_DataDaily["Pdem(kW)"]
    df_DataDaily.loc[df_DataDaily["Pdem(kW)"] > 0.0, "Importación (kW)"] = df_DataDaily["Pdem(kW)"]

    df_DataDaily["Excedentes (kW)"] = df_DataDaily["Exportación (kW)"]*(-1)
    df_DataDaily["Autoconsumo (kW)"] = df_DataDaily["Pgen(kW)"] - df_DataDaily["Excedentes (kW)"]

    df_DataDaily[time_info["name"]] = df_DataDaily["dates (Y-M-D hh:mm:ss)"].dt.strftime(time_info["strftime"])

    with st.expander("**Generación diaria**", icon="🍰"):
    
        col1, col2 = st.columns([0.5, 0.5])

        with col1:
            list_params = ["Eauto(kWh/day)", "Eexp(kWh/day)"]
            sizes = general.getSizesForPieChart(df=df_dailyAnalysisFilter, list_params=list_params)
            labels = general.fromParametersGetLabels(list_params)
            legend_title = "Generación:"
            colors = ["magenta", "gold"]
            pull = [0.1, 0]

            general.pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)
            
        with col2:
            list_params = ["Eauto(kWh/day)", "Exct1(kWh/day)", "Exct2(kWh/day)"]
            sizes =  general.getSizesForPieChart(df=df_dailyAnalysisFilter, list_params=list_params)
            labels = general.fromParametersGetLabels(list_params)
            legend_title = "Generación:"
            colors = ["magenta", "turquoise", "violet"]
            pull = [0.1, 0, 0]

            general.pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)
        
    with st.expander("**Atención de la carga**", icon="🍰"):
        list_params = ["Eimp(kWh/day)", "Eauto(kWh/day)"]
        sizes =  general.getSizesForPieChart(df=df_dailyAnalysisFilter, list_params=list_params)
        labels = general.fromParametersGetLabels(list_params)
        legend_title = "Atención:"
        colors = ["purple", "magenta"]
        pull = [0, 0, 0]

        general.pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)

    with st.expander(f"**Interacción entre demanda y generación**", icon="📊"):

        params_info ={
            "Load(kW)": {"label": "Demanda de la carga", "color": "teal"},
            "Pgen(kW)": {"label": "Generación total", "color": "turquoise"}  
        }
        serie_label = "Interacción:"

        general.plotVisualizationPxStreamlit(df_DataDaily, time_info, params_info, value_label, serie_label)

    with st.expander(f"**Producción diaria**", icon="📊"):
        tab1, tab2 = st.tabs(["🍰 Diagrama de torta", "📊 Gráfico de barras"])

        with tab1:
            list_params = ["Egen_INVPV(kWh/day)", "Egen_INVAERO(kWh/day)"]
            sizes =  general.getSizesForPieChart(df=df_dailyAnalysisFilter, list_params=list_params)
            labels = general.fromParametersGetLabels(list_params)
            legend_title = "Fuente de generación:"
            colors=["royalblue", "green"]
            pull = [0.1, 0]

            general.pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)

        with tab2:
            params_info ={
                "PinvAC_PV(kW)": {"label": "Generación fotovoltaica", "color": "royalblue"},
                "PinvAC_AERO(kW)": {"label": "Generación Eólica", "color": "green"}
                }
            serie_label = "Fuente de generación:"

            general.plotVisualizationPxStreamlit(df_DataDaily, time_info, params_info, value_label, serie_label)
            
    with st.expander(f"**Demanda diaria**", icon="📊"):
        
        tab1, tab2 = st.tabs(["🍰 Diagrama de torta", "📊 Gráfico de barras"])

        with tab1:
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                list_params = ["Eimp(kWh/day)", "Eexp(kWh/day)"]
                sizes =  general.getSizesForPieChart(df=df_dailyAnalysisFilter, list_params=list_params)
                labels = general.fromParametersGetLabels(list_params)
                legend_title = "Demanda:"
                colors = ["purple", "gold"]
                pull = [0.1, 0]

                general.pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)

            with col2:
                list_params = ["Eimp(kWh/day)", "Exct1(kWh/day)", "Exct2(kWh/day)"]
                sizes =  general.getSizesForPieChart(df=df_dailyAnalysisFilter, list_params=list_params)
                labels = general.fromParametersGetLabels(list_params)
                legend_title = "Demanda:"
                colors = ["purple", "turquoise", "violet"]
                pull = [0.1, 0, 0]

                general.pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)

        with tab2:
            params_info ={
                "Exportación (kW)": {"label": "Exportación", "color": "gold"},
                "Importación (kW)": {"label": "Importación", "color": "purple"}
                }
            serie_label = "Demanda:"

            general.plotVisualizationPxStreamlit(df_DataDaily, time_info, params_info, value_label, serie_label)

    with st.expander(f"**Generación diaria - Uso**", icon="📊"):
        params_info ={
            "Excedentes (kW)": {"label": "Excedentes", "color": "indigo"},
            "Autoconsumo (kW)": {"label": "Autoconsumo", "color": "navy"}
            }
        serie_label = "Uso:"

        general.plotVisualizationPxStreamlit(df_DataDaily, time_info, params_info, value_label, serie_label)

    with st.expander(f"**Atención de la carga**", icon="📊"):
        
        params_info ={
            "Importación (kW)": {"label": "Importación", "color": "purple"},
            "Autoconsumo (kW)": {"label": "Autoconsumo", "color": "magenta"}
            }
        serie_label = "Atención:"

        general.plotVisualizationPxStreamlit(df_DataDaily, time_info, params_info, value_label, serie_label, barmode="stack", opacity=1)

    list_drop = ["dates (Y-M-D hh:mm:ss)", "Egen_PV(kWh/day)", "Egen_AERO(kWh/day)"]
    printDataFloatResult(df_dailyAnalysisFilter, list_drop)

    return

def displayResult(df_current: pd.DataFrame, df_previus: pd.DataFrame, timeAnalysis: list, time_info: dict, value_label: str):

    with st.expander(f"**Generación {time_info['description']}**", icon="🍰"):
        col1, col2 = st.columns([0.5, 0.5])
        
        with col1:
            list_params = [f"Eauto(kWh/{timeAnalysis[0]})", f"Eexp(kWh/{timeAnalysis[0]})"]
            sizes =  general.getSizesForPieChart(df=df_current, list_params=list_params)
            labels = general.fromParametersGetLabels(list_params)
            legend_title = "Generación:"
            colors = ["magenta", "gold"]
            pull = [0.1, 0]

            general.pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)

        with col2:
            list_params = [f"Eauto(kWh/{timeAnalysis[0]})", f"Exct1(kWh/{timeAnalysis[0]})", f"Exct2(kWh/{timeAnalysis[0]})"]
            sizes =  general.getSizesForPieChart(df=df_current, list_params=list_params)
            labels = general.fromParametersGetLabels(list_params)
            legend_title = "Generación:"
            colors = ["magenta", "turquoise", "violet"]
            pull = [0.1, 0, 0]

            general.pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)

    with st.expander("**Atención de la carga**", icon="🍰"):
        list_params = [f"Eimp(kWh/{timeAnalysis[0]})", f"Eauto(kWh/{timeAnalysis[0]})"]
        sizes =  general.getSizesForPieChart(df=df_current, list_params=list_params)
        labels = general.fromParametersGetLabels(list_params)
        legend_title = "Atención:"
        colors = ["purple", "magenta"]
        pull = [0, 0, 0]

        general.pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)

    with st.expander("**Interacción entre demanda y generación**", icon="📊"):

        params_info ={
            f"Eload(kWh/{timeAnalysis[-1]})": {"label": "Demanda de la carga", "color": "teal"},
            f"Egen(kWh/{timeAnalysis[-1]})": {"label": "Generación", "color": "turquoise"}
            
        }
        serie_label = "Interacción:"

        general.plotVisualizationPxStreamlit(df_previus, time_info, params_info, value_label, serie_label)

    with st.expander(f"**Producción {time_info['description']}**", icon="📊"):
        tab1, tab2 = st.tabs(["🍰 Diagrama de torta", "📊 Gráfico de barras"])
        
        with tab1:
            list_params = [f"Egen_INVPV(kWh/{timeAnalysis[0]})", f"Egen_INVAERO(kWh/{timeAnalysis[0]})"]
            sizes =  general.getSizesForPieChart(df=df_current, list_params=list_params)
            labels = general.fromParametersGetLabels(list_params)
            legend_title = "Fuente de generación:"
            colors=["royalblue", "green"]
            pull = [0.1, 0]

            general.pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)

        with tab2:
            params_info ={
                f"Egen_INVPV(kWh/{timeAnalysis[-1]})": {"label": "Generación fotovoltaica", "color": "royalblue"},
                f"Egen_INVAERO(kWh/{timeAnalysis[-1]})": {"label": "Generación Eólica", "color": "green"}
                }
            serie_label = "Fuente de generación:"

            general.plotVisualizationPxStreamlit(df_previus, time_info, params_info, value_label, serie_label)

    with st.expander(f"**Demanda {time_info['description']}**", icon="📊"):
        tab1, tab2 = st.tabs(["🍰 Diagrama de torta", "📊 Gráfico de barras"])

        with tab1:
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                list_params = [f"Eimp(kWh/{timeAnalysis[0]})", f"Eexp(kWh/{timeAnalysis[0]})"]
                sizes =  general.getSizesForPieChart(df=df_current, list_params=list_params)
                labels = general.fromParametersGetLabels(list_params)
                legend_title = "Demanda:"
                colors = ["purple", "gold"]
                pull = [0.1, 0]

                general.pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)

            with col2:
                list_params = [f"Eimp(kWh/{timeAnalysis[0]})", f"Exct1(kWh/{timeAnalysis[0]})", f"Exct2(kWh/{timeAnalysis[0]})"]
                sizes =  general.getSizesForPieChart(df=df_current, list_params=list_params)
                labels = general.fromParametersGetLabels(list_params)
                legend_title = "Demanda:"
                colors = ["purple", "turquoise", "violet"]
                pull = [0.1, 0, 0]

                general.pieChartVisualizationStreamlit(sizes, labels, legend_title, colors, pull)

        with tab2:
            params_info ={
                f"Eexp(kWh/{timeAnalysis[-1]})": {"label": "Exportación", "color": "gold"},
                f"Eimp(kWh/{timeAnalysis[-1]})": {"label": "Importación", "color": "purple"}
                }
            
            serie_label = "Demanda:"

            general.plotVisualizationPxStreamlit(df_previus, time_info, params_info, value_label, serie_label, barmode="stack", opacity=1)

    with st.expander(f"**Generación {time_info['description']} - Uso**", icon="📊"):
        
        params_info ={
            f"Eexp(kWh/{timeAnalysis[-1]})": {"label": "Excedentes", "color": "indigo"},
            f"Eauto(kWh/{timeAnalysis[-1]})": {"label": "Autoconsumo", "color": "magenta"}
            }
        serie_label = "Uso:"

        general.plotVisualizationPxStreamlit(df_previus, time_info, params_info, value_label, serie_label, barmode="overlay", opacity=0.8)

    with st.expander("**Atención de la carga**", icon="📊"):
        
        params_info ={
            f"Eimp(kWh/{timeAnalysis[-1]})": {"label": "Importación", "color": "purple"},
            f"Eauto(kWh/{timeAnalysis[-1]})": {"label": "Autoconsumo", "color": "magenta"}
            }
        serie_label ="Atención:"

        general.plotVisualizationPxStreamlit(df_previus, time_info, params_info, value_label, serie_label)

    list_drop = ["dates (Y-M-D hh:mm:ss)", f"Egen_PV(kWh/{timeAnalysis[0]})", f"Egen_AERO(kWh/{timeAnalysis[0]})"]
    printDataFloatResult(df_current, list_drop)

    return

def displayMonthlyResults(df_data: pd.DataFrame, df_dailyAnalysis: pd.DataFrame, df_monthlyAnalysis: pd.DataFrame, optionYearRange, optionMonthRange):

    timeAnalysis = ["month", "day"]
    time_info = {"name": "Día", "label": "Día del mes", "strftime": "%d", "description": "mensual"}
    value_label = "Energía (kWh/día)"

    monthIndex = general.fromMonthGetIndex(month=optionMonthRange)
    df_current = df_monthlyAnalysis[(df_monthlyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.year == optionYearRange) & (df_monthlyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.month == monthIndex)]
    df_previus = df_dailyAnalysis[(df_dailyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.year == optionYearRange) & (df_dailyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.month == monthIndex)]

    df_previus[time_info["name"]] = df_previus["dates (Y-M-D hh:mm:ss)"].dt.strftime(time_info["strftime"])

    displayResult(df_current, df_previus, timeAnalysis, time_info, value_label)

    return

def displayAnnualResults(df_monthlyAnalysis: pd.DataFrame, df_annualAnalysis: pd.DataFrame, optionYearRange):

    timeAnalysis = ["year", "month"]
    time_info = {"name": "Mes", "label": "Mes del año", "strftime": "%m", "description": "anual"}
    value_label = "Energía (kWh/mes)"
    
    df_current = df_annualAnalysis[df_annualAnalysis["dates (Y-M-D hh:mm:ss)"].dt.year == optionYearRange]
    df_previus = df_monthlyAnalysis[df_monthlyAnalysis["dates (Y-M-D hh:mm:ss)"].dt.year == optionYearRange]

    df_previus[time_info["name"]] = df_previus["dates (Y-M-D hh:mm:ss)"].dt.strftime(time_info["strftime"])

    displayResult(df_current, df_previus, timeAnalysis, time_info, value_label)

    return
