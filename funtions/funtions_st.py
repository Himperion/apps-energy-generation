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

def curve_x_y(x, y, p_x, p_y, p_label, p_line, title, xlabe, ylabe):

    fig, ax = plt.subplots()
    ax.plot(x, y, 'r-')

    for i in range(0,len(p_line),1):
        pi_x = [p_x[p_line[i][0]], p_x[p_line[i][1]]]
        pi_y = [p_y[p_line[i][0]], p_y[p_line[i][1]]]

        ax.plot(pi_x, pi_y, color='blue', linestyle='--')
    
    ax.set_title(title)             
    ax.scatter(p_x, p_y, color='blue', label='Puntos de interés')

    for i in range(0,len(p_label),1):
        ax.annotate(p_label[i], (p_x[i], p_y[i]), textcoords="offset points", xytext=(5,0), ha='left')

    ax.set_xlabel(xlabe)
    ax.set_ylabel(ylabe)
    ax.grid(True)

    st.pyplot(fig)

    return

def curveMulti_x_y(conditions, x, y, curve_info, option):

    list_color = ["tab:blue", "tab:orange"]

    fig, ax = plt.subplots()

    for idx, case in conditions.iterrows():
        label = ("$G_{eff}$ " + f"{case['Geff']} $W/m^2$\n"
                 "$T_{cell}$ " + f"{case['Tcell']} $\\degree C$")
        
        ax.plot(x[idx], y[idx], label=label)

        if option == "current":
            p_x = curve_info['v_mp'][idx]
            p_y = curve_info['i_mp'][idx]

            pi_x =  [[p_x, p_x], [0, p_x]]
            pi_y = [[0, p_y], [p_y, p_y]]

            ax.set_ylabel("Corriente (A)")

        elif option == "power":
            p_x = curve_info['v_mp'][idx]
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

