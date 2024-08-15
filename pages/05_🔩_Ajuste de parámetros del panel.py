import streamlit as st
import pandas as pd
import numpy as np
import yaml
from io import BytesIO
from funtions import funtions, funtions_st

#%% funtions

@st.cache_data
def to_excel(df: pd.DataFrame):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    
    processed_data = output.getvalue()
        
    return processed_data

#%% global variables

with open("files/[PV] - values_Egap.yaml", 'r') as archivo:
    dict_value_Egap = yaml.safe_load(archivo)

with open("files//[PV] - params.yaml", 'r') as archivo:
    dict_params = yaml.safe_load(archivo)

with open("files//[PV] - dict_replace.yaml", 'r') as archivo:
    dict_rename = yaml.safe_load(archivo)

text = {
    "subheader_1" : "Los párametros de **Single diode** se calculan para un módulo fotovoltaico en condiciones **STC** de operación. Sí se desea hacer un análisis del panel fotovoltaico en condiciones distintas al **STC** es necesario aplicar ajustes a los parámetros para que reflejen un comportamiento acorde a los cambios en la operación.",
    "subheader_2" : "Este aplicativo web para efectuar la corrección de parámetros del módulo se logra mediante la librería **PVLIB** de Python que permite simular sistemas de energía fotovoltaicos.",
    "subheader_3" : "El aplicativo permite obtener los siguientes parámetros:"
}

options_sel_oper = ["📗 Única", "📚 Múltiple"]

items_options_columns_df = {
    "Geff" : ["Gef(W/m^2)", "Gef(W/m²)", "Gin(W/m²)", "Gin(W/m^2)"],
    "Toper" : ["Toper(°C)"]
}

template = {
    "directory": "files",
    "name_file": "[Plantilla] - Ajuste de parámetros del panel",
    "format_file": "xlsx",
    "description": "Irradiancia efectiva y Temperatura de operación del módulo"
}

keys_show_output = ["Iph", "Isat", "Rs", "Rp", "nNsVt", "Voc", "Isc", "Impp", "Vmpp", "Pmpp"]
dict_show_output = funtions.get_options_params(dict_params=dict_params, options_keys=keys_show_output)
list_show_output = [key for key in dict_show_output]

#%% main

st.markdown("# 🔩 Ajuste de parámetros del panel")

tab1, tab2 = st.tabs(["📑 Marco teórico", "📝 Entrada de datos"])  

with tab1:   
    st.markdown(text["subheader_1"])

    col1, col2, col3 = st.columns( [0.25, 0.5, 0.25])

    with col1:
        st.write("")
    with col2:
        st.image("images\\app2_img1.png")
    
with tab2:      
    with st.container(border=True):
        st.markdown("**:blue[{0}:]**".format("Parámetros del módulo"))
        
        Alfa = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["Alfa"]),
                                                   variable=dict_params["Alfa"]["number_input"])
        
        Iph = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["Iph"]),
                                                   variable=dict_params["Iph"]["number_input"])
        
        Isat = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["Isat"]),
                                                   variable=dict_params["Isat"]["number_input"])
        
        Rs = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["Rs"]),
                                                 variable=dict_params["Rs"]["number_input"])
        
        Rp = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["Rp"]),
                                                 variable=dict_params["Rp"]["number_input"])
        
        nNsVt = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["nNsVt"]),
                                                    variable=dict_params["nNsVt"]["number_input"])
        
        cell_type = st.selectbox("Tecnologia", options=list(dict_value_Egap.keys()), index=6)

    with st.container(border=True):
        st.markdown("**:blue[{0}:]**".format("Conexión de los módulos"))
        col1, col2 = st.columns(2)

        with col1:
            PVs = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["PVs"]),
                                                      variable=dict_params["PVs"]["number_input"])
        
        with col2:
            PVp = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["PVp"]),
                                                      variable=dict_params["PVp"]["number_input"])

    with st.container(border=True):
        st.markdown("**:blue[{0}:]**".format("Condiciones de operación del módulo"))

        option_sel = st.radio(label="Opciones para el ingreso de condiciones",
                              options=options_sel_oper,
                              captions=["Ingreso de una única condición de irradiancia y temperatura de operación.",
                                        "Ingreso de múltiples condiciones de irradiancia y temperatura de operación."])
        
        if option_sel == options_sel_oper[0]:
            col1, col2 = st.columns(2)
            
            with col1:
                Geff = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["Geff"]),
                                                           variable=dict_params["Geff"]["number_input"])
                
            with col2:
                Toper = funtions_st.get_widget_number_input(label=funtions.get_label_params(dict_param=dict_params["Toper"]),
                                                            variable=dict_params["Toper"]["number_input"])
            
        elif option_sel == options_sel_oper[1]:
            archive_Gef_Toper = st.file_uploader("Cargar archivo {0} y {1}".format("**Irradiancia efectiva** (m/s)",
                                                                                   "**Temperatura de operación del módulo** (°C)."),
                                                 type={"xlsx"})
                
            funtions_st.get_download_button(**template)

    show_output = funtions_st.get_expander_params(list_show_output)

    app_5_submitted = st.button("Aceptar")

    if app_5_submitted:
        STD_params = {
            "photocurrent": Iph,
            "saturation_current": Isat,
            "resistance_series": Rs,
            "resistance_shunt": Rp,
            "nNsVth": nNsVt
            }
        
        Input_desoto = {
            "Alfa": Alfa,
            "SDE_params": STD_params,
            "cell_type": cell_type,
            "dict_value_Egap": dict_value_Egap,
            "array_serie": PVs,
            "array_parallel": PVp
        }

        labels_output = funtions.get_labels_params_output(show_output, dict_show_output)
        
        if option_sel == options_sel_oper[0]:

            conditions = pd.DataFrame([(1000, 25), (Geff, Toper)], columns=['Geff', 'Toper'])
            df_info, v, i, p = funtions.get_params_desoto(conditions=conditions, rename=dict_rename, curve=True, **Input_desoto)

            sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📋 Parámetros Ajustados", "📈 Curva I-V", "📉 Curva P-V"])

            with sub_tab1:
                head_column = ["", "Condiciones STC", "Ajuste de operación"]

                funtions_st.get_print_params_dataframe(df_info, labels_output, dict_params, head_column)

            with sub_tab2:
                funtions_st.curveMulti_x_y(conditions, v, i, df_info, option="current")

            with sub_tab3:
                funtions_st.curveMulti_x_y(conditions, v, p, df_info, option="power")
        
        if option_sel == options_sel_oper[1]:
            if archive_Gef_Toper is not None:
                df_input = pd.read_excel(archive_Gef_Toper)

                df_pv, check, columns_options_sel = funtions.check_dataframe_input(dataframe=df_input,
                                                                                   options=items_options_columns_df)
                
                if check:
                    df_conditions = funtions.get_dataframe_conditions(dataframe=df_pv, columns_options_sel=columns_options_sel)

                    df_info = funtions.get_params_desoto(conditions=df_conditions, rename=dict_rename, curve=False, **Input_desoto)

                    dict_replace = funtions.get_dict_replace(dict_rename, dict_params)
                    
                    df_info.rename(columns=dict_replace, inplace=True)
                    df_info.drop(columns=["i_x", "i_xx"], inplace=True)
                    df_info = df_info[[item.split(":")[0] for item in show_output]]
                    df_info = pd.concat([df_pv, df_info], axis=1)

                    
                    st.dataframe(df_info)

                    excel = to_excel(df_info)
                    
                    st.download_button(label="📄 Descargar muestras",
                                       data=excel,
                                       file_name=funtions.name_file_head(name="parametersPV.xlsx"),
                                       mime="xlsx")


                

                    

                
                else:
                    st.warning("Falta cargar archivo **Excel** (.xlsx)", icon="⚠️")

            

    