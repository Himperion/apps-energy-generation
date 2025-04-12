# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import yaml, io, warnings
from datetime import datetime

from funtions import general

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

def getGlobalVariablesPV():
    params_PV, rename_PV, showOutputPV = None, None, None

    with open("files//[PV] - params.yaml", 'r') as archivo:
        params_PV = yaml.safe_load(archivo)

    with open("files//[PV] - dict_replace.yaml", 'r') as archivo:
        rename_PV = yaml.safe_load(archivo)

    if params_PV is not None:
        showOutputPV = [f"{params_PV[elm]['label']}{params_PV[elm]['unit']}: {params_PV[elm]['description']}" for elm in ["Voc", "Isc", "Impp", "Vmpp", "Pmpp"]]

    return params_PV, rename_PV, showOutputPV

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
                           componentInTheProject: dict,
                           timeInfo:dict):
    
    SOC_0, SOC_conx, SOC_max, SOC_min, SOC_ETP1, SOC_ETP2,  = getListChargeRegulatorData(RCPV_data, RCAERO_data, componentInTheProject["generationPV"], componentInTheProject["generationAERO"])
    VocPU_PV, VnomPU_PV, PnomPU_PV, InomPU_PV, RinvPU_PV, n_InvPV = getInverterParameters(INVPV_data, numberPhases, Sb, Vb, Ib, Zb, componentInTheProject["generationPV"])
    VocPU_AERO, VnomPU_AERO, PnomPU_AERO, InomPU_AERO, RinvPU_AERO, n_InvAERO = getInverterParameters(INVAERO_data, numberPhases, Sb, Vb, Ib, Zb, componentInTheProject["generationAERO"])
    n_RcPV = getChargeRegulatorParameters(RCPV_data, componentInTheProject["generationPV"])
    n_RcAERO = getChargeRegulatorParameters(RCAERO_data, componentInTheProject["generationAERO"])
    
    delta_t = timeInfo["deltaMinutes"]/60
    n_bat = BAT_data["bat_efficiency"]/100
    
    Ebb_nom, Vbb_max, Vbb_min, Ibb_max, Ibb_min, m_ETP2, b_ETP2 = getBatteryBankParameters(C=BAT_data["C"],
                                                                                           I_max=BAT_data["I_max"],
                                                                                           I_min=BAT_data["I_min"],
                                                                                           V_max=BAT_data["V_max"],
                                                                                           V_min=BAT_data["V_min"],
                                                                                           V_nom=BAT_data["V_nom"],
                                                                                           Ns=Ns_BAT, Np=Np_BAT,
                                                                                           SOC_ETP1=SOC_ETP1, SOC_ETP2=SOC_ETP2)

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
        
        #df_grid.loc[index, "NodoTotal"] = PrcDC_PV + PrcDC_AERO - Pbb - PinvDC_PV - PinvDC_AERO
        #df_grid.loc[index, "Nodo1"] = PrcDC_PV - PinvDC_PV - Pbb_PV
        #df_grid.loc[index, "Nodo2"] = PrcDC_AERO - PinvDC_AERO - Pbb_AERO
        #df_grid.loc[index, "Nodo3"] = Ibb - (Ibb_PV + Ibb_AERO)
        #df_grid.loc[index, "Nodo4"] = (Pbb_PV + Pbb_AERO) - Pbb
    
    return df_grid

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
                      componentInTheProject: dict,
                      generationType: str):
    
    params_PV, rename_PV, showOutputPV =  getGlobalVariablesPV()
    timeInfo = general.getTimeData(df_data)
    Sb, Vb, Ib, Zb = general.getGlobalPerUnitSystem(INVPV_data, INVAERO_data, numberPhases, componentInTheProject["generationPV"], componentInTheProject["generationAERO"])

    df_offGrid = df_data.copy()
    df_offGrid = general.initializeDataFrameColumns(df_offGrid, generationType)

    if componentInTheProject["generationPV"]:       # PV
        df_offGrid = general.getDataframePV(df_offGrid, PV_data, INVPV_data, PVs, PVp, columnsOptionsData, params_PV, rename_PV, showOutputPV, numberPhases)

    if componentInTheProject["generationAERO"]:     # AERO
        df_offGrid = general.getDataframeAERO(df_offGrid, AERO_data, INVAERO_data, rho, columnsOptionsData)

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
                                        componentInTheProject=componentInTheProject,
                                        timeInfo=timeInfo)

    if componentInTheProject["generationGE"]:       # GE
        df_offGrid = general.getDataframeGE(df_offGrid, GE_data, columnsOptionsData)

    return df_offGrid

def processComponentsDataOffGrid(PV_data: dict, INVPV_data: dict, RCPV_data: dict, AERO_data: dict, INVAERO_data: dict, RCAERO_data: dict,
                                 BAT_data: dict, GE_data: dict, rho: float, PVs: int, PVp: int, Ns_BAT: int, Np_BAT: int,
                                 columnsOptionsData: dict, numberPhases: int, validateEntries: dict, componentInTheProject: dict,
                                 generationType: str):

    TOTAL_data = {}

    if componentInTheProject["generationPV"]:
        TOTAL_data = general.proccesComponentData(TOTAL_data, PV_data, INVPV_data, RCPV_data, "PV", generationType)
        TOTAL_data["PVs"] = PVs
        TOTAL_data["PVp"] = PVp

    if componentInTheProject["generationAERO"]:
        TOTAL_data = general.proccesComponentData(TOTAL_data, AERO_data, INVAERO_data, RCAERO_data, "AERO", generationType)
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
        TOTAL_data = general.getAddUniqueColumnsOptionsData(TOTAL_data, columnsOptionsData)

    TOTAL_data["numberPhases"] = numberPhases

    if componentInTheProject is not None:
        for key, value in componentInTheProject.items():
            TOTAL_data[f"[componentInTheProject] {key}"] = value

    TOTAL_data["generationType"] = generationType

    return TOTAL_data

def getBytesFileExcelProjectOffGrid(dictDataOffGrid: dict, dataKeyList: list):

    dictOutput = general.getImputProcessComponentData(dictDataOffGrid, dataKeyList)
    TOTAL_data = processComponentsDataOffGrid(**dictOutput)
    bytesFileExcel = general.toExcelResults(df=dictDataOffGrid["df_data"], dictionary=TOTAL_data,
                                            df_sheetName="Data", dict_sheetName="Params")

    return TOTAL_data, bytesFileExcel

def getBytesFileYamlComponentsOffGrid(dictDataOffGrid: dict) -> bytes:

    dictDataOffGridCopy = dictDataOffGrid.copy()

    if "df_data" in dictDataOffGridCopy:
        del dictDataOffGridCopy["df_data"]

    bufferData = general.getBytesYaml(dictionary=dictDataOffGridCopy)

    return bufferData

def getDictCountSwLoad(df_timeLapse: pd.DataFrame) -> dict:

    dictCountSwLoad, swItems = {}, [1, 2, 3]
    countSwLoad = df_timeLapse["swLoad(t)"].value_counts()

    for key, value in countSwLoad.items():
        dictCountSwLoad[f"swLoad_{key}"] = value

    for item in swItems:
        if not f"swLoad_{item}" in dictCountSwLoad:
            dictCountSwLoad[f"swLoad_{item}"] = 0

    return dictCountSwLoad

def getDataAnalysisOffGrid(df_timeLapse: pd.DataFrame, deltaMinutes: int, timeLapse: str, date):

    dictCountSwLoad = getDictCountSwLoad(df_timeLapse)

    list_dftimeLapseColumns = df_timeLapse.columns.to_list()

    if not "Consumo_GE(l/h)" in list_dftimeLapseColumns:
        df_timeLapse["Consumo_GE(l/h)"] = 0.0

    Ebb_absorbed = df_timeLapse.loc[df_timeLapse["Pbb(kW)"] > 0, "Pbb(kW)"].sum()*(deltaMinutes/60)
    Ebb_delivered = df_timeLapse.loc[df_timeLapse["Pbb(kW)"] < 0, "Pbb(kW)"].sum()*(deltaMinutes/60)*(-1)
    Eload_GE = df_timeLapse.loc[df_timeLapse["swLoad(t)"] == 3, "Load(kW)"].sum()*(deltaMinutes/60)
    Eload_OffGrid = df_timeLapse.loc[df_timeLapse["swLoad(t)"] != 3, "Load(kW)"].sum()*(deltaMinutes/60)

    dataAnalysis = {
        f"dates (Y-M-D hh:mm:ss)": date,
        f"Eload(kWh/{timeLapse})": df_timeLapse["Load(kW)"].sum()*(deltaMinutes/60),
        f"Egen_PV(kWh/{timeLapse})": df_timeLapse["Pgen_PV(kW)"].sum()*(deltaMinutes/60),
        f"Egen_AERO(kWh/{timeLapse})": df_timeLapse["Pgen_AERO(kW)"].sum()*(deltaMinutes/60),
        f"Egen_INVPV(kWh/{timeLapse})": df_timeLapse["PinvAC_PV(kW)"].sum()*(deltaMinutes/60),
        f"Egen_INVAERO(kWh/{timeLapse})": df_timeLapse["PinvAC_AERO(kW)"].sum()*(deltaMinutes/60),
        f"Ebb(kWh/{timeLapse})": df_timeLapse["Pbb(kW)"].sum()*(deltaMinutes/60),
        f"Ebb_absorbed(kWh/{timeLapse})": Ebb_absorbed,
        f"Ebb_delivered(kWh/{timeLapse})": Ebb_delivered,
        f"Eload_GE(kWh/{timeLapse})": Eload_GE,
        f"Eload_OffGrid(kWh/{timeLapse})": Eload_OffGrid,
        f"conSD(h/{timeLapse})": df_timeLapse["conSD(t)"].sum()*(deltaMinutes/60),
        f"conSC(h/{timeLapse})": df_timeLapse["conSC(t)"].sum()*(deltaMinutes/60),
        f"swLoad_1(h/{timeLapse})": dictCountSwLoad["swLoad_1"]*(deltaMinutes/60),
        f"swLoad_2(h/{timeLapse})": dictCountSwLoad["swLoad_2"]*(deltaMinutes/60),
        f"swLoad_3(h/{timeLapse})": dictCountSwLoad["swLoad_3"]*(deltaMinutes/60),
        f"Consumo_GE(l/{timeLapse})": df_timeLapse["Consumo_GE(l/h)"].sum()*(deltaMinutes/60) 
    }

    return dataAnalysis

#%% funtions streamlit

def get_widget_number_input(label: str, disabled: bool, key: str, variable: dict):

    return st.number_input(label=label, disabled=disabled, key=key, **variable)

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
