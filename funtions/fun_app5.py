import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import streamlit as st
import datetime as dt
import pvlib

def name_file_head(name: str) -> str:
    now = dt.datetime.now()
    return f"[{now.day}-{now.month}-{now.year}_{now.hour}-{now.minute}] {name}"

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

def get_options_params(dict_params: dict, options_keys: list) -> list:

    dict_options_params = {}

    for key in options_keys:
        string_aux =  f"{dict_params[key]['label']}{dict_params[key]['unit']}: {dict_params[key]['description']}"
        dict_options_params[string_aux] = key
        
    return dict_options_params

def get_show_output(dict_params):

    keysShowOutput = ["Iph", "Isat", "Rs", "Rp", "nNsVt", "Voc", "Isc", "Impp", "Vmpp", "Pmpp"]
    dictShowOutput = get_options_params(dict_params=dict_params, options_keys=keysShowOutput)
    listShowOutput = [key for key in dictShowOutput]

    return keysShowOutput, dictShowOutput, listShowOutput

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

def get_dataframe_conditions(dataframe: pd.DataFrame, columns_options_sel: dict) -> pd.DataFrame:

    dict_rename = {value: key for key, value in columns_options_sel.items()}

    dataframe = dataframe.rename(columns=dict_rename)
    dataframe = dataframe.loc[:, [key for key in columns_options_sel]]

    return dataframe

def get_singlediode(conditions: pd.DataFrame, PV_params: dict, PVs: int, PVp: int):

    dict_list = {
        "Iph": [],
        "Isat": [],
        "Rs": [],
        "Rp": [],
        "nNsVt": [],
        "Isc": [],
        "Voc": [],
        "Impp": [],
        "Vmpp": [],
        "Pmpp": [],
    }

    for index, row in conditions.iterrows():
        if row["Geff"] != 0:

            dictAux = {
                "effective_irradiance": row["Geff"],
                "temp_cell": row["Toper"]
            }
            
            photocurrent, saturation_current, resistance_series, resistance_shunt, nNsVth = pvlib.pvsystem.calcparams_cec(**PV_params, **dictAux)

            PV_params_eff = {
                "photocurrent": photocurrent*PVp,
                "saturation_current": saturation_current*PVp,
                "resistance_series": resistance_series*(PVs/PVp),
                "resistance_shunt": resistance_shunt*(PVs/PVp),
                "nNsVth": nNsVth*PVs,
                "method": "lambertw"
                }
            
            singleDiode = dict(pvlib.pvsystem.singlediode(**PV_params_eff))
        
        else:
            PV_params_eff = {
                "photocurrent": 0.0,
                "saturation_current": 0.0,
                "resistance_series": 0.0,
                "resistance_shunt": 0.0,
                "nNsVth": 0.0,
                "method": "lambertw"
                }

            singleDiode = {
                "i_sc": 0.0,
                "v_oc": 0.0,
                "i_mp": 0.0,
                "v_mp": 0.0,
                "p_mp": 0.0,
                "i_x": 0.0,
                "i_xx": 0.0,
            }

        dict_list["Iph"].append(PV_params_eff["photocurrent"])
        dict_list["Isat"].append(PV_params_eff["saturation_current"])
        dict_list["Rs"].append(PV_params_eff["resistance_series"])
        dict_list["Rp"].append(PV_params_eff["resistance_shunt"])
        dict_list["nNsVt"].append(PV_params_eff["nNsVth"])
        dict_list["Isc"].append(round(float(singleDiode["i_sc"]), 6))
        dict_list["Voc"].append(round(float(singleDiode["v_oc"]), 6))
        dict_list["Impp"].append(round(float(singleDiode["i_mp"]), 6))
        dict_list["Vmpp"].append(round(float(singleDiode["v_mp"]), 6))
        dict_list["Pmpp"].append(round(float(singleDiode["p_mp"]), 6))

    df_values = pd.DataFrame({"Iph": dict_list["Iph"],
                              "Isat": dict_list["Isat"],
                              "Rs": dict_list["Rs"],
                              "Rp": dict_list["Rp"],
                              "nNsVt": dict_list["nNsVt"],
                              "Isc": dict_list["Isc"],
                              "Voc": dict_list["Voc"],
                              "Impp": dict_list["Impp"],
                              "Vmpp": dict_list["Vmpp"],
                              "Pmpp": dict_list["Pmpp"]
                              })

    return pd.concat([conditions, df_values], axis=1)

def get_dict_replace(dict_rename: dict, dict_params: dict) ->dict:

    dict_replace = {}

    for key, value in dict_rename.items():
        dict_replace[value] = f"{dict_params[value]['label']}{dict_params[value]['unit']}"

    return dict_replace

def get_final_dataframe(df_pv: pd.DataFrame, df_input: pd.DataFrame, dict_replace: dict, dict_conditions: dict, list_output: list) -> pd.DataFrame:

    df_pv["Pmpp"] = round(df_pv["Pmpp"]/1000, 4)
    df_pv.drop(columns=[key for key in dict_conditions], inplace=True)
    df_pv.rename(columns=dict_replace, inplace=True)
    df_pv = df_pv[[item.split(":")[0] for item in list_output]]

    return pd.concat([df_input, df_pv], axis=1)

def get_labels_params_output(show_output, dict_show_output):

    labels_output = []
    for key in show_output:
        labels_output.append(dict_show_output[key])

    return labels_output

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

def get_current_and_power_with_voltage(df, voltage, photocurrent, saturation_current, resistance_series, resistance_shunt, nNsVth, method):

    voltage = np.linspace(0., df['Voc'].values, 100)

    data_i_from_v = {
        "voltage": voltage,
        "photocurrent": df["Iph"].values,
        "saturation_current": df["Isat"].values,
        "resistance_series": df["Rs"].values,
        "resistance_shunt": df["Rp"].values,
        "nNsVth": df["nNsVt"].values,
        "method": "lambertw"
        }
    
    current = pvlib.pvsystem.i_from_v(**data_i_from_v)
    power = voltage*current

    return voltage.T, current.T, power.T

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

def get_print_params_dataframe(dataframe: pd.DataFrame, params_label: list, dict_param: dict, head_column: list):

    dataframe = dataframe[params_label]
    colors_string = [":grey[{0}]", ":blue[{0}]", ":red[{0}]"]

    with st.container(border=True):
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

    with st.container(border=True):
        st.pyplot(fig)

    return



