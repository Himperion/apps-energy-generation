# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import io, calendar, yaml
from datetime import datetime

from funtions import fun_app5, fun_app6
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

def get_label_params(dict_param: dict) -> str:

    return f"**{dict_param['label']}:** {dict_param['description']} {dict_param['unit']}"

def getParametersINV_data(INV_data: dict) -> dict:

    if INV_data is not None:
        INV_data['Iac_nom'] = round((INV_data['Pac_max']*1000)/(np.sqrt(dict_phases[INV_data['phases']]['Num'])*INV_data['Vac_nom']), 4)
        INV_data['Rinv'] = round((INV_data['Vac_max'] - INV_data['Vac_nom'])/INV_data['Iac_nom'], 4)

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
        f"Exct1(kWh/{timeLapse}": Eexct1,
        f"Exct2(kWh/{timeLapse}": Eexct2
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





