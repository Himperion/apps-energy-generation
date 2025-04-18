# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import yaml, io, calendar
from datetime import datetime, timedelta
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode, StAggridTheme

from funtions import fun_app1, fun_app5, fun_app6, fun_app7, fun_app8, fun_app9

listGenerationOptions = ["Generación solar", "Generación eólica", "Respaldo grupo electrógeno"]

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

itemsOptionsColumnsDf = {
    "DATA": {
        "Dates": ["dates (Y-M-D hh:mm:ss)"],
        "Load" : ["Load(kW)"]
    },
    "PV" : {
        "Geff" : ["Gef(W/m^2)", "Gef(W/m²)", "Gin(W/m²)", "Gin(W/m^2)"],
        "Toper" : ["Toper(°C)"]
    },
    "AERO" : {
        "Vwind" : ["Vwind(m/s)", "Vwind 10msnm(m/s)", "Vwind 50msnm(m/s)"]
    }
}

dictPhases = {
    "Monofásico": {"Num": 1, "label": "1️⃣ Monofásico"},
    "Trifásico": {"Num": 3, "label": "3️⃣ Trifásico"}
}

googleSheetID = st.secrets.GOOGLE_DRIVE["googleSheetID"]

urlGoogleSheet = "https://docs.google.com/spreadsheets/d/{0}/export?format=csv&gid={1}&format"

dictGoogleSheet = {
    "PV": st.secrets.GOOGLE_DRIVE["googleSheetPV"],
    "INV_PV": st.secrets.GOOGLE_DRIVE["googleSheetINVPV"],
    "INV_AERO": st.secrets.GOOGLE_DRIVE["googleSheetINVAERO"],
    "BAT": st.secrets.GOOGLE_DRIVE["googleSheetBAT"],
    "GE": st.secrets.GOOGLE_DRIVE["googleSheetGE"],
    "AERO": st.secrets.GOOGLE_DRIVE["googleSheetAERO"],
    "RC": st.secrets.GOOGLE_DRIVE["googleSheetRC"]
    }

listMonths = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

#%% funtions

def changeUnitsK(K, Base):
    
    return (Base*K)/100

def getGoogleSheetUrl(sheetName):

    return urlGoogleSheet.format(googleSheetID, dictGoogleSheet[sheetName])

def getDataComponent(sheetLabel: str, dir: str, onLine: bool) -> pd.DataFrame:

    if onLine:
        sheetUrl = getGoogleSheetUrl(sheetName=sheetLabel)
        df_data = pd.read_csv(sheetUrl)
    else:
        df_data = pd.read_excel(dir, sheet_name=sheetLabel)

    return df_data

def nameFileHead(name: str) -> str:
    now = datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def fromValueLabelGetKey(dict_in: dict, key_label: str, value_label: str) -> str:

    for key, value in dict_in.items():
        if value[key_label] == value_label:
            return key

    return

def getLabelColumn(params: dict, key: str) -> str:

    if params[key]['unit'] == "":
        label_column = str(params[key]['label'])
    else:
        label_column = f"{params[key]['label']} {params[key]['unit']}"

    return label_column

def fixDataTypeList(value: str):

    listOut = []

    if value.count("/") > 0:
        listOut = [float(item) for item in value.split("/")]

    return listOut

def selectedRowColumn(selected_row: pd.DataFrame, params: dict, key: str):

    column_name = getLabelColumn(params, key)
    value = selected_row.loc[0, column_name]

    if value is None:
        output_value = None
    else:
        if params[key]["data_type"] == "int":
            output_value = int(value)
        elif params[key]["data_type"] == "float":
            if type(value) is str:
                if value.count(",") == 1 and value.count(".") == 0:
                    output_value = float(value.replace(",", "."))
                else:
                    output_value = float(value)
            else:
                output_value = float(value)
        elif params[key]["data_type"] == "str":
            output_value = str(value)
        elif params[key]["data_type"] == "list":
            output_value = fixDataTypeList(value)
        else:
            st.text(f" -- {key}: {value}")
    
    return output_value

def getBytesYaml(dictionary: dict):

    yaml_data = yaml.dump(dictionary, allow_unicode=True)
    buffer = io.BytesIO()
    buffer.write(yaml_data.encode('utf-8'))
    buffer.seek(0)

    return buffer

def getLabelParams(dict_param: dict) -> str:

    return f"**{dict_param['label']}:** {dict_param['description']} {dict_param['unit']}"

def getGlobalVariablesPV():
    params_PV, rename_PV, showOutputPV = None, None, None

    with open("files//[PV] - params.yaml", 'r') as archivo:
        params_PV = yaml.safe_load(archivo)

    with open("files//[PV] - dict_replace.yaml", 'r') as archivo:
        rename_PV = yaml.safe_load(archivo)

    if params_PV is not None:
        showOutputPV = [f"{params_PV[elm]['label']}{params_PV[elm]['unit']}: {params_PV[elm]['description']}" for elm in ["Voc", "Isc", "Impp", "Vmpp", "Pmpp"]]

    return params_PV, rename_PV, showOutputPV

def checkDictInput(dictionary: dict, options) -> bool:

    return all([key in options for key in dictionary])

def getCompValidation(uploadedYaml, optionsKeys):

    check, data = False, False

    if uploadedYaml is not None:
        try:
            data = yaml.safe_load(uploadedYaml)
            check = checkDictInput(data, optionsKeys)
        except:
            st.error("Error al cargar archivo **YAML** (.yaml)", icon="🚨")

    return check, data

def getDataOnGridCompValidation(uploadedYamlCOMP, uploadedYamlINV_COMP,
                                optKeysCOMP: list, optKeysINVCOMP: list, typeOfSystem: str):
    
    check, data = {}, {}

    check["check_COMP"], data["COMP_data"] = getCompValidation(uploadedYamlCOMP, optKeysCOMP)               # COMP
    check["check_INVCOMP"], data["INVCOMP_data"] = getCompValidation(uploadedYamlINV_COMP, optKeysINVCOMP)  # INV_COMP
    
    return check, data

def getDataOnGridValidation(uploadedYamlCOMP, uploadedYamlINV_COMP, validateEntries: dict, typeOfSystem: str):

    if typeOfSystem == "PV":
        check, data = getDataOnGridCompValidation(uploadedYamlCOMP, uploadedYamlINV_COMP,
                                                  optKeysPV, optKeysINVCOMP, typeOfSystem)
        
        validateEntries["check_PV"] = check["check_COMP"]
        validateEntries["check_INVPV"] = check["check_INVCOMP"]

    if typeOfSystem == "AERO":
        check, data = getDataOnGridCompValidation(uploadedYamlCOMP, uploadedYamlINV_COMP,
                                                   optKeysAERO, optKeysINVCOMP, typeOfSystem)
        
        validateEntries["check_AERO"] = check["check_COMP"]
        validateEntries["check_INVAERO"] = check["check_INVCOMP"]

    return validateEntries, data["COMP_data"], data["INVCOMP_data"]

def getDataOffGridCompValidation(uploadedYamlCOMP, uploadedYamlINV_COMP, uploadedYamlRC_COMP,
                                 optKeysCOMP, optKeysINVCOMP, optKeysRCCOMP, typeOfSystem):
    
    check, data = getDataOnGridCompValidation(uploadedYamlCOMP, uploadedYamlINV_COMP, optKeysCOMP, optKeysINVCOMP, typeOfSystem)

    check["check_RCCOMP"], data["RCCOMP_data"] = getCompValidation(uploadedYamlRC_COMP, optKeysRCCOMP)      # RC_COMP

    return check, data

def getDataOffGridValidation(uploadedYamlCOMP, uploadedYamlINV_COMP, uploadedYamlRC_COMP, validateEntries: dict, typeOfSystem: str):
    
    if typeOfSystem == "PV":
        check, data = getDataOffGridCompValidation(uploadedYamlCOMP, uploadedYamlINV_COMP, uploadedYamlRC_COMP,
                                                   optKeysPV, optKeysINVCOMP, optKeysRCCOMP, typeOfSystem)

        validateEntries["check_PV"] = check["check_COMP"]
        validateEntries["check_INVPV"] = check["check_INVCOMP"]
        validateEntries["check_RCPV"] = check["check_RCCOMP"]

    if typeOfSystem == "AERO":
        check, data = getDataOffGridCompValidation(uploadedYamlCOMP, uploadedYamlINV_COMP, uploadedYamlRC_COMP,
                                                   optKeysAERO, optKeysINVCOMP, optKeysRCCOMP, typeOfSystem)
        
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

def getListGenerationOptions(generationType: str) -> list:

    if generationType == "OnGrid":
        listOut = listGenerationOptions[:-1]
    elif generationType == "OffGrid":
        listOut = listGenerationOptions
    else:
        listOut = []

    return listOut

def getDictValidateComponent(validateEntries: dict, generationType: str) -> dict:

    validateComponents = {}

    if generationType == "OnGrid" or generationType == "OffGrid":
        validateComponents["validateDATA"] = validateEntries["check_DATA"]
        validateComponents["validatePV"] = all([validateEntries["check_PV"], validateEntries["check_INVPV"]])
        validateComponents["validateAERO"] = all([validateEntries["check_AERO"], validateEntries["check_INVAERO"]])
    if generationType == "OffGrid":
        validateComponents["validatePV"] = all([validateComponents["validatePV"], validateEntries["check_RCPV"]])
        validateComponents["validateAERO"] = all([validateComponents["validateAERO"], validateEntries["check_RCAERO"]])
        validateComponents["validateGE"] = validateEntries["check_GE"]
        validateComponents["validateBAT"] = validateEntries["check_BAT"]

    return validateComponents

def getDictComponentInTheProject(generationOptions: list) -> dict:

    listKeys = [("generationPV", listGenerationOptions[0]),
                ("generationAERO", listGenerationOptions[1]),
                ("generationGE", listGenerationOptions[2])]
    
    componentInTheProject = {}

    for i in range(0,len(listKeys),1):
        if listKeys[i][1] in generationOptions:
            boolValue = True
        else:
            boolValue = False

        componentInTheProject[listKeys[i][0]] = boolValue

    return componentInTheProject

def getImputProcessComponentData(dictImput: dict, dataKeyList: list) -> dict:

    dictOutput = {}

    for i in range(0,len(dataKeyList),1):
        dictOutput[dataKeyList[i]] = dictImput[dataKeyList[i]]

    return dictOutput

def getErrorForMissingComponent(uploadedYamlPV, uploadedYamlINV_PV, uploadedYamlRC_PV,
                                uploadedYamlAERO, uploadedYamlINV_AERO, uploadedYamlRC_AERO,
                                uploadedXlsxDATA, uploadedYamlGE, uploadedYamlBAT,
                                generationType: str, componentInTheProject: dict):

    boolOut = True
    boolOut = getErrorForMissingItem(uploadedYamlItem=uploadedXlsxDATA, labelItem="Datos de carga, temperatura de operación y potencial energetico del sitio", boolItem=boolOut)

    if componentInTheProject["generationPV"] and boolOut:
        if generationType == "OnGrid" or generationType == "OffGrid":
            boolOut = getErrorForMissingItem(uploadedYamlItem=uploadedYamlPV, labelItem="Módulo fotovoltaico", boolItem=boolOut)
            boolOut = getErrorForMissingItem(uploadedYamlItem=uploadedYamlINV_PV, labelItem="Inversor fotovoltaico", boolItem=boolOut)
        if generationType == "OffGrid":
            boolOut = getErrorForMissingItem(uploadedYamlItem=uploadedYamlRC_PV, labelItem="Regulador de carga solar", boolItem=boolOut)

    if componentInTheProject["generationAERO"] and boolOut:
        if generationType == "OnGrid" or generationType == "OffGrid":
            boolOut = getErrorForMissingItem(uploadedYamlItem=uploadedYamlAERO, labelItem="Módulo eólico", boolItem=boolOut)
            boolOut = getErrorForMissingItem(uploadedYamlItem=uploadedYamlINV_AERO, labelItem="Inversor eólico", boolItem=boolOut)
        if generationType == "OffGrid":
            boolOut = getErrorForMissingItem(uploadedYamlItem=uploadedYamlRC_AERO, labelItem="Regulador de carga eólico", boolItem=boolOut)

    if componentInTheProject["generationGE"] and generationType == "OffGrid" and boolOut:
        boolOut = getErrorForMissingItem(uploadedYamlItem=uploadedYamlGE, labelItem="Grupo electrógeno", boolItem=boolOut)

    if generationType == "OffGrid" and boolOut:
        boolOut = getErrorForMissingItem(uploadedYamlItem=uploadedYamlBAT, labelItem="Banco de baterías", boolItem=boolOut)

    return boolOut

def initializeDictValidateEntries(generationType: str):

    validateEntries = {}

    if generationType == "OnGrid" or generationType == "OffGrid":
        validateEntries["check_DATA"] = False
        validateEntries["check_PV"] = False
        validateEntries["check_INVPV"] = False
        validateEntries["check_AERO"] = False
        validateEntries["check_INVAERO"] = False

    if generationType == "OffGrid":
        validateEntries["check_RCPV"] = False
        validateEntries["check_RCAERO"] = False
        validateEntries["check_BAT"] = False
        validateEntries["check_GE"] = False

    return validateEntries

def checkDataframeInput(dataframe: pd.DataFrame, options: dict):

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

def checkDataframesProject(df_data, componentInTheProject):

    check_PV, check_AERO = False, False
    columnsOptionsData = {}

    df_data, check_DATA, columnsOptionsData["DATA"] = checkDataframeInput(df_data, itemsOptionsColumnsDf["DATA"])

    if componentInTheProject["generationPV"]:   # Generación PV
        df_data, check_PV, columnsOptionsData["PV"] = checkDataframeInput(df_data, itemsOptionsColumnsDf["PV"])

    if componentInTheProject["generationAERO"]:   # Generación AERO
        df_data, check_AERO, columnsOptionsData["AERO"] = checkDataframeInput(df_data, itemsOptionsColumnsDf["AERO"])

    return check_DATA, check_PV, check_AERO, columnsOptionsData

def getCheckValidateGeneration(generationPV, generationAERO, generationGE, validateDATA, validatePV, validateAERO, validateGE, validateBAT, generationType):

    checkProject = False
    
    if generationType == "OffGrid":
        validateAUX = validateBAT
    elif generationType == "OnGrid":
        validateAUX = True
    else:
        validateAUX = False

    # Solo generación solar
    if generationPV and not generationAERO and validatePV and validateAUX:
        checkProject = True
    # Solo generación eólica
    elif not generationPV and generationAERO and validateAERO and validateAUX:
        checkProject = True
    # Generación solar  y eólica
    elif generationPV and generationAERO and validatePV and validateAERO and validateAUX:
        checkProject = True

    # Respaldo grupo electrógeno
    if generationGE:
        checkProject = checkProject and validateGE
    else:
        checkProject = checkProject and not validateGE

    checkProject = checkProject and validateDATA

    return checkProject

def getNumberPhases(INVPV_data, INVAERO_data, GE_data) -> int:

    numberPhases = None

    if INVPV_data is not None and INVAERO_data is None:
        numberPhases = dictPhases[INVPV_data['phases']]['Num']
    elif INVPV_data is None and INVAERO_data is not None:
        numberPhases = dictPhases[INVAERO_data['phases']]['Num']
    else:
        numberPhasesPV = dictPhases[INVPV_data['phases']]['Num']
        numberPhasesAERO = dictPhases[INVAERO_data['phases']]['Num']

        if numberPhasesPV == numberPhasesAERO:
            numberPhases = numberPhasesPV

    if GE_data is not None and numberPhases is not None:
        numberPhasesGE = dictPhases[GE_data['phases']]['Num']

        if numberPhases != numberPhasesGE:
            numberPhases = None
        
    return numberPhases

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

def getDataframeGE(df_data: pd.DataFrame, GE_data: dict, columnsOptionsData) -> pd.DataFrame:

    In_GE, Ra_GE, GE_dictPU = fun_app7.get_param_gp(GE_data, dictPhases)

    optionsList = {"Load": [columnsOptionsData["DATA"]["Load"]]}

    df_data, check, columnsOptionsSel = checkDataframeInput(dataframe=df_data, options=optionsList)
    
    df_data = fun_app7.getDataframeGE(dataframe=df_data,
                                      dict_pu=GE_dictPU,
                                      dict_param=GE_data,
                                      columnsOptionsSel={"Load": columnsOptionsData["DATA"]["Load"]})

    return df_data

def getDataframePV(df_data: pd.DataFrame,
                   PV_data: dict,
                   INVPV_data: dict,
                   PVs: int, PVp: int,
                   columnsOptionsData: list,
                   params_PV: dict, rename_PV: dict,
                   showOutputPV: list,
                   numberPhases: int):

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

def initializeDataFrameColumns(df_grid: pd.DataFrame, generationType: str) -> pd.DataFrame:

    df_grid["Pgen_PV(kW)"] = 0.0
    df_grid["Pgen_AERO(kW)"] = 0.0

    if generationType == "OnGrid":
        
        df_grid["PinvAC_PV(kW)"] = 0.0
        df_grid["VinvAC_PV(V)"] = 0.0
        df_grid["IinvAC_PV(A)"] = 0.0

        df_grid["PinvAC_AERO(kW)"] = 0.0
        df_grid["VinvAC_AERO(V)"] = 0.0
        df_grid["IinvAC_AERO(A)"] = 0.0

        df_grid["Vload(V)"] = 0.0
        df_grid["Iload(A)"] = 0.0

        df_grid["Pdem(kW)"] = 0.0
        df_grid["Vdem(V)"] = 0.0
        df_grid["Idem(A)"] = 0.0

    elif generationType == "OffGrid":

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

        df_grid["Ia_GE(A)"] = 0.0
        df_grid["Vt_GE(V)"] = 0.0
        df_grid["Consumo_GE(l/h)"] = 0.0
        df_grid["Eficiencia_GE(%)"] = 0.0

    return df_grid

def getAddUniqueColumnsOptionsData(TOTAL_data: dict, columnsOptionsData: dict):

    for key, value in columnsOptionsData.items():
        for subKey, subValue in value.items():
            TOTAL_data[f"[columnsOptionsData] {key}-{subKey}"] = subValue

    return TOTAL_data

def proccesComponentData(TOTAL_data: dict, COMP_data: dict, INV_data: dict, RC_data: dict, AddText: str, generationType: str):

    if generationType == "OnGrid":
        auxListString1 = ["{0}_data", "INV{0}_data"]
        auxListDict = [COMP_data, INV_data]
    elif generationType == "OffGrid":
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

def getFixFormatDictParams(TOTAL_data: dict, dataKeyList: list):
              
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

    for i in range(0,len(dataKeyList),1):
        if not dataKeyList[i] in dictOut:
            dictOut[dataKeyList[i]] = None

    for key, value in dictOut.items():
        if type(value) is dict:
            value = consolidationOfKeyIntoList(DICT_data=value)

    return dictOut

def getBytesFileYamlComponentsProject(dictDataProject: dict) -> bytes:

    dictDataProjectCopy = dictDataProject.copy()

    if "df_data" in dictDataProjectCopy:
        del dictDataProjectCopy["df_data"]

    bufferData = getBytesYaml(dictionary=dictDataProjectCopy)

    return bufferData

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

def getAnalysisInTime(df_data: pd.DataFrame, deltaMinutes: int, timeLapse: str, generationType: str) -> pd.DataFrame:

    result = []
    
    for date, group in df_data.groupby(df_data["dates (Y-M-D hh:mm:ss)"].dt.to_period(timeLapse[0].upper())):
        if getTimeDimensionCheck(group, deltaMinutes, timeLapse, date):

            if generationType == "OnGrid":
                dataAnalysis = fun_app8.getDataAnalysisOnGrid(group, deltaMinutes, timeLapse, date)
            elif generationType == "OffGrid":
                dataAnalysis = fun_app9.getDataAnalysisOffGrid(group, deltaMinutes, timeLapse, date)

            result.append(dataAnalysis)

    if len(result) != 0:
        return pd.DataFrame(result)

    return None

def toExcelResults(df: pd.DataFrame, dictionary: dict | None, df_sheetName: str, dict_sheetName: str | None) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=df_sheetName)
        if dictionary is not None:
            df_params = pd.DataFrame(dictionary, index=[0])
            df_params.to_excel(writer, index=False, sheet_name=dict_sheetName)

    return output.getvalue()

def toExcelAnalysis(df_data: pd.DataFrame, dictionary: dict, df_daily: pd.DataFrame, df_monthly: pd.DataFrame, df_annual: pd.DataFrame):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_data.to_excel(writer, index=False, sheet_name="Data")

        if dictionary is not None:
            df_params = pd.DataFrame(dictionary, index=[0])
            df_params.to_excel(writer, index=False, sheet_name="Params")
        if df_daily is not None:
            df_daily.to_excel(writer, index=False, sheet_name="DailyAnalysis")
        if df_monthly is not None:
            df_monthly.to_excel(writer, index=False, sheet_name="MonthlyAnalysis")
        if df_annual is not None:
            df_annual.to_excel(writer, index=False, sheet_name="AnnualAnalysis")

    return output.getvalue()

def uploadedXlsxSheetToDict(uploaderXlsx, sheet_name: str, dataKeyList: list) -> dict:

    TOTAL_data = pd.read_excel(uploaderXlsx, sheet_name=sheet_name).to_dict(orient="records")[0]

    return getFixFormatDictParams(TOTAL_data, dataKeyList)

def totalDataToDictParams(uploaderAnalysisXlsx, dataKeyList) -> dict:

    dict_params = uploadedXlsxSheetToDict(uploaderXlsx=uploaderAnalysisXlsx, sheet_name="Params", dataKeyList=dataKeyList)

    return dict_params

def getListOfTimeRanges(deltaMinutes: float) -> list:

    listTimeRanges = []
    timeDelta = timedelta(minutes=deltaMinutes)
    time = timedelta(hours=0.0, minutes=0.0, seconds=0.0)

    while time < timedelta(days=1.0):
        listTimeRanges.append(str(time))
        time = timeDelta + time

    return listTimeRanges

def getAnalizeTime(data_date: datetime.date, data_time: datetime.time):

    return datetime.combine(data_date, data_time)

def getNodeParametersOnGrid(df_dataFilter: pd.DataFrame):

    round_decimal = 3

    dictNodes = {
        "node1": {
            "Pn1 (kW)": round(df_dataFilter.iloc[0]["Pgen_PV(kW)"], round_decimal),
            "Vn1 (V)": round(df_dataFilter.iloc[0]["Vmpp_PV(V)"], round_decimal),
            "In1 (A)": round(df_dataFilter.iloc[0]["Impp_PV(A)"], round_decimal),
        },
        "node2": {
            "Pn2 (kW)": round(df_dataFilter.iloc[0]["Pgen_PV(kW)"], round_decimal),
            "Vn2 (V)": round(df_dataFilter.iloc[0]["Vmpp_PV(V)"], round_decimal),
            "In2 (A)": round(df_dataFilter.iloc[0]["Impp_PV(A)"], round_decimal),
        },
        "node3": {
            "Pn3 (kW)": round(df_dataFilter.iloc[0]["PinvAC_PV(kW)"], round_decimal),
            "Vn3 (V)": round(df_dataFilter.iloc[0]["VinvAC_PV(V)"], round_decimal),
            "In3 (A)": round(df_dataFilter.iloc[0]["IinvAC_PV(A)"], round_decimal),
        },
        "node4": {
            "Pn4 (kW)": round(df_dataFilter.iloc[0]["Pdem(kW)"], round_decimal),
            "Vn4 (V)": round(df_dataFilter.iloc[0]["Vdem(V)"], round_decimal),
            "In4 (A)": round(df_dataFilter.iloc[0]["Idem(A)"], round_decimal),
        },
        "node5": {
            "Pn5 (kW)": round(df_dataFilter.iloc[0]["Pgen_AERO(kW)"], round_decimal),
        },
        "node6": {
            "Pn6 (kW)": round(df_dataFilter.iloc[0]["PinvAC_AERO(kW)"], round_decimal),
            "Vn6 (V)": round(df_dataFilter.iloc[0]["VinvAC_AERO(V)"], round_decimal),
            "In6 (A)": round(df_dataFilter.iloc[0]["IinvAC_AERO(A)"], round_decimal),
        },
        "node7": {
            "Pn4 (kW)": round(df_dataFilter.iloc[0]["Load(kW)"], round_decimal),
            "Vn4 (V)": round(df_dataFilter.iloc[0]["Vload(V)"], round_decimal),
            "In4 (A)": round(df_dataFilter.iloc[0]["Iload(A)"], round_decimal),
        }      
    }

    return dictNodes

def getDictNodeValue(df: pd.DataFrame, listLabelColumns: list, round_decimal: int, num_node: int) -> dict:

    nodeX = {
        f"Pn{num_node} (kW)": round(df.iloc[0][listLabelColumns[0]], round_decimal),
        f"Vn{num_node} (V)": round(df.iloc[0][listLabelColumns[1]], round_decimal),
        f"In{num_node} (A)": round(df.iloc[0][listLabelColumns[2]], round_decimal)
    }

    return nodeX

def getDictNodeParams(df: pd.DataFrame, listLabelColumns: list, round_decimal: int, num_node: int, position: tuple) -> dict:

    dictNode = {}
    dictNode["value"] = getDictNodeValue(df, listLabelColumns, round_decimal, num_node)
    dictNode["position"] = position
    dictNode["num_node"] = num_node

    return dictNode

def timeInfoMonthsGetLabels(timeInfoMonths: list) -> list:

    listLabesMonths = []

    for i in range(0,len(timeInfoMonths),1):
        listAux = []
        for j in range(0,len(timeInfoMonths[i]),1):
            listAux.append(listMonths[j])
        listLabesMonths.append(listAux)
        
    return listLabesMonths

def fromMonthGetIndex(month):

    return listMonths.index(month) + 1

def getDictDataRow(selected_row: pd.DataFrame, key: str):

    return fun_app1.get_dict_data(selected_row, key)

#%% funtions streamlit

def getWidgetNumberInput(label: str, disabled: bool, key: str, variable: dict):

    return st.number_input(label=label, disabled=disabled, key=key, **variable)

def getParamsWidgetNumberInput(dictParam:dict, key:str, disabled: bool):

    dictOut = {
        "label": getLabelParams(dict_param=dictParam),
        "disabled": disabled,
        "key": key,
        "variable": dictParam["number_input"]
    }

    return dictOut

def widgetNumberImput(dictParam:dict, key:str, disabled: bool):

    return getWidgetNumberInput(**getParamsWidgetNumberInput(dictParam=dictParam, key=key, disabled=disabled))            

def excelDownloadButton(bytesFileExcel, file_name):

    df_download = st.download_button(
        label=f"📄 Descargar **:blue[{file_name}] XLSX**",
        data=bytesFileExcel,
        file_name=nameFileHead(name=f"{file_name}.xlsx"),
        mime='xlsx')

    return df_download

def yamlDownloadButton(bytesFileYaml, file_name, label):

    buttonDownload = st.download_button(
        label=label,
        data=bytesFileYaml,
        file_name=nameFileHead(name=f"{file_name}.yaml"),
        mime="text/yaml")

    return buttonDownload

def getErrorForMissingItem(uploadedYamlItem, labelItem, boolItem):

    if uploadedYamlItem is None and boolItem:
        st.error(f"Cargar **Datos del {labelItem}**", icon="🚨")
        boolItem = False

    return boolItem

def getDataValidation(uploadedXlsxDATA, componentInTheProject):

    check_OUT, df_data, columnsOptionsData = False, None, None

    try:
        df_data = pd.read_excel(uploadedXlsxDATA)
        check_DATA, check_PV, check_AERO, columnsOptionsData = checkDataframesProject(df_data, componentInTheProject)
        check_OUT = check_DATA and (check_PV or check_AERO)

        if not check_OUT:
            st.error("Error al cargar archivo (pueden faltar variables para su ejecución) **EXCEL** (.xlsx)", icon="🚨")
    except:
        st.error("Error al cargar archivo **EXCEL** (.xlsx)", icon="🚨")

    return check_OUT, df_data, columnsOptionsData

def getColForLength(length):

    if length == 1:
        col1 = st.columns(1)
        return [col1]
    elif length == 2:
        col1, col2 = st.columns(2)
        return [col1, col2]
    elif length == 3:
        col1, col2, col3 = st.columns(3)
        return [col1, col2, col3]

    return

def getPrintParamsDataframe(dataframe: pd.DataFrame, params_label: list, dict_param: dict, head_column: list):

    dataframe = dataframe[params_label]
    colors_string = [":grey[{0}]", ":blue[{0}]", ":red[{0}]"]

    with st.container(border=True):
        list_columns_title = getColForLength(len(head_column))

        for i in range(0,len(head_column),1):
            list_columns_title[i].markdown(f"**{colors_string[i].format(head_column[i])}**")

        for i in range(0,len(params_label),1):
            label = getLabelParams(dict_param=dict_param[params_label[i]])

            list_columns = getColForLength(len(head_column))

            list_columns[0].markdown(colors_string[0].format(label))

            for index, row in dataframe.iterrows():
                list_columns[index+1].markdown(colors_string[index+1].format(row[params_label[i]]))
                
    return

def getNodeVisualization(dictNode: dict, nodeNum: int):

    with st.container(border=True):
        st.markdown(f"**:blue[Node {nodeNum}]**")
        for key, value in dictNode.items():
            st.caption(f"**{key}**: {value}")

    return

def printData(dataframe: pd.DataFrame, columns_print: list):

    with st.container(border=True):

        for i in range(0,len(columns_print),1):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**:blue[{columns_print[i]}:]**")
            with col2:
                st.markdown(dataframe.loc[dataframe.index[0], columns_print[i]])

    return

def printDataFloat(dataframe: pd.DataFrame, columns_print: list, round_int: int):

    with st.container(border=True):

        for i in range(0,len(columns_print),1):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**:blue[{columns_print[i]}:]**")
            with col2:
                st.markdown(round(float(dataframe.loc[dataframe.index[0], columns_print[i]]), round_int))

    return

def dataframe_AgGrid(dataframe: pd.DataFrame, height: int) -> pd.DataFrame:

    gb = GridOptionsBuilder.from_dataframe(dataframe)
    gb.configure_selection(selection_mode="single", use_checkbox=True)
    gb.configure_side_bar()
    gridOptions = gb.build()

    data = AgGrid(dataframe,
                  gridOptions=gridOptions,
                  enable_enterprise_modules=True,
                  allow_unsafe_jscode=True,
                  update_mode=GridUpdateMode.SELECTION_CHANGED,
                  columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                  height=height)
    
    """
    custom_theme = (
        StAggridTheme(base="balham").withParams({"fontSize": 16,
                                                 "rowBorder": False,
                                                 "backgroundColor": "#FFFFFF"}).withParts(['iconSetMaterial'])
            )
    """
    


    return data["selected_rows"]