# -*- coding: utf-8 -*-
import streamlit as st

#%% funtions general

def get_label_params(dict_param: dict) -> str:

    return f"**{dict_param['label']}:** {dict_param['description']} {dict_param['unit']}"


#%% funtions streamlit

def get_widget_number_input(label: str, disabled: bool, variable: dict):

    return st.number_input(label=label, disabled=disabled, **variable)