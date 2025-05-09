# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import yaml, io, calendar, tomllib
import plotly.express as px
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode, StAggridTheme
from streamlit_pdf_viewer import pdf_viewer

from funtions import fun_app1, fun_app5, fun_app6, fun_app7, fun_app8, fun_app9

with open("files//[CONN] - GoogleSheet.toml", "rb") as f:
    gd = tomllib.load(f)

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

googleSheetID = gd["GOOGLE_DRIVE"]["googleSheetID"]

urlGoogleSheet = "https://docs.google.com/spreadsheets/d/{0}/export?format=csv&gid={1}&format"

dictGoogleSheet = {
    "PV": gd["GOOGLE_DRIVE"]["googleSheetPV"],
    "INV_PV": gd["GOOGLE_DRIVE"]["googleSheetINVPV"],
    "INV_AERO": gd["GOOGLE_DRIVE"]["googleSheetINVAERO"],
    "BAT": gd["GOOGLE_DRIVE"]["googleSheetBAT"],
    "GE": gd["GOOGLE_DRIVE"]["googleSheetGE"],
    "AERO": gd["GOOGLE_DRIVE"]["googleSheetAERO"],
    "RC": gd["GOOGLE_DRIVE"]["googleSheetRC"]
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

def fromLabelObtainNumberOf(label):

    return dictPhases[label]["Num"]

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

        df_grid["Pbb_PV(kW)"] = 0.0
        df_grid["IbbDC_PV(A)"] = 0.0

        df_grid["Pbb_AERO(kW)"] = 0.0
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
        df_grid["conNORMAL(t)"] = False
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

def getGenerationSystemsNotationLabel(generationPV: bool, generationAERO: bool, generationGE: bool):

    if generationPV and not generationAERO and not generationGE:        # PV
        key = "PV"
    elif not generationPV and generationAERO and not generationGE:      # AERO
       key = "AERO"
    elif generationPV and not generationAERO and generationGE:          # PV-GE
        key = "PV-GE"
    elif not generationPV and generationAERO and generationGE:          # AERO-GE
        key ="AERO-GE"
    elif generationPV and generationAERO and not generationGE:          # PV-AERO
        key ="PV-AERO"
    elif generationPV and generationAERO and generationGE:              # PV-AERO-GE
        key ="PV-AERO-GE"

    return key

def getDictNodeValue(df: pd.DataFrame, listLabelColumns: list, round_decimal: int, num_node: int) -> dict:

    nodeX = {}
    dictKey = {0: ["P", "kW"], 1: ["V", "V"], 2: ["I", "A"]}

    for i in range(0,len(listLabelColumns),1):
        key = f"{dictKey[i][0]}n{num_node} ({dictKey[i][1]})"
        if listLabelColumns[i] is not None:
            value = round(df.iloc[0][listLabelColumns[i]], round_decimal)
        else:
            value = "No data"
        nodeX[key] = value

    return nodeX

def getKeyValueParam(select_param: str, num_node: int) -> str:

    if select_param == "P":
        keyValue = f"Pn{num_node} (kW)"
    elif select_param == "V":
        keyValue = f"Vn{num_node} (V)"
    else:
        keyValue = f"In{num_node} (A)"

    return keyValue

def getDictNodeParams(df: pd.DataFrame, listLabelColumns: list, round_decimal: int, num_node: int, position: tuple) -> dict:

    dictNode = {}
    dictNode["value"] = getDictNodeValue(df, listLabelColumns, round_decimal, num_node)
    dictNode["position"] = position
    dictNode["num_node"] = num_node

    return dictNode

def dictPositionInfoAddValues(df: pd.DataFrame, label_systems: str, columnsOptionsData: dict, round_decimal: int, generationType: str):

    if generationType == "OffGrid":
        with open("files//[OffGrid] - auxiliary_position.yaml", "r") as archivo:
            auxiliaryPositionInfo = yaml.safe_load(archivo)
    elif generationType == "OnGrid":
        with open("files//[OnGrid] - auxiliary_position.yaml", "r") as archivo:
            auxiliaryPositionInfo = yaml.safe_load(archivo)
    elif generationType == "GE":
        auxiliaryPositionInfo = {
            "GE": {"Consumo_GE": [26, 300]}
        }

    dict_info = auxiliaryPositionInfo[label_systems]

    for key, value in dict_info.items():
        dictAux = {"position": value}

        if key == "Geff":
            dictAux["value"] = round(float(df.iloc[0][columnsOptionsData["PV"]["Geff"]]), round_decimal)
            dictAux["label"] = "Irradiancia (W/m²)"
        elif key == "Toper":
            dictAux["value"] = round(float(df.iloc[0][columnsOptionsData["PV"]["Toper"]]), round_decimal)
            dictAux["label"] = "Temperatura de operación del panel (°C)"
        elif key == "Vwind":
            dictAux["value"] = round(float(df.iloc[0][columnsOptionsData["AERO"]["Vwind"]]), round_decimal)
            dictAux["label"] = "Velocidad del viento (m/s)"
        elif key == "Consumo_GE":
            dictAux["value"] = round(float(df.iloc[0]["Consumo_GE(l/h)"]), round_decimal)
            dictAux["label"] = "Consumo (l/h)"
        elif key == "SOC":
            dictAux["value"] = round(float(df.iloc[0]["SOC(t)"]), round_decimal)
            dictAux["label"] = "SOC"
        elif key == "conSD":
            dictAux["value"] = str(df.iloc[0]["conSD(t)"])
            dictAux["label"] = "Sobredescarga"
        elif key == "conSC":
            dictAux["value"] = str(df.iloc[0]["conSC(t)"])
            dictAux["label"] = "Sobrecarga"
        elif key == "swLoad":
            dictAux["value"] = int(df.iloc[0]["swLoad(t)"])
            dictAux["label"] = "SW"
        
        dict_info[key] = dictAux

    return dict_info

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

def get_df_plot(df: pd.DataFrame, time_info: dict, params_info: dict):

    dict_plot ={
        **{time_info["name"]: df[time_info["name"]]},
        **{value["label"]: df[key] for key, value in params_info.items()}
    }

    df_plot = pd.DataFrame(dict_plot)
    df_long = df_plot.melt(id_vars=time_info["name"], var_name="Serie", value_name="Value")

    return df_long

def get_color_discrete_map(params_info: dict):

    return {params_info[key]["label"]: params_info[key]["color"] for key in params_info}

def getSizesForPieChart(df: pd.DataFrame, list_params: list) -> list:

    return [df.loc[df.index[0], list_params[i]] for i in range(0,len(list_params),1)]

def get_dict_replace_date():

    listPrams = ["kWh", "h", "l", "%", "V", "A", "kW"]
    dictTimeReplace = {"day": "día", "month": "mes", "year": "año"}
    dictParamReplace = {"l": "L"}

    dict_replace_date = {}

    for i in range(0,len(listPrams),1):
        if listPrams[i] in dictParamReplace:
            paramReplace = dictParamReplace[listPrams[i]]
        else:
            paramReplace = listPrams[i]

        for key, value in dictTimeReplace.items():
            dict_replace_date[f"({listPrams[i]}/{key})"] = f" ({paramReplace}/{value})"

    return dict_replace_date

def fromParametersGetLabels(list_params: list):

    dict_replace_param = {
        "Eauto": "Autoconsumo",
        "Eexp": "Exportación",
        "Eimp": "Importación",
        "Exct1": "Excedentes tipo 1",
        "Exct2": "Excedentes tipo 2",
        "Egen_INVPV": "Generación fotovoltaica",
        "Egen_INVAERO": "Generación Eólica",
        "Egen": "Generación total",
        "Eload": "Demanda de la carga",
        "Edem": "Demanda neta a la red",
        "ErcDC_PV": "Generación Fotovoltaica",
        "ErcDC_AERO": "Generación Eólica",
        "Egen_PV": "Generación Fotovoltaica",
        "Egen_AERO": "Generación Eólica",
        "Eload_OffGrid": "Demanda suplida por el conjunto fotovoltaica/eólica/banco de baterías",
        "Eload_GE": "Demanda suplida por el  grupo electrógeno",
        "Eload_OffLine": "Demanda de la carga no atendida",
        "conNORMAL": "Normalidad del banco de baterías",
        "conSD": "Sobredescarga del banco de baterías",
        "conSC": "Sobrecarga del banco de baterías",
        "Ebb": "Energía neta del banco de baterías",
        "Ebb_absorbed": "Energía absorbida por el  banco de baterías",
        "Ebb_delivered": "Energía entregada por el banco de baterías",
        "swLoad_1": "SW=1",
        "swLoad_2": "SW=2",
        "swLoad_3": "SW=3",
        "Consumo_GE": "Consumo de combustible del grupo electrógeno",
        "Pdem_max": "Potencia máxima demandada",
        "Pdem_min": "Potencia mínima demandada",
        "Pdem_prom": "Potencia promedio demandada",
        "Vdem_max": "Tensión máxima demandada",
        "Vdem_min": "Tensión mínima demandada",
        "Vdem_prom": "Tensión promedio demandada",
        "Idem_max": "Corriente máxima demandada",
        "Idem_min": "Corriente mínima demandada",
        "Idem_prom": "Corriente promedio demandada",
        "EficienciaMax_GE": "Eficiencia máxima del grupo electrógeno",
        "EficienciaMin_GE": "Eficiencia mínima del grupo electrógeno",
        "EficienciaProm_GE": "Eficiencia promedio del grupo electrógeno",
        "OperGE": "Operación del grupo electrógeno",
        "OperGEmaxNom": "Operación del grupo electrógeno mayor a su potencia nominal",
        "OperGEminNom": "Operación del grupo electrógeno menor a su potencia nominal"
    }

    dict_replace_date = get_dict_replace_date()

    list_out = list_params.copy()

    for i in range(0,len(list_params),1):
        if list_params[i].count("(") == 1 and list_params[i].count(")"):
            stringAux = list_params[i].split("(")[0]
            if stringAux in dict_replace_param:
                list_out[i] = list_params[i].replace(stringAux, dict_replace_param[stringAux])
    
    for i in range(0,len(list_out),1):
        if list_out[i].count("(") == 1 and list_out[i].count(")"):
            if list_out[i].find("(") > 0:
                stringAux = list_out[i][list_out[i].find("("):list_out[i].find(")")+1]
                if stringAux in dict_replace_date:
                    list_out[i] = list_out[i].replace(stringAux, dict_replace_date[stringAux])

    return list_out

def reorderDictForindividualGraph(dictIG: dict) -> dict:

    dictReorderIG = {}

    for i in range(0,len(dictIG["column_name"]),1):
        dictAux = {}
        dictAux["value_label"] = dictIG["value_label"][i]
        dictAux["color"] = dictIG["color"][i]
        dictAux["xt"] = dictIG["xt"][i]
        dictAux["xrsv"] = dictIG["xrsv"][i]

        dictReorderIG[dictIG["column_name"][i]] = dictAux

    return dictReorderIG

def valueLabelGetTabs(dictIG: dict) -> dict:

    tabs_label = [f"{dictIG['icon'][i]} {dictIG['value_label'][i]}" for i in range(len(dictIG["column_name"]))]

    if len(tabs_label) == 2:
        tab1, tab2 = st.tabs(tabs_label)
        tabs_items = [tab1, tab2]
    elif len(tabs_label) == 3:
        tab1, tab2, tab3 = st.tabs(tabs_label)
        tabs_items = [tab1, tab2, tab3]
    elif len(tabs_label) == 4:
        tab1, tab2, tab3, tab4 = st.tabs(tabs_label)
        tabs_items = [tab1, tab2, tab3, tab4]
    elif len(tabs_label) == 5:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(tabs_label)
        tabs_items = [tab1, tab2, tab3, tab4, tab5]
    elif len(tabs_label) == 6:
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(tabs_label)
        tabs_items = [tab1, tab2, tab3, tab4, tab5, tab6]

    dictTabs = {}

    for i in range(0,len(dictIG["column_name"]),1):
        dictTabs[dictIG["column_name"][i]] = tabs_items[i]

    return dictTabs

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
        mime="text/yaml",
        on_click="ignore")

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
            col1, col2 = st.columns([0.8, 0.2])
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

    return data["selected_rows"]

def pieChartVisualizationStreamlit(sizes: list, labels: list, legend_title: str, colors: list, pull: list):
    
    fig = px.pie(
        names=labels,
        values=sizes
        )
    fig.update_traces(
        hovertemplate="%{label}<br>Valor: %{value:.3f}<br>Porcentaje: %{percent:.2%}<extra></extra>",
        marker=dict(colors=colors),
        texttemplate="%{percent:.2%}",
        textposition="inside",
        pull=pull
        )
    fig.update_layout(
        legend_title_text=legend_title,
        legend=dict(orientation="h")
        )
    config ={
        "displayModeBar": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["zoom", "pan", "hoverClosestCartesian", "hoverCompareCartesian", "sendDataToCloud"]
    }

    st.plotly_chart(fig, use_container_width=True, config=config)

    return

def plotVisualizationPxStreamlit(df: pd.DataFrame, time_info: dict, params_info: dict, value_label: str, serie_label: str, barmode="overlay", opacity=0.8):

    df_long = get_df_plot(df, time_info, params_info)

    fig = px.bar(
        df_long,
        x=time_info["name"], y="Value", color="Serie", barmode=barmode, opacity=opacity,
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
    
    config ={
        "displayModeBar": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["zoom", "pan", "hoverClosestCartesian", "hoverCompareCartesian", "sendDataToCloud",
                                   "zoomIn", "zoomOut", "lasso2d", "select2d"]
    }
    
    st.plotly_chart(fig, use_container_width=True, config=config)

    return

def individualGraph(df: pd.DataFrame, time_info: dict, column_name: str, value_label: str, color: str, xt: int, xrsv: bool):

    fig = px.line(df,
                  x=time_info["name"],
                  y=column_name,
                  markers=False,
                  color_discrete_sequence=[color],
                  labels={
                      "Value": value_label
                  }
    )

    q1, q2, q3 = df[column_name].quantile(0.25), df[column_name].median(), df[column_name].quantile(0.75)
    min_val, max_val = df[column_name].min(), df[column_name].max()

    fig.add_hline(y=q1, line_dash="dash", line_color="green",
                  annotation_text=f"Q1: {q1:.3f}", annotation_position="bottom right")
    fig.add_hline(y=q2, line_dash="dash", line_color="red",
                  annotation_text=f"Mediana: {q2:.3f}", annotation_position="top right")
    fig.add_hline(y=q3, line_dash="dash", line_color="blue",
                  annotation_text=f"Q3: {q3:.3f}", annotation_position="top right")
    fig.add_hline(y=min_val, line_dash="dot", line_color="purple",
                  annotation_text=f"Min: {min_val:.3f}", annotation_position="bottom left")
    fig.add_hline(y=max_val, line_dash="dot", line_color="orange",
                  annotation_text=f"Max: {max_val:.3f}", annotation_position="top left")
    
    fig.update_layout(
        xaxis_tickangle=-90,
        xaxis=dict(showgrid=True),
        yaxis=dict(tickformat=".3f", showgrid=True),  
        xaxis_title=time_info["label"],
        yaxis_title=value_label,
        xaxis_rangeslider_visible=xrsv
    )

    config ={
        "displayModeBar": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["zoom", "pan", "hoverClosestCartesian", "hoverCompareCartesian", "sendDataToCloud",
                                   "zoomIn", "zoomOut", "lasso2d", "select2d"]
    }

    fig.update_layout(xaxis_tickangle=xt, legend=dict(title="Condición:", orientation="h", y=10, yanchor="bottom"),
                      xaxis_rangeslider_visible=xrsv,
                      yaxis=dict(showgrid=False))

    st.plotly_chart(fig, use_container_width=True, config=config)

    return

def viewGeneratorSetParameters():

    return

def printDataFloatResult(df_current: pd.DataFrame, list_drop: list):

    columnsPrint = df_current.drop(list_drop, axis=1).columns.tolist()
    columnsPrintRename = fromParametersGetLabels(list_params=columnsPrint)
    dict_replace = {columnsPrint[i]: columnsPrintRename[i] for i in range(0,len(columnsPrint),1)}
    df_current = df_current.rename(columns=dict_replace)

    printDataFloat(dataframe=df_current, columns_print=columnsPrintRename, round_int=3)

    return

def addInformationSystemImage(img_path: str, dictNode: dict, dictInfo: dict, select_param: str, size: int):

    dictColor = {
        "P": (0, 128, 0, 255),      # green
        "V": (0, 0, 255, 255),      # blue
        "I": (255, 0, 0, 255)       # red
    }

    image = Image.open(img_path).convert("RGBA")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("font/Cabin-VariableFont_wdth,wght.ttf", size)

    for key, value in dictNode.items():
        position = (value["position"][0]-20, value["position"][1]-25)
        text = str(value["value"][getKeyValueParam(select_param, value["num_node"])])

        draw.text(position, text, font=font, fill=dictColor[select_param])

    for key, value in dictInfo.items():
        position = (value["position"][0], value["position"][1])
        text = f"{value['label']}: {value['value']}"

        draw.text(position, text, font=font, fill=(0, 0, 0, 255))

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    st.image(buffer, use_container_width=True)

    return

def getNodeParametersGenerationType(df_datatime: pd.DataFrame, numberPhases: int, round_decimal: int, label_systems: str, generationType: str):

    dictNode = {}

    if generationType == "OffGrid":
        dictNode = fun_app9.getNodeParametersOffGrid(df_datatime, numberPhases, round_decimal, label_systems)
    elif generationType == "OnGrid":
        dictNode = fun_app8.getNodeParametersOnGrid(df_datatime, numberPhases, round_decimal, label_systems)
    elif generationType == "GE":
        dictNode = fun_app7.getNodeParametersGE(df_datatime, round_decimal, label_systems)

    return dictNode

def get_df_datatime(df_data: pd.DataFrame, data_date, data_time):

    pf_datetime = getAnalizeTime(data_date=data_date, data_time=data_time)
    df_datatime = df_data[df_data["dates (Y-M-D hh:mm:ss)"] == pf_datetime].copy()

    return df_datatime

def displayInstantResults(df_data: pd.DataFrame, PARAMS_data: dict, pf_date: datetime.date, pf_time: datetime.time, label_systems: str):

    numberPhases, round_decimal = PARAMS_data["numberPhases"], 4

    df_datatime = get_df_datatime(df_data, pf_date, pf_time)

    dictNode = getNodeParametersGenerationType(df_datatime, numberPhases, round_decimal, label_systems, PARAMS_data["generationType"])
    dictInfo = dictPositionInfoAddValues(df_datatime, label_systems, PARAMS_data["columnsOptionsData"], round_decimal, PARAMS_data["generationType"])

    size = 14

    if PARAMS_data["generationType"] == "OffGrid":
        img_path = f"images/app9/{label_systems}.png"
    elif PARAMS_data["generationType"] == "OnGrid":
        img_path = f"images/app8/{label_systems}.png"
    elif PARAMS_data["generationType"] == "GE":
        img_path, size = f"images/app7/{label_systems}.png", 22

    tab1, tab2, tab3 = st.tabs(["💡 Potencia (kW)", "🔋 Tensión (V)", "🔌 Corriente (A)"])

    with tab1:
        addInformationSystemImage(img_path, dictNode, dictInfo, "P", size)
    with tab2:
        addInformationSystemImage(img_path, dictNode, dictInfo, "V", size)
    with tab3:
        addInformationSystemImage(img_path, dictNode, dictInfo, "I", size)

    return

def infographicViewer(infographic_path: str, infographic_label: str):

    pdf_viewer(infographic_path, pages_vertical_spacing=0)

    with open(infographic_path, "rb") as f:
        pdf_bytes = f.read()

    st.download_button(
        label="⬇️ Descargar infografía",
        data=pdf_bytes,
        file_name=f"{infographic_label}.pdf",
        mime="application/pdf"
        )

    return
