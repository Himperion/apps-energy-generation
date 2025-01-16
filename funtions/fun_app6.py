import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import streamlit as st
import datetime as dt
from io import BytesIO
import yaml

#%% funtions general

def name_file_head(name: str) -> str:
    now = dt.datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def get_label_params(dict_param: dict) -> str:
    return f"**{dict_param['label']}:** {dict_param['description']} {dict_param['unit']}"

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

    df_out["Pideal(kW)"] = ""
    df_out["Pbetz(kW)"] = ""
    df_out["Pgen(kW)"] = ""
    df_out["efficiency(%)"] = ""

    for index, row in df_out.iterrows():
        Vwind = row[column_label]
        P_gen, n, P_ideal, P_betz = get_power_wind_turbine(params, rho, Vwind)

        df_out.loc[index, "Pideal(kW)"] = P_ideal
        df_out.loc[index, "Pbetz(kW)"] = P_betz
        df_out.loc[index, "Pgen(kW)"] = P_gen
        df_out.loc[index, "efficiency(%)"] = n
        
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

def get_bytes_yaml(dictionary: dict):

    yaml_data = yaml.dump(dictionary, allow_unicode=True)

    buffer = BytesIO()
    buffer.write(yaml_data.encode('utf-8'))
    buffer.seek(0)

    return buffer

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