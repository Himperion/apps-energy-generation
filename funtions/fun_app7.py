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

    numPhases = dict_phases[dict_param["Fases"]]["Num"]
    
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

    df_GE = pd.DataFrame(np.arange(start=0, stop=1.01, step=0.01), columns=["load(p.u.)"])
    df_GE["load(kW)"] = df_GE["load(p.u.)"]*dict_pu["Sb"]*dict_param["FP"]

    return df_GE

def get_columns_df_GE(dataframe: pd.DataFrame, dict_pu: dict, dict_param: dict) -> pd.DataFrame:

    dataframe["Ia(p.u.)"] = 0.0
    dataframe["Vt(p.u.)"] = 0.0

    for index, row in dataframe.iterrows():
        Ia = (dict_pu["Ea"] - np.sqrt((dict_pu["Ea"]**2)-4*dict_pu["Ra"]*row["load(p.u.)"]))/(2*dict_pu["Ra"])
        Vt = dict_pu["Ea"] - Ia*dict_pu["Ra"]

        dataframe.loc[index, "Ia(p.u.)"] = Ia
        dataframe.loc[index, "Vt(p.u.)"] = Vt

    dataframe["Ia(A)"] = dataframe["Ia(p.u.)"]*dict_pu["Ib"]
    dataframe["Vt(V)"] = dataframe["Vt(p.u.)"]*dict_pu["Vb"]

    dataframe["Consumo(l/h)"] = ((dict_param["C100"] - dict_param["C0"])*dataframe["load(p.u.)"]) + dict_param["C0"]
    dataframe["Eficiencia(%)"] = (dataframe["load(kW)"]/(dataframe["Consumo(l/h)"]*dict_param["PE_fuel"]))*100

    dataframe = dataframe.drop(columns=["load(p.u.)", "Ia(p.u.)", "Vt(p.u.)"])

    return dataframe

def get_bytes_yaml(dictionary: dict):

    yaml_data = yaml.dump(dictionary, allow_unicode=True)

    buffer = BytesIO()
    buffer.write(yaml_data.encode('utf-8'))
    buffer.seek(0)

    return buffer

#%% funtions streamlit

def get_widget_number_input(label: str, variable: dict):
    return st.number_input(label=label, **variable)

def get_graph_consumption_efficiency(dataframe: pd.DataFrame):

    fig, ax1 = plt.subplots()

    ax1.set_xlabel("load(kW)")
    ax1.set_ylabel("Consumo(l/h)", color="tab:blue")
    ax1.plot(dataframe["load(kW)"], dataframe["Consumo(l/h)"], color="tab:blue")
    ax1.grid(True)
    

    ax2 = ax1.twinx()

    ax2.set_ylabel("Eficiencia(%)", color="tab:red")
    ax2.plot(dataframe["load(kW)"], dataframe["Eficiencia(%)"], color="tab:red")

    st.pyplot(fig)

    return

def get_graph_load_characteristic(dataframe: pd.DataFrame):

    fig, ax1 = plt.subplots()

    ax1.set_xlabel("load(kW)")
    ax1.set_ylabel("Tensión(V)", color="tab:red")
    ax1.plot(dataframe["load(kW)"], dataframe["Vt(V)"], color="tab:red")
    ax1.grid(True)

    st.pyplot(fig)