import numpy as np
import pandas as pd
import streamlit as st
import datetime as dt
import matplotlib.pyplot as plt
from io import BytesIO
import yaml

#%% funtions general

def name_file_head(name: str) -> str:
    now = dt.datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def get_label_params(dict_param: dict) -> str:
    return f"**{dict_param['label']}:** {dict_param['description']} {dict_param['unit']}"

def from_value_label_get_key(dict_in: dict, value_label: str) -> str:

    for key, value in dict_in.items():
        if value["label"] == value_label:
            return key

    return

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

    st.text(dataframe.columns)
    st.text(f"columnsOptionsSel: {columnsOptionsSel}")

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
            Ia_PU, Vt_PU, consumption, efficiency = getParamsIaVtGE(row, dict_pu)

            dataframe.loc[index, "Ia_GE(A)"] = Ia_PU*dict_pu["Ib"]
            dataframe.loc[index, "Vt_GE(V)"] = Vt_PU*dict_pu["Vb"]
            dataframe.loc[index, "Consumo_GE(l/h)"] = consumption
            dataframe.loc[index, "Eficiencia_GE(%)"] = efficiency

    return dataframe

def get_bytes_yaml(dictionary: dict):

    yaml_data = yaml.dump(dictionary, allow_unicode=True)

    buffer = BytesIO()
    buffer.write(yaml_data.encode('utf-8'))
    buffer.seek(0)

    return buffer

def check_dataframe_input(dataframe: pd.DataFrame, options: list) -> bool:

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

#%% funtions streamlit

def get_widget_number_input(label: str, variable: dict):
    return st.number_input(label=label, **variable)

def get_download_button(directory: str, name_file: str, format_file: str, description: str):
    
    with open(f"{directory}/{name_file}.{format_file}", "rb") as content_xlsx:
                st.download_button(label=f"📄 Descargar plantilla **:red[{description}]**:",
                                   data=content_xlsx,
                                   file_name=f"{name_file}.{format_file}",
                                   mime=format_file)
                
    return

def getGraphConsumptionEfficiency(dataframe: pd.DataFrame):

    fig, ax1 = plt.subplots()

    ax1.set_xlabel("Load(kW)")
    ax1.set_ylabel("Consumo(l/h)", color="tab:blue")
    ax1.plot(dataframe["Load(kW)"], dataframe["Consumo_GE(l/h)"], color="tab:blue")
    ax1.grid(True)
    

    ax2 = ax1.twinx()

    ax2.set_ylabel("Eficiencia(%)", color="tab:red")
    ax2.plot(dataframe["Load(kW)"], dataframe["Eficiencia_GE(%)"], color="tab:red")

    st.pyplot(fig)

    return

def getGraphLoadCharacteristic(dataframe: pd.DataFrame):

    fig, ax1 = plt.subplots()

    ax1.set_xlabel("Load(kW)")
    ax1.set_ylabel("Tensión(V)", color="tab:red")
    ax1.plot(dataframe["Load(kW)"], dataframe["Vt_GE(V)"], color="tab:red")
    ax1.grid(True)

    st.pyplot(fig)