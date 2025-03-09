# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import yaml, io, warnings
from datetime import datetime

from funtions import fun_app5, fun_app6, fun_app7

optKeysPV = [
    "alpha_sc",
    "beta_voc",
    "cells_in_series",
    "celltype",
    "gamma_pmp",
    "i_mp",
    "i_sc",
    "v_mp",
    "v_oc"
]

optKeysAERO = [
    "D",
    "V_in",
    "V_nom",
    "V_max",
    "P_nom"
]

optKeysINVCOMP = [
    "Pac_max",
    "Vac_max",
    "Vac_min",
    "Vac_nom",
    "Vbb_nom",
    "efficiency_max",
    "grid_type",
    "phases"
]

optKeysRCCOMP = [
    "SOC_0",
    "SOC_ETP1",
    "SOC_ETP2",
    "SOC_conx",
    "SOC_max",
    "SOC_min",
    "Vdc_bb",
    "rc_efficiency"
]

optKeysGE = [
    "C0",
    "C100",
    "Combustible",
    "FP",
    "PE_fuel",
    "Pnom",
    "Voc",
    "Vpc",
    "phases"
]

optKeysBAT = [
    "C",
    "DOD",
    "I_min",
    "I_max",
    "V_max",
    "V_min",
    "V_nom",
    "bat_type",
    "bat_efficiency"
]

dict_phases = {
    "Monofásico": {"Num": 1, "label": "1️⃣ Monofásico"},
    "Trifásico": {"Num": 3, "label": "3️⃣ Trifásico"}
}

#%% equations


#%% funtions general

def name_file_head(name: str) -> str:
    now = datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def get_bytes_yaml(dictionary: dict):

    yaml_data = yaml.dump(dictionary, allow_unicode=True)

    buffer = io.BytesIO()
    buffer.write(yaml_data.encode('utf-8'))
    buffer.seek(0)

    return buffer

def getGlobalVariablesPV():
    params_PV, rename_PV, showOutputPV = None, None, None

    with open("files//[PV] - params.yaml", 'r') as archivo:
        params_PV = yaml.safe_load(archivo)

    with open("files//[PV] - dict_replace.yaml", 'r') as archivo:
        rename_PV = yaml.safe_load(archivo)

    if params_PV is not None:
        showOutputPV = [f"{params_PV[elm]['label']}{params_PV[elm]['unit']}: {params_PV[elm]['description']}" for elm in ["Voc", "Isc", "Impp", "Vmpp", "Pmpp"]]

    return params_PV, rename_PV, showOutputPV

def toExcelResults(df: pd.DataFrame, dictionary: dict | None, df_sheetName: str, dict_sheetName: str | None) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=df_sheetName)
        if dictionary is not None:
            df_params = pd.DataFrame(dictionary, index=[0])
            df_params.to_excel(writer, index=False, sheet_name=dict_sheetName)

    return output.getvalue()

def fixDictColumnsOptionsData(columnsOptionsData: dict) -> dict:

    listUniqueKeys, dictOut= [], {}

    for key in columnsOptionsData:
        newKey = key.split("-")[0]
        if not newKey in listUniqueKeys:
            listUniqueKeys.append(newKey)

    for i in range(0,len(listUniqueKeys),1):
        dictAux = {}
        for key, value in columnsOptionsData.items():
            if key.split("-")[0] == listUniqueKeys[i]:
                dictAux[key.split("-")[1]] = value

        dictOut[listUniqueKeys[i]] = dictAux

    return dictOut

def consolidationOfKeyIntoList(DICT_data: dict):

    dictAux, listUniqueKeys, listUniqueValues = {}, [], []

    for key, value in DICT_data.items():
        if key.count("-") == 1:
            if key.split("-")[1].isdigit():
                dictAux[key] = value
                if not key.split("-")[0] in listUniqueKeys:
                    listUniqueKeys.append(key.split("-")[0])

    for i in range(0,len(listUniqueKeys),1):
        listAux = []
        for key, value in dictAux.items():
            if key.split("-")[0] == listUniqueKeys[i]:
                listAux.append(value)
        listUniqueValues.append(listAux)

    if len(listUniqueKeys) > 0 and len(listUniqueKeys) == len(listUniqueValues):
        for i in range(0,len(listUniqueKeys),1):
            DICT_data[listUniqueKeys[i]] = listUniqueValues[i]

    for key in dictAux:
        if key in DICT_data:
            del DICT_data[key]
                
    return DICT_data

def getFixFormatDictParams(TOTAL_data: dict):

    listCheckKeys = ["PV_data", "INVPV_data", "RCPV_data", "AERO_data", "INVAERO_data", "RCAERO_data",
                     "BAT_data", "GE_data", "rho", "PVs", "PVp", "Ns_BAT", "Np_BAT",
                     "columnsOptionsData", "numberPhases", "validateEntries", "componentInTheProject"]
                                    
    listUniqueKeys, listLonelyKeys, dictOut = [], [], {}

    for key in TOTAL_data:
        if (key.count("[") > 0) and (key.count("]") > 0):
            newKey = key[:key.find("]")+1][1:-1]
            if not newKey in listUniqueKeys:
                listUniqueKeys.append(newKey)
        else:
            listLonelyKeys.append(key)

    for i in range(0,len(listUniqueKeys),1):
        dictAux = {}
        for key, value in TOTAL_data.items():
            if (key.count("[") > 0) and (key.count("]") > 0):
                if key[:key.find("]")+1][1:-1] == listUniqueKeys[i]:
                    dictAux[key.split(" ")[1]] = value

        dictOut[listUniqueKeys[i]] = dictAux

    for i in range(0,len(listLonelyKeys),1):
        dictOut[listLonelyKeys[i]] = TOTAL_data[listLonelyKeys[i]]
                    
    if "columnsOptionsData" in dictOut:
        columnsOptionsData = fixDictColumnsOptionsData(columnsOptionsData=dictOut["columnsOptionsData"])
        dictOut["columnsOptionsData"] = columnsOptionsData

    for i in range(0,len(listCheckKeys),1):
        if not listCheckKeys[i] in dictOut:
            dictOut[listCheckKeys[i]] = None

    for key, value in dictOut.items():
        if type(value) is dict:
            value = consolidationOfKeyIntoList(DICT_data=value)

    return dictOut

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

def check_dict_input(dictionary: dict, options) -> bool:

    return all([key in options for key in dictionary])

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

        listAuxMonth = []
        for year in timeInfo["years"]:
            df_year = df_data[df_data["dates (Y-M-D hh:mm:ss)"].dt.year == year]

            list_month = df_year["dates (Y-M-D hh:mm:ss)"].dt.month.unique().tolist()
            listAuxMonth.append(list_month)

        timeInfo["months"] = listAuxMonth

    return timeInfo

def getNumberPhasesOffGrid(INVPV_data, INVAERO_data, GE_data):

    numberPhases = None

    if INVPV_data is not None and INVAERO_data is None:
        numberPhases = dict_phases[INVPV_data['phases']]['Num']
    elif INVPV_data is None and INVAERO_data is not None:
        numberPhases = dict_phases[INVAERO_data['phases']]['Num']
    else:
        numberPhasesPV = dict_phases[INVPV_data['phases']]['Num']
        numberPhasesAERO = dict_phases[INVAERO_data['phases']]['Num']

        if numberPhasesPV == numberPhasesAERO:
            numberPhases = numberPhasesPV

    if GE_data is not None and numberPhases is not None:
        numberPhasesGE = dict_phases[GE_data['phases']]['Num']

        if numberPhases != numberPhasesGE:
            numberPhases = None
        
    return numberPhases

def getDataframePV(df_data: pd.DataFrame, PV_data: dict, INVPV_data: dict, PVs: int, PVp: int, columnsOptionsData: list, params_PV: dict, rename_PV: dict, showOutputPV: list, numberPhases: int):

    conditions = fun_app5.get_dataframe_conditions(df_data, columnsOptionsData["PV"])
    PV_params = fun_app5.get_PV_params(**PV_data)
    dict_replace = fun_app5.get_dict_replace(dict_rename=rename_PV, dict_params=params_PV)

    df_pv = fun_app5.get_singlediode(conditions, PV_params, PVs, PVp)
    df_pv = fun_app5.get_final_dataframe(df_pv=df_pv,
                                         df_input=df_data,
                                         dict_replace=dict_replace,
                                         dict_conditions=columnsOptionsData["PV"],
                                         list_output=showOutputPV)
    
    df_pv["Pgen_PV(kW)"] = df_pv["Pmpp(kW)"]
    df_pv.rename(columns={"Voc(V)": "Voc_PV(V)", "Isc(A)": "Isc_PV(A)", "Impp(A)": "Impp_PV(A)", "Vmpp(V)": "Vmpp_PV(V)"}, inplace=True)

    return df_pv

def getDataframeAERO(df_data: pd.DataFrame, AERO_data: dict, INVAERO_data: dict, rho, columnsOptionsData: list):

    df_AERO = fun_app6.get_dataframe_power_wind_turbine(params=AERO_data,
                                                        rho=rho,
                                                        dataframe=df_data,
                                                        column=columnsOptionsData["AERO"])

    return df_AERO

def getPerUnitSystem(Pac_nom: float, Vac_nom: float, numberPhases: int):

    Sb = Pac_nom
    Vb = Vac_nom
    Ib = (Pac_nom*1000)/(np.sqrt(numberPhases)*Vac_nom)
    Zb = Vb/Ib

    return Sb, Vb, Ib, Zb

def getGlobalPerUnitSystem(INVPV_data: dict, INVAERO_data: dict, numberPhases: int, generationPV: bool, generationAERO: bool):

    if generationPV and not generationAERO:
        Pac_nom, Vac_nom = INVPV_data["Pac_max"], INVPV_data["Vac_nom"]
    elif not generationPV and generationAERO:
        Pac_nom, Vac_nom = INVAERO_data["Pac_max"], INVAERO_data["Vac_nom"]
    else:
        Pac_nom, Vac_nom = INVPV_data["Pac_max"], INVPV_data["Vac_nom"]

    return getPerUnitSystem(Pac_nom=Pac_nom, Vac_nom=Vac_nom, numberPhases=numberPhases)

def getListChargeRegulatorData(RCPV_data: dict, RCAERO_data: dict, generationPV: bool, generationAERO: bool):

    listLabelParams = ["SOC_0", "SOC_conx", "SOC_max", "SOC_min", "SOC_ETP1", "SOC_ETP2"]
    listOut = []

    for i in range(0,len(listLabelParams),1):
        if generationPV and generationAERO:             # generación solar y eólica
            listOut.append(RCPV_data[listLabelParams[i]])
        elif generationPV and not generationAERO:       # generación solar
            listOut.append(RCPV_data[listLabelParams[i]])
        elif not generationPV and generationAERO:       # generación eólica
            listOut.append(RCAERO_data[listLabelParams[i]])
           
    return listOut

def getInverterParameters(INV_data: dict, numberPhases: int, Sb: float, Vb: float, Ib: float, Zb: float, generationTYPE: bool):

    if generationTYPE:
        Iac_nom = (INV_data["Pac_max"]*1000)/(np.sqrt(numberPhases)*INV_data["Vac_nom"])

        VocPU = INV_data["Vac_max"]/Vb
        VnomPU = INV_data["Vac_nom"]/Vb
        PnomPU = INV_data["Pac_max"]/Sb
        InomPU = Iac_nom/Ib
        RinvPU = (VocPU - VnomPU)/InomPU

        n_InvCOMP = INV_data["efficiency_max"]/100
    else:
        VocPU, VnomPU, PnomPU, InomPU, RinvPU, n_InvCOMP = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0


    return VocPU, VnomPU, PnomPU, InomPU, RinvPU, n_InvCOMP

def getChargeRegulatorParameters(RC_data: dict, generationTYPE: bool):

    if generationTYPE:
        n_RcCOMP = RC_data["rc_efficiency"]/100
    else:
        n_RcCOMP = 0.0

    return n_RcCOMP

def getBatteryBankParameters(C: float, I_max: float, I_min: float, V_max: float, V_min: float, V_nom: float, Ns: int, Np: int, SOC_ETP1: float, SOC_ETP2: float):

    Ebb_nom = ((C*V_nom)/1000)*(Ns*Np)
    Vbb_max = V_max*Ns
    Vbb_min = V_min*Ns
    Ibb_max = I_max*Np
    Ibb_min = I_min*Np
    m_ETP2 = (Ibb_max - Ibb_min)/(SOC_ETP1 - SOC_ETP2)
    b_ETP2 = Ibb_max - m_ETP2*SOC_ETP1

    return Ebb_nom, Vbb_max, Vbb_min, Ibb_max, Ibb_min, m_ETP2, b_ETP2

def getRootsQuadraticEcuation(a: float, b: float, c: float):

    try:
        discri = np.sqrt((b**2)-4*a*c)
    except:
        print(a, b, c)

    x1 = (-b + np.sqrt((b**2)-4*a*c))/(2*a)
    x2 = (-b - np.sqrt((b**2)-4*a*c))/(2*a)

    return x1, x2

def getVloadPU(VocPU_PV, RinvPU_PV, VocPU_AERO, RinvPU_AERO, Pload_PU, componentInTheProject):

    if componentInTheProject["generationPV"] and not componentInTheProject["generationAERO"]:
        a = 1
        b = -VocPU_PV
        c = RinvPU_PV*Pload_PU
    elif not componentInTheProject["generationPV"] and componentInTheProject["generationAERO"]:
        a = 1
        b = -VocPU_AERO
        c = RinvPU_AERO*Pload_PU
    elif componentInTheProject["generationPV"] and componentInTheProject["generationAERO"]:
        a = RinvPU_PV + RinvPU_AERO
        b = -(RinvPU_AERO*VocPU_PV + RinvPU_PV*VocPU_AERO)
        c = RinvPU_PV*RinvPU_AERO*Pload_PU

    x1, x2 = getRootsQuadraticEcuation(a, b, c)

    return [x1, x2]

def getIinvPU(VocPU_PV, RinvPU_PV, VocPU_AERO, RinvPU_AERO, VloadPU, componentInTheProject):

    IinvPU_PV, IinvPU_AERO = 0.0, 0.0

    if componentInTheProject["generationPV"]:
        IinvPU_PV = (VocPU_PV - VloadPU)/RinvPU_PV
    if componentInTheProject["generationAERO"]:
        IinvPU_AERO = (VocPU_AERO - VloadPU)/RinvPU_AERO

    return IinvPU_PV, IinvPU_AERO
    
def getPinvCOMP_DC(PinvPV_PU, PinvAERO_PU, n_InvPV, n_InvAERO, Sb, componentInTheProject):

    PinvPV_DC, PinvAERO_DC = 0.0, 0.0

    if componentInTheProject["generationPV"]:
        PinvPV_DC = (PinvPV_PU/n_InvPV)*Sb
    if componentInTheProject["generationAERO"]:
        PinvAERO_DC = (PinvAERO_PU/n_InvAERO)*Sb

    return PinvPV_DC, PinvAERO_DC

def getBatteryCalculations(df_grid: pd.DataFrame, BAT_data: dict,
                           RCPV_data: dict, INVPV_data: dict,
                           RCAERO_data: dict, INVAERO_data: dict,
                           Ns_BAT: int, Np_BAT: int,
                           numberPhases: int,
                           Sb: float, Vb: float, Ib: float, Zb: float,
                           columnsOptionsData: dict,
                           componentInTheProject: dict):
    
    timeInfo = getTimeData(df_grid)
    SOC_0, SOC_conx, SOC_max, SOC_min, SOC_ETP1, SOC_ETP2,  = getListChargeRegulatorData(RCPV_data, RCAERO_data, componentInTheProject["generationPV"], componentInTheProject["generationAERO"])
    VocPU_PV, VnomPU_PV, PnomPU_PV, InomPU_PV, RinvPU_PV, n_InvPV = getInverterParameters(INVPV_data, numberPhases, Sb, Vb, Ib, Zb, componentInTheProject["generationPV"])
    VocPU_AERO, VnomPU_AERO, PnomPU_AERO, InomPU_AERO, RinvPU_AERO, n_InvAERO = getInverterParameters(INVAERO_data, numberPhases, Sb, Vb, Ib, Zb, componentInTheProject["generationAERO"])
    n_RcPV = getChargeRegulatorParameters(RCPV_data, componentInTheProject["generationPV"])
    n_RcAERO = getChargeRegulatorParameters(RCAERO_data, componentInTheProject["generationAERO"])
    
    delta_t = timeInfo["deltaMinutes"]/60
    n_bat = BAT_data["bat_efficiency"]/100

    st.text(f"n_RcPV: {n_RcPV}")
    st.text(f"n_RcAERO: {n_RcAERO}")
    st.text(f"n_InvPV: {n_InvPV}")
    st.text(f"n_InvAERO: {n_InvAERO}")
    
    Ebb_nom, Vbb_max, Vbb_min, Ibb_max, Ibb_min, m_ETP2, b_ETP2 = getBatteryBankParameters(C=BAT_data["C"],
                                                                                           I_max=BAT_data["I_max"],
                                                                                           I_min=BAT_data["I_min"],
                                                                                           V_max=BAT_data["V_max"],
                                                                                           V_min=BAT_data["V_min"],
                                                                                           V_nom=BAT_data["V_nom"],
                                                                                           Ns=Ns_BAT, Np=Np_BAT,
                                                                                           SOC_ETP1=SOC_ETP1, SOC_ETP2=SOC_ETP2)

    df_grid["Pbb(kW)"] = 0.0
    df_grid["Vbb(V)"] = 0.0
    df_grid["Ibb(A)"] = 0.0
    df_grid["IbbDC_PV(A)"] = 0.0
    df_grid["IbbDC_AERO(A)"] = 0.0
    
    df_grid["PrcDC_PV(kW)"] = 0.0
    df_grid["VrcDC_PV(V)"] = 0.0
    df_grid["IrcDC_PV(A)"] = 0.0

    df_grid["PrcDC_AERO(kW)"] = 0.0
    df_grid["VrcDC_AERO(V)"] = 0.0
    df_grid["IrcDC_AERO(A)"] = 0.0
    
    df_grid["PinvDC_PV(kW)"] = 0.0
    df_grid["VinvDC_PV(V)"] = 0.0
    df_grid["IinvDC_PV(A)"] = 0.0

    df_grid["PinvDC_AERO(kW)"] = 0.0
    df_grid["VinvDC_AERO(V)"] = 0.0
    df_grid["IinvDC_AERO(A)"] = 0.0

    df_grid["PinvAC_PV(kW)"] = 0.0
    df_grid["VinvAC_PV(V)"] = 0.0
    df_grid["IinvAC_PV(A)"] = 0.0

    df_grid["PinvAC_AERO(kW)"] = 0.0
    df_grid["VinvAC_AERO(V)"] = 0.0
    df_grid["IinvAC_AERO(A)"] = 0.0
    
    df_grid["conSD(t)"] = False
    df_grid["conSC(t)"] = False
    df_grid["swLoad(t)"] = 1

    df_grid["deltaEbb(kWh)"] = 0.0
    df_grid["Ebb(kWh)"] = 0.0
    df_grid["SOC(t)"] = 0.0
    df_grid["DOD(t)"] = 0.0

    df_grid["NodoTotal"] = 0.0
    df_grid["Nodo1"] = 0.0
    df_grid["Nodo2"] = 0.0
    df_grid["Nodo3"] = 0.0
    df_grid["Nodo4"] = 0.0

    for index, row in df_grid.iterrows():
        Pload_PU = df_grid.loc[index, columnsOptionsData["DATA"]["Load"]]/Sb
        Vload_PU = getVloadPU(VocPU_PV, RinvPU_PV, VocPU_AERO, RinvPU_AERO, Pload_PU, componentInTheProject)[0]
        Iload_PU = Pload_PU/Vload_PU
        IinvAC_PV_PU, IinvAC_AERO_PU = getIinvPU(VocPU_PV, RinvPU_PV, VocPU_AERO, RinvPU_AERO, Vload_PU, componentInTheProject)
        PinvAC_PV_PU, PinvAC_AERO_PU = Vload_PU*IinvAC_PV_PU, Vload_PU*IinvAC_AERO_PU
        PinvDC_PV, PinvDC_AERO = getPinvCOMP_DC(PinvAC_PV_PU, PinvAC_AERO_PU, n_InvPV, n_InvAERO, Sb, componentInTheProject)

        Pgen_PV = df_grid.loc[index, "Pgen_PV(kW)"]
        Pgen_AERO = df_grid.loc[index, "Pgen_AERO(kW)"]

        # valores anteriores t-1
        if index == 0: 
            SOC_t_1, swLoad_t_1 = SOC_0, 1
        else:
            SOC_t_1, swLoad_t_1 = df_grid.loc[index-1, "SOC(t)"], df_grid.loc[index-1, "swLoad(t)"]

        # condición sobreCarga (Limitar la generación al igualarla a la demanda)
        if SOC_t_1 >= SOC_max and (n_RcPV*Pgen_PV + n_RcAERO*Pgen_AERO) >= (PinvDC_PV + PinvDC_AERO) and swLoad_t_1 == 1:
            PrcDC_PV = PinvDC_PV
            PrcDC_AERO = PinvDC_AERO
            conSC = True
        else:
            PrcDC_PV = n_RcPV*Pgen_PV
            PrcDC_AERO = n_RcAERO*Pgen_AERO
            conSC = False

        # condición sobreDescarga (Desconectar la carga e iniciar proceso de carga del banco de baterías)
        if SOC_t_1 <= SOC_min and (n_RcPV*Pgen_PV + n_RcAERO*Pgen_AERO) < (PinvDC_PV + PinvDC_AERO):
            conSD = True
        else:
            conSD = False
        
        # condición de conexión de carga (Reconectar la carga cuando se alcance el SOC_conx)
        if conSD and swLoad_t_1 == 1:
            if componentInTheProject["generationGE"]:
                swLoad = 3
            else:
                swLoad = 2
        else:
            if SOC_t_1 >= SOC_conx and swLoad_t_1 != 1:
                swLoad = 1
            else:
                swLoad = swLoad_t_1

        # Carga desconectada
        if swLoad != 1:
            PinvAC_PV_PU = 0.0
            PinvAC_AERO_PU = 0.0
            PinvDC_PV = 0.0
            PinvDC_AERO = 0.0

        # Potencia del banco de baterías Pbb
        #Pbb = (PrcDC_PV + PrcDC_AERO) - (PinvDC_PV + PinvDC_AERO)
        Pbb_PV = PrcDC_PV - PinvDC_PV
        Pbb_AERO = PrcDC_AERO - PinvDC_AERO
        Pbb = Pbb_PV + Pbb_AERO
        
        # deltaEbb
        if Pbb >= 0:    
            deltaEbb = Pbb*n_bat*delta_t
        else:
            deltaEbb = Pbb*(1/n_bat)*delta_t

        # SOC(t), DOD(t), Ebb(kWh), Vbb(V), Ibb(A)
        SOC = SOC_t_1 + (deltaEbb/Ebb_nom)
        DOD = 1 - SOC
        Ebb = SOC_t_1*Ebb_nom + deltaEbb
        Vbb = (Vbb_max - Vbb_min)*SOC + Vbb_min
        Ibb = (Pbb*1000)/Vbb
        Ibb_PV = (Pbb_PV*1000)/Vbb
        Ibb_AERO = (Pbb_AERO*1000)/Vbb

        # condición ETP1
        if swLoad == 2 and SOC_ETP1 <= SOC_t_1:
            I_ETP1, V_ETP1 = Ibb_max, Vbb
        else:
            I_ETP1, V_ETP1  = 0.0, 0.0

        # condición ETP2
        if swLoad == 2 and SOC_ETP1 < SOC_t_1 and SOC_ETP2 < SOC_t_1:
            I_ETP2 = (m_ETP2*SOC_t_1) + b_ETP2
            V_ETP2 = (Vbb_max - Vbb_min)*SOC_ETP1 + Vbb_min
        else:
            I_ETP2 = 0
            V_ETP2 = 0

        # Parametros AC
        PinvAC_PV, VinvAC_PV, IinvAC_PV = PinvAC_PV_PU*Sb, Vload_PU*Vb, IinvAC_PV_PU*Ib
        PinvAC_AERO, VinvAC_AERO, IinvAC_AERO = PinvAC_AERO_PU*Sb, Vload_PU*Vb, IinvAC_AERO_PU*Ib
        Vload = Vload_PU*Vb
        Iload = Iload_PU*Ib

        # Parametros DC
        IrcDC_PV = (n_RcPV*Pgen_PV*1000)/Vbb
        IrcDC_AERO = (n_RcPV*Pgen_PV*1000)/Vbb
        IinvDC_PV = (PinvDC_PV*1000)/Vbb
        IinvDC_AERO = (PinvDC_AERO*1000)/Vbb

        # Actualizar datos
        df_grid.loc[index, "Pbb(kW)"] = Pbb
        df_grid.loc[index, "Vbb(V)"] = Vbb
        df_grid.loc[index, "Ibb(A)"] = Ibb
        df_grid.loc[index, "IbbDC_PV(A)"] = Ibb_PV
        df_grid.loc[index, "IbbDC_AERO(A)"] = Ibb_AERO
    

        df_grid.loc[index, "PrcDC_PV(kW)"] = n_RcPV*Pgen_PV
        df_grid.loc[index, "VrcDC_PV(V)"] = Vbb
        df_grid.loc[index, "IrcDC_PV(A)"] = IrcDC_PV

        df_grid.loc[index, "PrcDC_AERO(kW)"] = n_RcPV*Pgen_AERO
        df_grid.loc[index, "VrcDC_AERO(V)"] = Vbb
        df_grid.loc[index, "IrcDC_AERO(A)"] = IrcDC_AERO
        
        df_grid.loc[index, "PinvDC_PV(kW)"] = PinvDC_PV
        df_grid.loc[index, "VinvDC_PV(V)"] = Vbb
        df_grid.loc[index, "IinvDC_PV(A)"] = IinvDC_PV

        df_grid.loc[index, "PinvDC_AERO(kW)"] = PinvDC_AERO
        df_grid.loc[index, "VinvDC_AERO(V)"] = Vbb
        df_grid.loc[index, "IinvDC_AERO(A)"] = IinvDC_AERO

        df_grid.loc[index, "PinvAC_PV(kW)"] = PinvAC_PV
        df_grid.loc[index, "VinvAC_PV(V)"] = VinvAC_PV
        df_grid.loc[index, "IinvAC_PV(A)"] = IinvAC_PV

        df_grid.loc[index, "PinvAC_AERO(kW)"] = PinvAC_AERO
        df_grid.loc[index, "VinvAC_AERO(V)"] = VinvAC_AERO
        df_grid.loc[index, "IinvAC_AERO(A)"] = IinvAC_AERO
        
        df_grid.loc[index, "conSD(t)"] = conSD
        df_grid.loc[index, "conSC(t)"] = conSC
        df_grid.loc[index, "swLoad(t)"] = swLoad

        df_grid.loc[index, "deltaEbb(kWh)"] = deltaEbb
        df_grid.loc[index, "Ebb(kWh)"] = Ebb
        df_grid.loc[index, "SOC(t)"] = SOC
        df_grid.loc[index, "DOD(t)"] = DOD

        # Pruebas
        
        df_grid.loc[index, "NodoTotal"] = PrcDC_PV + PrcDC_AERO - Pbb - PinvDC_PV - PinvDC_AERO
        df_grid.loc[index, "Nodo1"] = PrcDC_PV - PinvDC_PV - Pbb_PV
        df_grid.loc[index, "Nodo2"] = PrcDC_AERO - PinvDC_AERO - Pbb_AERO
        df_grid.loc[index, "Nodo3"] = Ibb - (Ibb_PV + Ibb_AERO)
        df_grid.loc[index, "Nodo4"] = (Pbb_PV + Pbb_AERO) - Pbb
    
    return df_grid

def initializeDictValidateEntries():

    validateEntries = {
                    "check_DATA": False,
                    "check_PV": False,
                    "check_INVPV": False,
                    "check_RCPV": False,
                    "check_AERO": False,
                    "check_INVAERO": False,
                    "check_RCAERO": False,
                    "check_BAT": False,
                    "check_GE": False
                }

    return validateEntries

def getDictValidateComponent(validateEntries: dict) -> dict:

    validateComponents = {}

    validateComponents["validateDATA"] = validateEntries["check_DATA"]
    validateComponents["validatePV"] = all([validateEntries["check_PV"], validateEntries["check_INVPV"], validateEntries["check_RCPV"]])
    validateComponents["validateAERO"] = all([validateEntries["check_AERO"], validateEntries["check_INVAERO"], validateEntries["check_RCAERO"]])
    validateComponents["validateGE"] = validateEntries["check_GE"]
    validateComponents["validateBAT"] = validateEntries["check_BAT"]

    return validateComponents

def getDictComponentInTheProject(generationOptions: list, listGenerationOptions: list) -> dict:

    componentInTheProject = {
        "generationPV": listGenerationOptions[0] in generationOptions,
        "generationAERO": listGenerationOptions[1] in generationOptions,
        "generationGE": listGenerationOptions[2] in generationOptions,
    }

    return componentInTheProject

def getCheckValidateGeneration(generationPV, generationAERO, generationGE, validateDATA, validatePV, validateAERO, validateGE, validateBAT):

    checkProject = False

    # Solo generación solar
    if generationPV and not generationAERO and validatePV and validateBAT:
        checkProject = True
    # Solo generación eólica
    elif not generationPV and generationAERO and validateAERO and validateBAT:
        checkProject = True
    # Generación solar  y eólica
    elif generationPV and generationAERO and validatePV and validateAERO and validateBAT:
        checkProject = True

    # Respaldo grupo electrógeno
    if generationGE:
        checkProject = checkProject and validateGE
    else:
        checkProject = checkProject and not validateGE

    checkProject = checkProject and validateDATA

    return checkProject

def validateCompatibilityOfCOMP_BAT(RCCOMP_data, Vnom_bb):

    list_VdcBB, listAuxVnBB = RCCOMP_data["Vdc_bb"], []

    for i in range(0,len(list_VdcBB),1):
        listAuxVnBB.append(list_VdcBB[i] == Vnom_bb)

    return any(listAuxVnBB)

def getCompatibilityBAT(RCPV_data, RCAERO_data, BAT_data, Ns_BAT, generationPV, generationAERO) -> bool:

    Vnom_bb = Ns_BAT*BAT_data["V_nom"]
    outCheck = False

    if generationPV and not generationAERO:         # Solo generación solar
        outCheck = validateCompatibilityOfCOMP_BAT(RCPV_data, Vnom_bb)

    elif not generationPV and generationAERO:       # Solo generación eólica
        outCheck = validateCompatibilityOfCOMP_BAT(RCAERO_data, Vnom_bb)

    elif generationPV and generationAERO:           # Generación solar  y eólica
        outCheckPV = validateCompatibilityOfCOMP_BAT(RCPV_data, Vnom_bb)
        outCheckAERO = validateCompatibilityOfCOMP_BAT(RCAERO_data, Vnom_bb)
        outCheck = outCheckPV and outCheckAERO

    return outCheck

def getDataframeGE(df_data: pd.DataFrame, GE_data: dict, columnsOptionsData) -> pd.DataFrame:

    In_GE, Ra_GE, GE_dictPU = fun_app7.get_param_gp(GE_data, dict_phases)

    optionsList = {"Load": [columnsOptionsData["DATA"]["Load"]]}

    df_data, check, columnsOptionsSel = fun_app7.check_dataframe_input(dataframe=df_data,
                                                                       options=optionsList)
    
    df_data = fun_app7.getDataframeGE(dataframe=df_data,
                                      dict_pu=GE_dictPU,
                                      dict_param=GE_data,
                                      columnsOptionsSel={"Load": columnsOptionsData["DATA"]["Load"]})

    return df_data

def generationOffGrid(df_data: pd.DataFrame,
                      PV_data: dict| None,
                      INVPV_data: dict | None,
                      RCPV_data: dict | None,
                      AERO_data: dict | None,
                      INVAERO_data: dict | None,
                      RCAERO_data: dict | None,
                      BAT_data: dict | None,
                      GE_data: dict | None,
                      rho: float | None,
                      PVs: int | None,
                      PVp: int | None,
                      Ns_BAT: int | None,
                      Np_BAT: int | None,
                      columnsOptionsData: list,
                      numberPhases: int,
                      validateEntries: dict,
                      componentInTheProject: dict) -> pd.DataFrame:
    
    params_PV, rename_PV, showOutputPV =  getGlobalVariablesPV()
    Sb, Vb, Ib, Zb = getGlobalPerUnitSystem(INVPV_data, INVAERO_data, numberPhases, componentInTheProject["generationPV"], componentInTheProject["generationAERO"])

    df_offGrid = df_data.copy()
    df_offGrid["Pgen_PV(kW)"] = 0.0
    df_offGrid["Pgen_AERO(kW)"] = 0.0

    if componentInTheProject["generationPV"]:       # PV
        df_offGrid = getDataframePV(df_offGrid, PV_data, INVPV_data, PVs, PVp, columnsOptionsData, params_PV, rename_PV, showOutputPV, numberPhases)

    if componentInTheProject["generationAERO"]:     # AERO
        df_offGrid = getDataframeAERO(df_offGrid, AERO_data, INVAERO_data, rho, columnsOptionsData)

    df_offGrid = getBatteryCalculations(df_grid=df_offGrid,
                                        BAT_data=BAT_data,
                                        RCPV_data=RCPV_data,
                                        INVPV_data=INVPV_data,
                                        RCAERO_data=RCAERO_data,
                                        INVAERO_data=INVAERO_data,
                                        Ns_BAT=Ns_BAT, Np_BAT=Np_BAT,
                                        numberPhases=numberPhases,
                                        Sb=Sb, Vb=Vb, Ib=Ib, Zb=Zb,
                                        columnsOptionsData=columnsOptionsData,
                                        componentInTheProject=componentInTheProject)

    if componentInTheProject["generationGE"]:       # GE
        df_offGrid = getDataframeGE(df_offGrid, GE_data, columnsOptionsData)
        
    
    
    bytesFileExcel = toExcelResults(df=df_offGrid, dictionary=None, df_sheetName="Prueba", dict_sheetName=None)
    botonOut = excelDownloadButton(bytesFileExcel, "prueba")

    

    return

def getAddUniqueColumnsOptionsData(TOTAL_data: dict, columnsOptionsData: dict):

    for key, value in columnsOptionsData.items():
        for subKey, subValue in value.items():
            TOTAL_data[f"[columnsOptionsData] {key}-{subKey}"] = subValue

    return TOTAL_data

def getImputProcessComponentData(dictImput: dict) -> dict:

    dictOutput = {
        "PV_data": dictImput["PV_data"],
        "INVPV_data": dictImput["INVPV_data"],
        "RCPV_data": dictImput["RCPV_data"],
        "AERO_data": dictImput["AERO_data"],
        "INVAERO_data": dictImput["INVAERO_data"],
        "RCAERO_data": dictImput["RCAERO_data"],
        "BAT_data": dictImput["BAT_data"],
        "GE_data": dictImput["GE_data"],
        "rho": dictImput["rho"],
        "PVs": dictImput["PVs"],
        "PVp": dictImput["PVp"],
        "Ns_BAT": dictImput["Ns_BAT"],
        "Np_BAT": dictImput["Np_BAT"],
        "columnsOptionsData": dictImput["columnsOptionsData"],
        "numberPhases": dictImput["numberPhases"],
        "validateEntries": dictImput["validateEntries"],
        "componentInTheProject": dictImput["componentInTheProject"],
    }

    return dictOutput

def proccesComponentData(TOTAL_data: dict, COMP_data: dict, INV_data: dict, RC_data: dict, AddText: str):

    auxListString1 = ["{0}_data", "INV{0}_data", "RC{0}_data"]
    auxListDict = [COMP_data, INV_data, RC_data]

    for i in range(0,len(auxListString1),1):
        textAux = auxListString1[i].format(AddText)
        for key, value in auxListDict[i].items():
            if type(value) is list:
                for j in range(0,len(value),1):
                    TOTAL_data[f"[{textAux}] {key}-{j}"] = value[j]
            else:
                TOTAL_data[f"[{textAux}] {key}"] = value

    return TOTAL_data

def processComponentsData(PV_data: dict, INVPV_data: dict, RCPV_data: dict, AERO_data: dict, INVAERO_data: dict, RCAERO_data: dict,
                          BAT_data: dict, GE_data: dict, rho: float, PVs: int, PVp: int, Ns_BAT: int, Np_BAT: int,
                          columnsOptionsData: dict, numberPhases: int, validateEntries: dict, componentInTheProject: dict):

    TOTAL_data = {}

    if componentInTheProject["generationGE"]:
        TOTAL_data = proccesComponentData(TOTAL_data, PV_data, INVPV_data, RCPV_data, "PV")
        TOTAL_data["PVs"] = PVs
        TOTAL_data["PVp"] = PVp

    if componentInTheProject["generationAERO"]:
        TOTAL_data = proccesComponentData(TOTAL_data, AERO_data, INVAERO_data, RCAERO_data, "AERO")
        TOTAL_data["rho"] = rho

    if BAT_data is not None:
        for key, value in BAT_data.items():
            TOTAL_data[f"[BAT_data] {key}"] = value

    TOTAL_data["Ns_BAT"] = Ns_BAT
    TOTAL_data["Np_BAT"] = Np_BAT

    if GE_data is not None:
        for key, value in GE_data.items():
            TOTAL_data[f"[GE_data] {key}"] = value

    if validateEntries is not None:
        for key, value in validateEntries.items():
            TOTAL_data[f"[validateEntries] {key}"] = value

    if columnsOptionsData is not None:
        TOTAL_data = getAddUniqueColumnsOptionsData(TOTAL_data, columnsOptionsData)

    TOTAL_data["numberPhases"] = numberPhases

    if validateEntries is not None:
        for key, value in componentInTheProject.items():
            TOTAL_data[f"[componentInTheProject] {key}"] = value

    return TOTAL_data

def getBytesFileExcelProjectOffGrid(dictDataOffGrid: dict) -> bytes:

    dictOutput = getImputProcessComponentData(dictDataOffGrid)
    TOTAL_data = processComponentsData(**dictOutput)
    bytesFileExcel = toExcelResults(df=dictDataOffGrid["df_data"], dictionary=TOTAL_data,
                                    df_sheetName="Data", dict_sheetName="Params")

    return bytesFileExcel

def getBytesFileYamlComponentsOffGrid(dictDataOffGrid: dict) -> bytes:

    dictDataOffGridCopy = dictDataOffGrid.copy()

    if "df_data" in dictDataOffGridCopy:
        del dictDataOffGridCopy["df_data"]

    bufferData = get_bytes_yaml(dictionary=dictDataOffGridCopy)

    return bufferData

#%% funtions streamlit

def get_widget_number_input(label: str, disabled: bool, key: str, variable: dict):

    return st.number_input(label=label, disabled=disabled, key=key, **variable)

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

def getCompValidation(uploadedYaml, optionsKeys):

    check, data = False, False

    if uploadedYaml is not None:
        try:
            data = yaml.safe_load(uploadedYaml)
            check = check_dict_input(data, optionsKeys)
        except:
            st.error("Error al cargar archivo **YAML** (.yaml)", icon="🚨")

    return check, data

def getDataOffGridCompValidation(uploadedYamlCOMP, uploadedYamlINV_COMP, uploadedYamlRC_COMP,
                                 optKeysCOMP, optKeysINVCOMP, optKeysRCCOMP):

    check, data = {}, {}

    if uploadedYamlCOMP is None:
        st.error("Cargar **Datos del Módulo**", icon="🚨")
    if uploadedYamlINV_COMP is None:
        st.error("Cargar **Datos del Inversor**", icon="🚨")
    if uploadedYamlRC_COMP is None:
        st.error("Cargar **Datos del Regulador de carga**", icon="🚨")

    check["check_COMP"], data["COMP_data"] = getCompValidation(uploadedYamlCOMP, optKeysCOMP)               # COMP
    check["check_INVCOMP"], data["INVCOMP_data"] = getCompValidation(uploadedYamlINV_COMP, optKeysINVCOMP)  # INV_COMP
    check["check_RCCOMP"], data["RCCOMP_data"] = getCompValidation(uploadedYamlRC_COMP, optKeysRCCOMP)      # RC_COMP

    return check, data

def getDataOffGridValidation(uploadedYamlCOMP, uploadedYamlINV_COMP, uploadedYamlRC_COMP, validateEntries: dict, typeOfSystem: str):
    
    if typeOfSystem == "PV":
        check, data = getDataOffGridCompValidation(uploadedYamlCOMP, uploadedYamlINV_COMP, uploadedYamlRC_COMP,
                                                   optKeysPV, optKeysINVCOMP, optKeysRCCOMP)

        validateEntries["check_PV"] = check["check_COMP"]
        validateEntries["check_INVPV"] = check["check_INVCOMP"]
        validateEntries["check_RCPV"] = check["check_RCCOMP"]

    if typeOfSystem == "AERO":
        check, data = getDataOffGridCompValidation(uploadedYamlCOMP, uploadedYamlINV_COMP, uploadedYamlRC_COMP,
                                                   optKeysAERO, optKeysINVCOMP, optKeysRCCOMP)
        
        validateEntries["check_AERO"] = check["check_COMP"]
        validateEntries["check_INVAERO"] = check["check_INVCOMP"]
        validateEntries["check_RCAERO"] = check["check_RCCOMP"]

    return validateEntries, data["COMP_data"], data["INVCOMP_data"], data["RCCOMP_data"]

def getDataGEorBATValidation(uploadedYamlCOMP, validateEntries: dict, typeOfComponet: str):

    if uploadedYamlCOMP is None:
        if typeOfComponet == "GE":
            st.error("Cargar **Datos del Grupo electrógeno**", icon="🚨")
        elif typeOfComponet == "BAT":
            st.error("Cargar **Datos del Banco de baterías**", icon="🚨")

    if typeOfComponet == "GE":
        optKeys = optKeysGE
    elif typeOfComponet == "BAT":
        optKeys = optKeysBAT

    check, data = getCompValidation(uploadedYamlCOMP, optKeys)
    validateEntries[f"check_{typeOfComponet}"] = check
    
    return validateEntries, data

def getCompValidationBattery(check_RCCOMP: bool, RCCOMP_data: dict, BAT_data: dict):

    outCheck = False

    if check_RCCOMP:
        list_VdcBB, listAuxVnBB = RCCOMP_data["Vdc_bb"], []
        for i in range(0,len(list_VdcBB),1):
            listAuxVnBB.append(list_VdcBB[i] == BAT_data["V_nom"])

        outCheck = any(listAuxVnBB)

        if not outCheck:
            st.error("**Regulador de carga**", icon="🚨")
        

    return outCheck

def excelDownloadButton(bytesFileExcel, file_name):

    df_download = st.download_button(
        label=f"📄 Descargar **:blue[{file_name}] XLSX**",
        data=bytesFileExcel,
        file_name=name_file_head(name=f"{file_name}.xlsx"),
        mime='xlsx')

    return df_download


