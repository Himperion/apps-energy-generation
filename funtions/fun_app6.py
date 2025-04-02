import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import streamlit as st
import datetime as dt
from io import BytesIO
import yaml

#%% funtions general

def get_param_turbine_2_dict(params):
    D = params["D"]
    V_in = params["V_in"]
    V_nom = params["V_nom"]
    V_max = params["V_max"]
    P_nom = params["P_nom"]

    return D, V_in, V_nom, V_max, P_nom

def get_power_wind_turbine(params, rho, V_wind):
    D, V_in, V_nom, V_max, P_nom = get_param_turbine_2_dict(params)

    A_barrido = np.pi*((0.5*D)**2)
    P_ideal = (0.5*rho*(V_wind**3)*A_barrido)/1000
    P_betz = round(0.593*P_ideal, 4)

    if V_in <= V_wind < V_nom:
        P_gen = round(P_nom*((V_wind**3 - V_in**3)/(V_nom**3 - V_in**3)), 4)
    elif V_nom <= V_wind < V_max:
        P_gen = round(P_nom, 4)
    else:
        P_gen = 0

    if P_gen > 0:
        n = round((P_gen/P_ideal)*100, 4)
    else:
        n = 0

    return P_gen, n, P_ideal, P_betz

def get_dataframe_power_wind_turbine(params: dict, rho: float, dataframe: pd.DataFrame, column: dict) -> pd.DataFrame:
    column_label = column[next(iter(column))]
    df_out = dataframe.copy(deep=True)

    df_out["Pideal_AERO(kW)"] = 0.0
    df_out["Pbetz_AERO(kW)"] = 0.0
    df_out["Pgen_AERO(kW)"] = 0.0
    df_out["efficiency_AERO(%)"] = 0.0

    for index, row in df_out.iterrows():
        Vwind = row[column_label]
        P_gen, n, P_ideal, P_betz = get_power_wind_turbine(params, rho, Vwind)

        df_out.loc[index, "Pideal_AERO(kW)"] = P_ideal
        df_out.loc[index, "Pbetz_AERO(kW)"] = P_betz
        df_out.loc[index, "Pgen_AERO(kW)"] = P_gen
        df_out.loc[index, "efficiency_AERO(%)"] = n
        
    return df_out

def get_values_curve_turbine(params: dict, rho: float) -> pd.DataFrame:
    V_wind_list = np.linspace(0., params["V_max"], 200).tolist()

    list_P_gen, list_n, list_P_ideal, list_P_betz = [], [], [], []

    for i in range(0,len(V_wind_list),1):
        P_gen, n, P_ideal, P_betz = get_power_wind_turbine(params, rho, V_wind_list[i])
        
        list_P_gen.append(round(P_gen, 4))
        list_n.append(round(n, 4))
        list_P_ideal.append(round(P_ideal, 4))
        list_P_betz.append(round(P_betz, 4))
    
    df_values = pd.DataFrame({"V_wind": V_wind_list,
                              "P_gen": list_P_gen,
                              "n_turbine": list_n,
                              "P_ideal": list_P_ideal,
                              "P_betz": list_P_betz
                              })

    return df_values

#%% funtions streamlit

def get_download_button(directory: str, name_file: str, format_file: str, description: str):

    with open(f"{directory}/{name_file}.{format_file}", "rb") as content_xlsx:
                st.download_button(label=f"📄 Descargar plantilla **:red[{description}]**:",
                                   data=content_xlsx,
                                   file_name=f"{name_file}.{format_file}",
                                   mime=format_file)
                
    return

def curve_x_yy(x, y1, y2, points_y1: dict, points_y2: dict, lines_y1: list, lines_y2: list, x_label: str, y1_label: str, y2_label: str, title: str):

    p_x1, p_y1 = [], []
    p_x2, p_y2 = [], []

    fig, ax1 = plt.subplots()

    for item in lines_y1:
        x_item = [points_y1[item[0]][0], points_y1[item[1]][0]]
        y_item = [points_y1[item[0]][1], points_y1[item[1]][1]]

        ax1.plot(x_item, y_item, color="tab:blue", linestyle='--')

    for key, value in points_y1.items():
        ax1.annotate(text=key,
                     xy=value,
                     textcoords="offset points",
                     xytext=(5,0),
                     ha="left")
        
        p_x1.append(value[0])
        p_y1.append(value[1])

    ax1.scatter(p_x1, p_y1, color="tab:blue", label='Puntos de interés')
    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y1_label, color="tab:blue")
    ax1.plot(x, y1, color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    ax2 = ax1.twinx()

    for item in lines_y2:
        x_item = [points_y2[item[0]][0], points_y2[item[1]][0]]
        y_item = [points_y2[item[0]][1], points_y2[item[1]][1]]

        ax2.plot(x_item, y_item, color="tab:orange", linestyle='--')

    for key, value in points_y2.items():
        ax2.annotate(text=key,
                     xy=value,
                     textcoords="offset points",
                     xytext=(5,0),
                     ha="left")
        
        p_x2.append(value[0])
        p_y2.append(value[1])

    ax2.set_ylabel(y2_label, color="tab:orange")
    ax2.plot(x, y2, color="tab:orange", linestyle=':')
    ax2.tick_params(axis='y', labelcolor="tab:orange")

    plt.title(title)

    with st.container(border=True):
        st.pyplot(fig)

    return

def curve_x_y(x, y, points, lines, title, xlabel, ylabel):

    p_x, p_y = [], []

    fig, ax = plt.subplots()
    ax.plot(x, y, 'r-')

    for item in lines:
        x_item = [points[item[0]][0], points[item[1]][0]]
        y_item = [points[item[0]][1], points[item[1]][1]]

        ax.plot(x_item, y_item, color='blue', linestyle='--')

    for key, value in points.items():
        ax.annotate(text=key,
                    xy=value,
                    textcoords="offset points",
                    xytext=(5,0),
                    ha="left")
        
        p_x.append(value[0])
        p_y.append(value[1])

    ax.set_title(title)             
    ax.scatter(p_x, p_y, color='blue', label='Puntos de interés')

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)

    with st.container(border=True):
        st.pyplot(fig)

    return

def curve_x_yyy(x, y1, y2, y3, title, xlabel, ylabel, label_Y):

    fig, ax = plt.subplots()
    ax.plot(x, y1, 'r-', label=label_Y[0])
    ax.plot(x, y2, 'b-', label=label_Y[1])
    ax.plot(x, y3, 'g-', label=label_Y[2])
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    ax.legend()

    with st.container(border=True):
        st.pyplot(fig)

    return