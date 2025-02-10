# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import yaml

from funtions import fun_app5, fun_app6

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

optKeysBATCOMP = [
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

optKeysRCCOMP = [
    "SOC_0",
    "SOC_ETP1",
    "SOC_ETP2",
    "SOC_conx",
    "SOC_max",
    "SOC_min",
    "rc_efficiency"
]

dict_phases = {
    "Monofásico": {"Num": 1, "label": "1️⃣ Monofásico"},
    "Trifásico": {"Num": 3, "label": "3️⃣ Trifásico"}
}

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

def getBoolGeneration(validateEntries):

    bool_PV = validateEntries["check_PV"] and validateEntries["check_INVPV"] and validateEntries["check_BATPV"] and validateEntries["check_RCPV"]
    bool_AERO = validateEntries["check_AERO"] and validateEntries["check_INVAERO"] and validateEntries["check_BATAERO"] and validateEntries["check_RCAERO"]
    bool_GE = validateEntries["check_GE"]

    return bool_PV, bool_AERO, bool_GE

def getConditionValidateEntriesOffGrid(validateEntries: dict):

    bool_PV, bool_AERO, bool_GE = getBoolGeneration(validateEntries)

    return (validateEntries['check_DATA'] and (bool_PV or bool_AERO)) or bool_GE

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
    
    df_pv['Pinv_PV(kW)'] =  df_pv['Pmpp(kW)']*INVPV_data['efficiency_max']/100

    df_pv = df_pv[["Voc(V)", "Isc(A)", "Impp(A)", "Vmpp(V)", "Pmpp(kW)", "Pinv_PV(kW)"]]
    df_pv.rename(columns={"Voc(V)": "Voc_PV(V)", "Isc(A)": "Isc_PV(A)", "Impp(A)": "Impp_PV(A)", "Vmpp(V)": "Vmpp_PV(V)", "Pmpp(kW)": "Pmpp_PV(kW)"}, inplace=True)

    return df_pv

def getPerUnitSystem(Pac_nom: float, Vac_nom: float, numberPhases: int):

    Sb = Pac_nom
    Vb = Vac_nom
    Ib = (Pac_nom*1000)/(np.sqrt(numberPhases)*Vac_nom)
    Zb = Vb/Ib

    return Sb, Vb, Ib, Zb

def getGlobalPerUnitSystem(INVPV_data: dict, INVAERO_data: dict, numberPhases: int, bool_PV: bool, bool_AERO: bool):

    if INVPV_data and not INVAERO_data:
        Pac_nom, Vac_nom = INVPV_data["Pac_max"], INVPV_data["Vac_nom"]
        
    elif not INVPV_data and INVAERO_data:
        Pac_nom, Vac_nom = INVAERO_data["Pac_max"], INVAERO_data["Vac_nom"]

    else:
        Pac_nom, Vac_nom = INVPV_data["Pac_max"], INVPV_data["Vac_nom"]

    return getPerUnitSystem(Pac_nom=Pac_nom, Vac_nom=Vac_nom, numberPhases=numberPhases)

def getInverterParameters(INV_data: dict, numberPhases: int, Sb: float, Vb: float, Ib: float, Zb: float):

    Iac_nom = (INV_data["Pac_max"]*1000)/(np.sqrt(numberPhases)*INV_data["Vac_nom"])

    Voc_PU = INV_data["Vac_max"]/Vb
    Vnom_PU = INV_data["Vac_nom"]/Vb
    Pnom_PU = INV_data["Pac_max"]/Sb
    Inom_PU = Iac_nom/Ib
    Rinv_PU = (Voc_PU - Vnom_PU)/Inom_PU

    return Voc_PU, Vnom_PU, Pnom_PU, Inom_PU, Rinv_PU

def getBatteryBankParameters(C: float, I_max: float, I_min: float, V_max: float, V_min: float, V_nom: float, Ns: int, Np: int, SOC_ETP1: float, SOC_ETP2: float):

    Ebb_nom = ((C*V_nom)/1000)*(Ns*Np)
    Vbb_max = V_max*Ns
    Vbb_min = V_min*Ns
    Ibb_max = I_max*Np
    Ibb_min = I_min*Np
    m_ETP2 = (Ibb_max - Ibb_min)/(SOC_ETP1 - SOC_ETP2)
    b_ETP2 = Ibb_max - m_ETP2*SOC_ETP1

    return Ebb_nom, Vbb_max, Vbb_min, Ibb_max, Ibb_min, m_ETP2, b_ETP2

def getBatteryCalculationsPV(df_data: pd.DataFrame,
                             df_PV: pd.DataFrame,
                             C: float,
                             DOD: float,
                             I_max: float,
                             I_min: float,
                             V_max: float,
                             V_min: float,
                             V_nom: float,
                             bat_type: str,
                             bat_efficiency: float,
                             SOC_0: float,
                             SOC_ETP1: float,
                             SOC_ETP2: float,
                             SOC_conx: float,
                             SOC_max: float,
                             SOC_min: float,
                             rc_efficiency: float,
                             inv_efficiency: float,
                             Ns: int,
                             Np: int):
    
    timeInfo = getTimeData(df_data)
    delta_t = timeInfo["deltaMinutes"]/60
    n_bat = bat_efficiency/100

    Ebb_nom, Vbb_max, Vbb_min, Ibb_max, Ibb_min, m_ETP2, b_ETP2 = getBatteryBankParameters(C, I_max, I_min, V_max, V_min, V_nom, Ns, Np, SOC_ETP1, SOC_ETP2)
    
    df_PV["Pinv_PV(kW)"] = df_data["Load(kW)"]/(inv_efficiency/100)
    df_PV["Pbb_PV(kW)"] = df_PV["Pmpp_PV(kW)"] - df_PV["Pinv_PV(kW)"]
    df_PV["SOC(t)"] = 0
    df_PV["deltaEbb(kWh)"] = 0.0
    df_PV["SW1(t)"] = False
    df_PV["SW2(t)"] = False
    df_PV["conSD(t)"] = False
    df_PV["conSC(t)"] = False

    df_PV["deltaEbb(kWh)"] = df_PV["deltaEbb(kWh)"].astype(float)

    st.text(f"delta_t: {delta_t}")
    st.text(f"type: {bat_efficiency}")

    st.text(df_PV.dtypes)


    for index, row in df_PV.iterrows():
        #st.text(f"{index}: {df_PV.loc[index, 'Pbb_PV(kW)']}")

        if index == 0:      # (t-1)
            SOC_t_1, SW1_t_1, SW2_t_1 = SOC_0, True, True
        else:
            SOC_t_1, SW1_t_1, SW2_t_1 = df_PV.loc[index-1, "SOC(t)"], df_PV.loc[index-1, "SW1(t)"], df_PV.loc[index-1, "SW1(t)"]

        if df_PV.loc[index, 'Pbb_PV(kW)'] >= 0:
            df_PV.loc[index, "deltaEbb(kWh)"] = df_PV.loc[index, 'Pbb_PV(kW)']*n_bat*delta_t
        else:
            df_PV.loc[index, "deltaEbb(kWh)"] = df_PV.loc[index, 'Pbb_PV(kW)']*(1/n_bat)*delta_t

            
            
            

    # conditionSC
    # conditionSD

    st.dataframe(df_PV)

    st.dataframe(df_data)

    return

def generationOffGrid(df_data: pd.DataFrame,
                      PV_data: dict| None,
                      INVPV_data: dict | None,
                      BATPV_data: dict | None,
                      RCPV_data: dict | None,
                      AERO_data: dict | None,
                      INVAERO_data: dict | None,
                      BATAERO_data: dict | None,
                      RCAERO_data: dict | None,
                      rho: float | None,
                      PVs: int | None,
                      PVp: int | None,
                      Ns_PV: int | None,
                      Np_PV: int | None,
                      Ns_AERO: int | None,
                      Np_AERO: int | None,
                      columnsOptionsData: list,
                      numberPhases: int,
                      validateEntries: dict) -> pd.DataFrame:
    
    params_PV, rename_PV, showOutputPV =  getGlobalVariablesPV()
    bool_PV, bool_AERO, bool_GE = getBoolGeneration(validateEntries)
    Sb, Vb, Ib, Zb = getGlobalPerUnitSystem(INVPV_data, INVAERO_data, numberPhases, bool_PV, bool_AERO)

    st.text(bool_PV)
    st.text(bool_GE)

    if bool_PV:     # PV
        df_PV = getDataframePV(df_data, PV_data, INVPV_data, PVs, PVp, columnsOptionsData, params_PV, rename_PV, showOutputPV, numberPhases)
        
        Voc_PUPV, Vnom_PUPV, Pnom_PUPV, Inom_PUPV, Rinv_PUPV = getInverterParameters(INVPV_data, numberPhases, Sb, Vb, Ib, Zb)

        getBatteryCalculationsPV(df_data=df_data, df_PV=df_PV, Ns=Ns_PV, Np=Np_PV, inv_efficiency=INVPV_data["efficiency_max"], **BATPV_data, **RCPV_data)

        
        

    if bool_GE:     # GE
        print("Ajaaaaaaaaaa")
        
         

    return

def getUniqueDictColumnsOptionsData(columnsOptionsData: dict):

    uniqueColumnsOptionsData = {}

    for key, value in columnsOptionsData.items():
        for subKey, subValue in value.items():
            st.text(f"[{key}][{subKey}]: {subValue}")

            uniqueColumnsOptionsData[f"{key}-{subKey}"] = subValue

    return uniqueColumnsOptionsData

def processComponentData(dictImput):

    dictOutput = {
        "PV_data": dictImput["PV_data"],
        "INVPV_data": dictImput["INVPV_data"],
        "BATPV_data": dictImput["BATPV_data"],
        "RCPV_data": dictImput["RCPV_data"],
        "AERO_data": dictImput["AERO_data"],
        "INVAERO_data": dictImput["INVAERO_data"],
        "BATAERO_data": dictImput["BATAERO_data"],
        "RCAERO_data": dictImput["RCAERO_data"],
        "rho": dictImput["rho"],
        "PVs": dictImput["PVs"],
        "PVp": dictImput["PVp"],
        "Ns_PV": dictImput["Ns_PV"],
        "Np_PV": dictImput["Np_PV"],
        "Ns_AERO": dictImput["Ns_AERO"],
        "Np_AERO": dictImput["Np_AERO"],
        "numberPhases": dictImput["numberPhases"],
        "validateEntries": dictImput["validateEntries"]
    }

    dictImput["columnsOptionsData"]
    dictImput["params_PV"]
    dictImput["rename_PV"]
    dictImput["showOutputPV"]
    dictImput["validateEntries"]

    listPrint = ["columnsOptionsData", "params_PV", "rename_PV", "showOutputPV", "validateEntries"]

    for item in listPrint:
        st.text("{0}: {1}".format(item, dictImput[item]))

    return

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

def getDataOffGridCompValidation(uploadedYamlCOMP, uploadedYamlINV_COMP, uploadedYamlBAT_COMP, uploadedYamlRC_COMP,
                                 optKeysCOMP, optKeysINVCOMP, optKeysBATCOMP, optKeysRCCOMP):

    check, data = {}, {}

    if uploadedYamlCOMP is None:
        st.error("Cargar **Datos del Módulo**", icon="🚨")
    if uploadedYamlINV_COMP is None:
        st.error("Cargar **Datos del Inversor**", icon="🚨")
    if uploadedYamlBAT_COMP is None:
        st.error("Cargar **Datos del Banco de baterías**", icon="🚨")
    if uploadedYamlBAT_COMP is None:
        st.error("Cargar **Datos del Regulador de carga**", icon="🚨")

    check["check_COMP"], data["COMP_data"] = getCompValidation(uploadedYamlCOMP, optKeysCOMP)               # COMP
    check["check_INVCOMP"], data["INVCOMP_data"] = getCompValidation(uploadedYamlINV_COMP, optKeysINVCOMP)  # INV_COMP
    check["check_BATCOM"], data["BATCOMP_data"] = getCompValidation(uploadedYamlBAT_COMP, optKeysBATCOMP)   # BAT_COMP
    check["check_RCCOMP"], data["RCCOMP_data"] = getCompValidation(uploadedYamlRC_COMP, optKeysRCCOMP)      # RC_COMP

    return check, data

def getDataOffGridValidation(uploadedYamlCOMP, uploadedYamlINV_COMP, uploadedYamlBAT_COMP, uploadedYamlRC_COMP, validateEntries: dict, typeOfSystem: str):

    if typeOfSystem == "PV":
        check, data = getDataOffGridCompValidation(uploadedYamlCOMP, uploadedYamlINV_COMP, uploadedYamlBAT_COMP, uploadedYamlRC_COMP,
                                                   optKeysPV, optKeysINVCOMP, optKeysBATCOMP, optKeysRCCOMP)

        validateEntries["check_PV"] = check["check_COMP"]
        validateEntries["check_INVPV"] = check["check_INVCOMP"]
        validateEntries["check_BATPV"] = check["check_BATCOM"]
        validateEntries["check_RCPV"] = check["check_RCCOMP"]

    if typeOfSystem == "AERO":
        check, data = getDataOffGridCompValidation(uploadedYamlCOMP, uploadedYamlINV_COMP, uploadedYamlBAT_COMP, uploadedYamlRC_COMP,
                                                   optKeysAERO, optKeysINVCOMP, optKeysBATCOMP, optKeysRCCOMP)
        
        validateEntries["check_AERO"] = check["check_COMP"]
        validateEntries["check_INVAERO"] = check["check_INVCOMP"]
        validateEntries["check_BATAERO"] = check["check_BATCOM"]
        validateEntries["check_RCAERO"] = check["check_RCCOMP"]

    return validateEntries, data["COMP_data"], data["INVCOMP_data"], data["BATCOMP_data"], data["RCCOMP_data"]
