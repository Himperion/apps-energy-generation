import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from funtions import funtions

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
    
    list_data_columns = list(dataframe.columns)

    list_tabs_graph_name, list_tabs_graph_label = funtions.get_list_tabs_graph(list_data_columns,
                                                                               list_options_columns_name,
                                                                               list_options_columns_label)
    
    tab_con1, tab_con2 = st.tabs(["📄 Tabla", "📈 Gráficas"])
    with tab_con1:
        st.dataframe(dataframe)
    with tab_con2: 
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

    list_tabs_graph_name, list_tabs_graph_label = funtions.get_list_tabs_graph(list(dataframe.columns),
                                                                               list_options_columns_name,
                                                                               list_options_columns_label)
    
    tab_con1, tab_con2 = st.tabs(["📄 Tabla", "📈 Gráficas"])
    with tab_con1:
        st.dataframe(dataframe)
    with tab_con2: 
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

def get_print_params(params, params_label):

    list_params_keys = list(params.keys())

    col1, col2 = st.columns(2)

    for i in range(0,len(list_params_keys),1):
        if type(params[list_params_keys[i]]) is float or type(params[list_params_keys[i]]) == np.float64:
            value = params[list_params_keys[i]]
        else:
            value = params[list_params_keys[i]].to_list()[1]

        col1.markdown(f"**{params_label[i]}:**")
        col2.markdown(value)

    return

def get_col_for_length(length):

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

def get_print_params_dataframe(dataframe: pd.DataFrame, params_label: list, dict_param: dict, head_column: list):

    dataframe = dataframe[params_label]
        
    colors_string = [":grey[{0}]", ":blue[{0}]", ":red[{0}]"]

    list_columns_title = get_col_for_length(len(head_column))

    for i in range(0,len(head_column),1):
        list_columns_title[i].markdown(f"**{colors_string[i].format(head_column[i])}**")

    for i in range(0,len(params_label),1):
        label = funtions.get_label_params(dict_param=dict_param[params_label[i]])

        list_columns = get_col_for_length(len(head_column))

        list_columns[0].markdown(colors_string[0].format(label))

        for index, row in dataframe.iterrows():
            list_columns[index+1].markdown(colors_string[index+1].format(row[params_label[i]]))
            
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

    st.pyplot(fig)

    return

def curveMulti_x_y(conditions: pd.DataFrame, x, y, df_info: pd.DataFrame, option: str):

    list_color = ["tab:blue", "tab:orange"]

    fig, ax = plt.subplots()

    for idx, case in conditions.iterrows():
        label = ("$G_{eff}$ " + f"{case['Geff']} $W/m^2$\n"
                 "$T_{cell}$ " + f"{case['Toper']} $\\degree C$")
        
        ax.plot(x[idx], y[idx], label=label)

        if option == "current":
            p_x = df_info.loc[idx, 'Vmpp']
            p_y = df_info.loc[idx, 'Impp']

            pi_x =  [[p_x, p_x], [0, p_x]]
            pi_y = [[0, p_y], [p_y, p_y]]

            ax.set_ylabel("Corriente (A)")

        elif option == "power":
            p_x = df_info.loc[idx, 'Vmpp']
            p_y = np.max(y[idx])

            pi_x = [[p_x, p_x], [0, p_x]]
            pi_y = [[0, p_y], [p_y, p_y]]

            ax.set_ylabel("Potencia (W)")

        for i in range(0,len(pi_x), 1):
            ax.plot(pi_x[i], pi_y[i], color=list_color[idx], linestyle='--')

        ax.plot([p_x], [p_y], ls='', marker='o', color=list_color[idx])

    ax.set_xlabel("Voltaje (V)")
    ax.grid(True)
    ax.legend()

    st.pyplot(fig)

    return

def curveTurbine(df_values: pd.DataFrame, column_xy: tuple, label_xy: tuple, label_title: str, color: str):

    fig, ax = plt.subplots()

    ax.plot(df_values[column_xy[0]], df_values[column_xy[1]], color=color)
    ax.set_xlabel(label_xy[0])
    ax.set_ylabel(label_xy[1])
    ax.set_title(label_title)

    st.pyplot(fig)

    return

def graphicalDataframe(dataframe: pd.DataFrame):

    columns = dataframe.columns.to_list()

    if "dates (Y-M-D hh:mm:ss)" in columns:
        columns.remove("dates (Y-M-D hh:mm:ss)")

        options = st.selectbox(label="Visualizar datos en el tiempo:",
                                options=columns,
                                placeholder="Seleccione una opción",
                                index=0)
        
        st.text(options)

    return

def get_download_button(directory: str, name_file: str, format_file: str, description: str):

    with open(f"{directory}/{name_file}.{format_file}", "rb") as content_xlsx:
                st.download_button(label=f"📄 Descargar plantilla **:red[{description}]**:",
                                   data=content_xlsx,
                                   file_name=name_file,
                                   mime=format_file)
                
    return

def get_expander_params(list_show_output):

    with st.expander(label="🪛 **{0}**".format("Personalizar parámetros de salida")): 
        show_output = st.multiselect(label="Seleccionar parámetros", options=list_show_output, default=list_show_output)

    return show_output

def get_widget_number_input(label: str, variable: dict):

    return st.number_input(label=label, **variable)


