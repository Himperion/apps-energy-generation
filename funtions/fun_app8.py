# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import io, calendar, yaml
from datetime import datetime

from funtions import fun_app5, fun_app6

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

def name_file_head(name: str) -> str:
    now = datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def toExcelResults(df: pd.DataFrame, dict_params: dict) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
        if dict_params is not None:
            df_params = pd.DataFrame(dict_params, index=[0])
            df_params.to_excel(writer, index=False, sheet_name="Params")

    return output.getvalue()

def get_label_params(dict_param: dict) -> str:

    return f"**{dict_param['label']}:** {dict_param['description']} {dict_param['unit']}"

def getParametersINV_data(INV_data: dict) -> dict:

    if INV_data is not None:
        INV_data['Iac_nom'] = round((INV_data['Pac_max']*1000)/(np.sqrt(dict_phases[INV_data['phases']]['Num'])*INV_data['Vac_nom']), 4)
        INV_data['Rinv'] = round((INV_data['Vac_max'] - INV_data['Vac_nom'])/INV_data['Iac_nom'], 4)

    return INV_data

def processComponentData(PV_data: dict, INVPV_data: dict, AERO_data: dict, INVAERO_data: dict, rho, PVs, PVp, V_PCC, numberPhases):

    COMP_data = {}

    if PV_data is not None and INVPV_data is not None:

        for key, value in PV_data.items():
            COMP_data[f"[PV_data] {key}"] = value

        for key, value in INVPV_data.items():
            COMP_data[f"[INVPV_data] {key}"] = value

        COMP_data["PVs"] = PVs
        COMP_data["PVp"] = PVp

    if AERO_data is not None and INVAERO_data is not None:

        for key, value in AERO_data.items():
            COMP_data[f"[AERO_data] {key}"] = value

        for key, value in INVAERO_data.items():
            COMP_data[f"[INVAERO_data] {key}"] = value

    COMP_data["V_PCC"] = V_PCC
    COMP_data["numberPhases"] = numberPhases

    return COMP_data

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

def getNumberPhases(INVPV_data, INVAERO_data) -> int:

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

    return numberPhases

def getDataframePV(df_data: pd.DataFrame, PV_data: dict, INVPV_data: dict, PVs: int, PVp: int, V_PCC: float, columnsOptionsData: list, params_PV: dict, rename_PV: dict, showOutputPV: list, numberPhases: int):

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
    df_pv['Vinv_PV(V)'] = V_PCC
    df_pv['Iinv_PV(A)'] = (df_pv['Pinv_PV(kW)']*1000)/(np.sqrt(numberPhases)*V_PCC)

    df_pv = df_pv[["Voc(V)", "Isc(A)", "Impp(A)", "Vmpp(V)", "Pmpp(kW)", "Pinv_PV(kW)", "Iinv_PV(A)"]]
    df_pv.rename(columns={"Voc(V)": "Voc_PV(V)", "Isc(A)": "Isc_PV(A)", "Impp(A)": "Impp_PV(A)", "Vmpp(V)": "Vmpp_PV(V)", "Pmpp(kW)": "Pmpp_PV(kW)"}, inplace=True)

    return df_pv

def getDataframeAERO(df_data: pd.DataFrame, AERO_data: dict, INVAERO_data: dict, rho, V_PCC: float, columnsOptionsData: list, numberPhases: int):

    df_aero = fun_app6.get_dataframe_power_wind_turbine(params=AERO_data,
                                                        rho=rho,
                                                        dataframe=df_data,
                                                        column=columnsOptionsData["AERO"])
    
    df_aero.rename(columns={"Pideal(kW)": "Pideal_AERO(kW)", "Pbetz(kW)": "Pbetz_AERO(kW)", "Pgen(kW)":"Pgen_AERO(kW)", "efficiency(%)": "efficiency_AERO(%)"}, inplace=True)

    df_aero['Pinv_AERO(kW)'] =  df_aero["Pgen_AERO(kW)"]*INVAERO_data["efficiency_max"]/100
    df_aero['Vinv_AERO(V)'] = V_PCC
    df_aero['Iinv_AERO(V)'] = (df_aero['Pinv_AERO(kW)']*1000)/(np.sqrt(numberPhases)*V_PCC)

    df_aero = df_aero[["Pideal_AERO(kW)", "Pbetz_AERO(kW)", "Pgen_AERO(kW)", "Pinv_AERO(kW)", "Iinv_AERO(V)"]]

    return df_aero

def generationOnGrid(df_data: pd.DataFrame, PV_data: dict, INVPV_data: dict, AERO_data: dict, INVAERO_data: dict, rho: float, PVs: int, PVp: int, V_PCC: float, columnsOptionsData: list, params_PV: dict, rename_PV: dict, showOutputPV: list, numberPhases: int) -> pd.DataFrame:

    flagPV = (PV_data is not None) and (INVPV_data is not None) and ("PV" in columnsOptionsData)
    flagAERO = (AERO_data is not None) and (INVAERO_data is not None) and ("AERO" in columnsOptionsData)
    df_out, df_pv, df_aero = None, None, None

    if numberPhases is not None:
        if flagPV:
            df_pv = getDataframePV(df_data, PV_data, INVPV_data, PVs, PVp, V_PCC, columnsOptionsData, params_PV, rename_PV, showOutputPV, numberPhases)
        if flagAERO:
            df_aero = getDataframeAERO(df_data, AERO_data, INVAERO_data, rho, V_PCC, columnsOptionsData, numberPhases)

        if flagPV and not flagAERO:
            df_out = pd.concat([df_data, df_pv], axis=1)
            df_out["Pgen_AERO(kW)"] = 0
            df_out["Pinv_AERO(kW)"] = 0
        elif not flagPV and flagAERO:
            df_out = pd.concat([df_data, df_aero], axis=1)
            df_out["Pmpp_PV(kW)"] = 0
            df_out["Pinv_PV(kW)"] = 0
        else:
            df_out = pd.concat([df_data, df_pv, df_aero], axis=1)

        df_out['I_LOAD(A)'] = (df_out['Load(kW)']*1000)/(np.sqrt(numberPhases)*V_PCC)
        df_out["Pdem(kW)"] = df_out["Load(kW)"] - df_out["Pinv_PV(kW)"] - df_out["Pinv_AERO(kW)"]
        

    else:
        st.text("Error fases")

    return df_out

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

def getDataAnalysis(df_timeLapse: pd.DataFrame, deltaMinutes: int, timeLapse: str, date) -> dict:

    Egen = (df_timeLapse["Pinv_PV(kW)"].sum()+df_timeLapse["Pinv_AERO(kW)"].sum())*(deltaMinutes/60)
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
        f"Egen_PV(kWh/{timeLapse})": df_timeLapse["Pmpp_PV(kW)"].sum()*(deltaMinutes/60),
        f"Egen_INV-PV(kWh/{timeLapse})": df_timeLapse["Pinv_PV(kW)"].sum()*(deltaMinutes/60),
        f"Egen_AERO(kWh/{timeLapse})": df_timeLapse["Pgen_AERO(kW)"].sum()*(deltaMinutes/60),
        f"Egen_INV-AERO(kWh/{timeLapse})": df_timeLapse["Pinv_AERO(kW)"].sum()*(deltaMinutes/60),
        f"Egen(kWh/{timeLapse})": Egen,
        f"Edem(kWh/{timeLapse})": df_timeLapse["Pdem(kW)"].sum()*(deltaMinutes/60),
        f"Eimp(kWh/{timeLapse})": Eimp,
        f"Eexp(kWh/{timeLapse})": Eexp,
        f"Eauto(kWh/{timeLapse})": Egen - Eexp,
        f"Exct1(kWh/{timeLapse}": Eexct1,
        f"Exct2(kWh/{timeLapse}": Eexct2
        }

    return dataAnalysis

def getTimeDimensionCheck(dataframe: pd.DataFrame, deltaMinutes: int, timeLapse: str, date) -> bool:

    test1, test2, test3 = False, False, False

    dailySamples = (60/deltaMinutes)*24

    if timeLapse == "day":
        test1 = dataframe.shape[0] == dailySamples
    elif timeLapse == "month":
        if date.month == 2:
            if calendar.isleap(date.year):
                test2 = dataframe.shape[0] == 29*dailySamples
            else:
                test2 = dataframe.shape[0] == 28*dailySamples
        else:
            test2 = dataframe.shape[0] == 30*dailySamples or dataframe.shape[0] == 31*dailySamples
    elif timeLapse == "year":
        if calendar.isleap(date.year):
            test3 = dataframe.shape[0] == 366*dailySamples
        else:
            test3 = dataframe.shape[0] == 365*dailySamples

    finalTest = test1 or test2 or test3

    return finalTest

def getAnalysisInTime(df_data: pd.DataFrame, deltaMinutes: int, timeLapse: str) -> pd.DataFrame:

    result = []
    
    for date, group in df_data.groupby(df_data["dates (Y-M-D hh:mm:ss)"].dt.to_period(timeLapse[0].upper())):
        if getTimeDimensionCheck(group, deltaMinutes, timeLapse, date):
            dataAnalysis = getDataAnalysis(group, deltaMinutes, timeLapse, date)

            result.append(dataAnalysis)

    if len(result) != 0:
        return pd.DataFrame(result)

    return None

def toExcelAnalysis(df_data: pd.DataFrame, df_daily: pd.DataFrame, df_monthly: pd.DataFrame, df_annual: pd.DataFrame):

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_data.to_excel(writer, index=False, sheet_name="Data")

        if df_daily is not None:
            df_daily.to_excel(writer, index=False, sheet_name="DailyAnalysis")
        if df_monthly is not None:
            df_monthly.to_excel(writer, index=False, sheet_name="MonthlyAnalysis")
        if df_annual is not None:
            df_annual.to_excel(writer, index=False, sheet_name="AnnualAnalysis")

    return output.getvalue()

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

def getConditionValidateEntries(validateEntries):

    bool_PV = validateEntries["check_PV"] and validateEntries["check_INV_PV"]
    bool_AERO = validateEntries["check_AERO"] and validateEntries["check_INV_AERO"]

    return validateEntries['check_DATA'] and (bool_PV or bool_AERO)

def getImputProcessComponentData(dictImput):

    dictOutput = {
        "PV_data": dictImput["PV_data"],
        "INVPV_data": dictImput["INVPV_data"],
        "AERO_data": dictImput["AERO_data"],
        "INVAERO_data": dictImput["INVAERO_data"],
        "rho": dictImput["rho"],
        "PVs": dictImput["PVs"],
        "PVp": dictImput["PVp"],
        "V_PCC": dictImput["V_PCC"],
        "numberPhases": dictImput["numberPhases"]
    }

    return dictOutput

#%% funtions streamlit

def get_widget_number_input(label: str, disabled: bool, variable: dict):

    return st.number_input(label=label, disabled=disabled, **variable)


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

def getDataCompValidation(uploadedYamlCOMP, uploadedYamlINV_COMP, optionsKeysUploadedCOMP, optionsKeysUploadedINVCOMP):

    check_COMP, check_INV_COMP, COMP_data, INVCOMP_data = False, False, False, False

    if uploadedYamlCOMP is None:
        st.error("Cargar **Datos del Módulo fotovoltaico**", icon="🚨")
    if uploadedYamlINV_COMP is None:
        st.error("Cargar **Datos del Inversor fotovoltaico**", icon="🚨")

    if uploadedYamlCOMP is not None and uploadedYamlINV_COMP is not None:
        try:
            COMP_data = yaml.safe_load(uploadedYamlCOMP)
            check_COMP = check_dict_input(COMP_data, optionsKeysUploadedCOMP)
        except:
            st.error("Error al cargar archivo **YAML** (.yaml)", icon="🚨")

        try:
            INVCOMP_data = yaml.safe_load(uploadedYamlINV_COMP)
            check_INV_COMP = check_dict_input(INVCOMP_data, optionsKeysUploadedINVCOMP)
        except:
            st.error("Error al cargar archivo **YAML** (.yaml)", icon="🚨")

    return check_COMP, check_INV_COMP, COMP_data, INVCOMP_data