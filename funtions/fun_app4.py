import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO
import pvlib, yaml

#%% funtions general

def changeUnitsK(K, Base):

    K_out = (Base*K)/100
    
    return K_out

def get_label_params(dict_param: dict) -> str:

    return f"**{dict_param['label']}:** {dict_param['description']} {dict_param['unit']}"

def celltype_options(celltype: dict):

    options = []
    for key, value in celltype.items():
        options.append(f"{key} ({value['label']})")

    return options

def for_options_get_celltype(option):

    key = option.split("(")[0][:-1]

    return key

def get_PV_params(celltype, v_mp, i_mp, v_oc, i_sc, alpha_sc, beta_voc, gamma_pmp, cells_in_series):

    I_L_ref, I_o_ref, R_s, R_sh_ref, a_ref, Adjust = pvlib.ivtools.sdm.fit_cec_sam(celltype, v_mp, i_mp, v_oc, i_sc, alpha_sc, beta_voc, gamma_pmp, cells_in_series)
    
    PV_params = {
        "alpha_sc": alpha_sc,
        "a_ref": a_ref,
        "I_L_ref": I_L_ref,
        "I_o_ref": I_o_ref,
        "R_sh_ref": R_sh_ref,
        "R_s": R_s,
        "Adjust": Adjust
    }

    return PV_params

def from_PVparams_get_SDEparams(PV_params: dict) -> dict:

    SDE_params = {
        "resistance_shunt": PV_params["R_sh_ref"],
        "resistance_series": PV_params["R_s"],
        "nNsVth": PV_params["a_ref"],
        "saturation_current": PV_params["I_o_ref"],
        "photocurrent": PV_params["I_L_ref"],
        "method": "lambertw"
    }

    return SDE_params

def get_values_curve_I_V_P(v_oc, SDE_params):

    v = np.linspace(0., v_oc, 100)
    i = pvlib.pvsystem.i_from_v(voltage=v, **SDE_params)
    p = v*i

    return v, i, p

def get_singlediode(PV_params):

    photocurrent, saturation_current, resistance_series, resistance_shunt, nNsVth = pvlib.pvsystem.calcparams_cec(**PV_params)

    PV_params_eff = {
        "photocurrent": photocurrent,
        "saturation_current": saturation_current,
        "resistance_series": resistance_series,
        "resistance_shunt": resistance_shunt,
        "nNsVth": nNsVth,
        "method": "lambertw"
        }

    return_singlediode = dict(pvlib.pvsystem.singlediode(**PV_params_eff))

    return return_singlediode

def get_bytes_yaml(dictionary: dict):

    yaml_data = yaml.dump(dictionary, allow_unicode=True)

    buffer = BytesIO()
    buffer.write(yaml_data.encode('utf-8'))
    buffer.seek(0)

    return buffer

#%% funtions streamlit

def get_widget_number_input(label: str, variable: dict):

    return st.number_input(label=label, **variable)

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
        label = get_label_params(dict_param=dict_param[params_label[i]])

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

