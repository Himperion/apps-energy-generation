# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st
import datetime as dt
from pynasapower.get_data import query_power
from pynasapower.geometry import point
from io import BytesIO
import yaml


#%% funtions

def name_file_head(name: str) -> str:
    now = dt.datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

def get_label_params(dict_param: dict) -> str:

    return f"**{dict_param['label']}:** {dict_param['description']} {dict_param['unit']}"

def GMS_2_GD(dict_in):

    lat = dict_in["lat_degrees"] + (dict_in["lat_minutes"] + dict_in["lat_seconds"]/60)/60
    lon = dict_in["lon_degrees"] + (dict_in["lon_minutes"] + dict_in["lon_seconds"]/60)/60

    if dict_in["lat_NS"] == "S":
        lat = -1*lat
    if dict_in["lon_EO"] == "W":
        lon = -1*lon

    dict_params = {
        "latitude": lat,
        "longitude": lon,
        "start": dict_in["date_ini"],
        "end": dict_in["date_end"]
    }

    return dict_params

def cal_rows(date_ini, date_end, steps):

    date_delta = date_end - date_ini
    cal_rows = int((date_delta.days * 1440)/steps)

    return cal_rows

def get_parameters_NASA_POWER(options: list, dict_parameters: dict) -> list:

    parameters = []

    for i in range(0,len(options),1):
        parameters.append(dict_parameters[options[i]][0])

    return parameters

def get_dataframe_NASA_POWER(dict_params: dict, parameters: list, dict_parameters: dict) -> pd.DataFrame:

    dataframe = query_power(geometry = point(x=dict_params["longitude"], y=dict_params["latitude"], crs="EPSG:4326"),
                            start = dict_params["start"],
                            end = dict_params["end"],
                            to_file = False,
                            community = "re",
                            parameters = parameters,
                            temporal_api = "hourly",
                            spatial_api = "point")

    list_columns, list_columns_drop = list(dataframe.columns), ["YEAR", "MO", "DY", "HR"]

    for i in range(0,len(list_columns_drop),1):
        if list_columns_drop[i] in list_columns:
            dataframe = dataframe.drop(columns=[list_columns_drop[i]])

    for key in dict_parameters:
        if dict_parameters[key][0] in list_columns:
            dataframe = dataframe.rename(columns={dict_parameters[key][0]: dict_parameters[key][1]})

    return dataframe

def add_column_dates(dataframe: pd.DataFrame, date_ini, rows, steps) -> pd.DataFrame:

    list_columns = list(dataframe.columns)
    if not "dates (Y-M-D hh:mm:ss)" in list_columns:
        dates = pd.date_range(start=date_ini,
                              periods=rows,
                              freq=pd.Timedelta(minutes=steps))
        
        if dataframe.shape[0] >= dates.shape[0]:
            dataframe = dataframe.head(rows)

        if dataframe.shape[0] == dates.shape[0]:
            dataframe["dates (Y-M-D hh:mm:ss)"] = dates
            dataframe = dataframe[["dates (Y-M-D hh:mm:ss)"] + list_columns]

    return dataframe

def get_list_tabs_graph(list_data_columns, list_options_columns_name, list_options_columns_label):

    list_tabs_graph_name, list_tabs_graph_label = [], []
    for i in range(0,len(list_data_columns),1):
        if list_data_columns[i] in list_options_columns_name:
            list_tabs_graph_name.append(list_data_columns[i])
            list_tabs_graph_label.append(list_options_columns_label[list_options_columns_name.index(list_data_columns[i])])

    return list_tabs_graph_name, list_tabs_graph_label

def get_bytes_yaml(dictionary: dict):

    yaml_data = yaml.dump(dictionary, allow_unicode=True)

    buffer = BytesIO()
    buffer.write(yaml_data.encode('utf-8'))
    buffer.seek(0)

    return buffer

def check_dataframe_input(dataframe: pd.DataFrame, options: list):

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
                    columns_options_drop.append(options[i])

        else:
            columns_options_sel[key] = None
            columns_options_check[key] = False

    if len(columns_options_drop) != 0:
        dataframe = dataframe.drop(columns=columns_options_drop)

    for key in columns_options_check:
        check = check and columns_options_check[key]

    return dataframe, check, columns_options_sel

def get_column_Toper(dataframe: pd.DataFrame, options_sel: dict, NOCT: int, column_name: str) -> pd.DataFrame:

    dataframe[column_name] = dataframe[options_sel["Tamb"]] + (NOCT-20)*(dataframe[options_sel["Geff"]]/800)

    return dataframe

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

def get_expander_params(list_show_output):

    with st.expander(label="🪛 **{0}**".format("Personalizar parámetros de salida")): 
        show_output = st.multiselect(label="Seleccionar parámetros", options=list_show_output, default=list_show_output)

    return show_output

def view_dataframe_information(dataframe):

    list_options_columns_name = ["Load(W)",
                                 "Gin(W/m²)",
                                 "Tamb 2msnm(°C)",
                                 "Vwind 10msnm(m/s)",
                                 "Vwind 50msnm(m/s)"]

    list_options_columns_label = ["💡 Load(W)",
                                  "🌤️ Gin(W/m²)",
                                  "🌡️ Tamb 2msnm(°C)",
                                  "✈️ Vwind 10msnm(m/s)",
                                  "✈️ Vwind 50msnm(m/s)"]

    list_tabs_graph_name, list_tabs_graph_label = get_list_tabs_graph(list(dataframe.columns),
                                                                      list_options_columns_name,
                                                                      list_options_columns_label)
     
    if len(list_tabs_graph_name) != 0:
        if len(list_tabs_graph_name) == 1:
            subtab_con1 = st.tabs(list_tabs_graph_label)
            list_subtab_con = [subtab_con1[0]]
        elif len(list_tabs_graph_name) == 2:
            subtab_con1, subtab_con2 = st.tabs(list_tabs_graph_label)
            list_subtab_con = [subtab_con1, subtab_con2]
        elif len(list_tabs_graph_name) == 3:
            subtab_con1, subtab_con2, subtab_con3 = st.tabs(list_tabs_graph_label)
            list_subtab_con = [subtab_con1, subtab_con2, subtab_con3]
        elif len(list_tabs_graph_name) == 4:
            subtab_con1, subtab_con2, subtab_con3, subtab_con4 = st.tabs(list_tabs_graph_label)
            list_subtab_con = [subtab_con1, subtab_con2, subtab_con3, subtab_con4]

        for i in range(0,len(list_subtab_con),1):
            with list_subtab_con[i]:
                st.line_chart(data=dataframe[[list_tabs_graph_name[i]]], y=list_tabs_graph_name[i])

    return
