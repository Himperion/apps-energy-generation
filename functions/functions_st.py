import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from functions import functions
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode

def view_dataframe_information(dataframe):
    list_options_columns_name = ["Load(W)", "Gin(W/m²)", "Tamb(°C)", "Vwind(m/s)"]
    list_options_columns_label = ["💡 Load(W)", "🌤️ Gin(W/m²)", "🌡️ Tamb(°C)", "✈️ Vwind(m/s)"]
    list_data_columns = list(dataframe.columns)

    list_tabs_graph_name, list_tabs_graph_label = functions.get_list_tabs_graph(list_data_columns,
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

def refreseh_token(auth):
    user = auth.refresh(st.session_state.refreshToken)

    st.session_state.idToken = user['idToken']
    st.session_state.refreshToken = user['refreshToken']
    return

def warning_input_data(list_bool, list_label):
    for i in range(0,len(list_bool),1):
        if not list_bool[i]:
            st.markdown(' - No se encontro el campo: :blue[{0}].'.format(list_label[i]))
    
    return

def dataframe_AgGrid(dataframe):

    gb = GridOptionsBuilder.from_dataframe(dataframe)
    gb.configure_selection(selection_mode="single", use_checkbox=True)
    gb.configure_side_bar()
    gridOptions = gb.build()

    data = AgGrid(dataframe,
                  gridOptions=gridOptions,
                  enable_enterprise_modules=True,
                  allow_unsafe_jscode=True,
                  update_mode=GridUpdateMode.SELECTION_CHANGED,
                  columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

    return data

def get_filter_component_pv(dataframe, dict_data_filter_pv):

    min_Wp = dict_data_filter_pv['min_Wp']
    max_Wp = dict_data_filter_pv['max_Wp']
    min_Voc = dict_data_filter_pv['min_Voc']
    max_Voc = dict_data_filter_pv['max_Voc']
    min_Isc = dict_data_filter_pv['min_Isc']
    max_Isc = dict_data_filter_pv['max_Isc']
    list_cell_type = dict_data_filter_pv['list_cell_type']
    list_manufacturer = dict_data_filter_pv['list_manufacturer']

    with st.expander('✂️ Opciones de filtrado'):
        with st.container(border=True):
            col1_1, col1_2 = st.columns([0.4, 0.6])

            checkbox_1 = col1_1.checkbox(label='Potencia máxima (Wp):', value=False)
            slider_1 = col1_2.slider('Seleccionar el rango:', min_Wp, max_Wp, (min_Wp, max_Wp),
                                     disabled=not checkbox_1, key='delta_Wp')
            
            if checkbox_1:
                condition1 = dataframe['Pmax (Wp)'] >= slider_1[0]
                condition2 = dataframe['Pmax (Wp)'] <= slider_1[1]

                dataframe = dataframe[condition1 & condition2]

        with st.container(border=True):
            col2_1, col2_2 = st.columns([0.4, 0.6])

            checkbox_2 = col2_1.checkbox(label='Tensión de circuito-abierto (V):', value=False) 
            slider_2 = col2_2.slider('Seleccionar el rango:', min_Voc, max_Voc, (min_Voc, max_Voc),
                                     disabled=not checkbox_2, key='delta_Voc')
            
            if checkbox_2:
                condition1 = dataframe['Voc (V)'] >= slider_2[0]
                condition2 = dataframe['Voc (V)'] <= slider_2[1]

                dataframe = dataframe[condition1 & condition2]

        with st.container(border=True):
            col3_1, col3_2 = st.columns([0.4, 0.6])

            checkbox_3 = col3_1.checkbox(label='Corriente de corto-circuito (A):', value=False)
            slider_3 = col3_2.slider('Seleccionar el rango:', min_Isc, max_Isc, (min_Isc, max_Isc),
                                     disabled=not checkbox_3, key='delta_Isc')
            
            if checkbox_3:
                condition1 = dataframe['Isc (A)'] >= slider_3[0]
                condition2 = dataframe['Isc (A)'] <= slider_3[1]

                dataframe = dataframe[condition1 & condition2]

        with st.container(border=True):
            col4_1, col4_2 = st.columns([0.4, 0.6])

            checkbox_4 = col4_1.checkbox(label='Tipo de célula fotovoltaica:', value=False)
            selectbox_4 = col4_2.selectbox(label='Seleccione una opción', options=list_cell_type, index=0,
                                           disabled=not checkbox_4)
            
            if checkbox_4:
                dataframe = dataframe[dataframe['Tecnología'] == selectbox_4]

        with st.container(border=True):
            col5_1, col5_2 = st.columns([0.4, 0.6])

            checkbox_5 = col5_1.checkbox(label='Fabricante:', value=False)
            selectbox_5 = col5_2.selectbox(label='Seleccione una opción', options=list_manufacturer, index=0,
                                           disabled=not checkbox_5)
            
            if checkbox_5:
                dataframe = dataframe[dataframe['Fabricante'] == selectbox_5]
       
    return dataframe

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

        elif option == "power":
            p_x = curve_info['v_mp'][idx]
            p_y = np.max(y[idx])

            pi_x = [[p_x, p_x], [0, p_x]]
            pi_y = [[0, p_y], [p_y, p_y]]

        for i in range(0,len(pi_x), 1):
            ax.plot(pi_x[i], pi_y[i], color=list_color[idx], linestyle='--')

        ax.plot([p_x], [p_y], ls='', marker='o', color=list_color[idx])

    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

    return





