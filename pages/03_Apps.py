import streamlit as st

from functions.apps import photovoltaic, battery

# variables ----------------------------------------------------------------------------------------- 

options_menu_apps = ["🪟 Módulos fotovoltaicos", "🔋 Baterías"]

# streamlit -----------------------------------------------------------------------------------------
#st.session_state

st.sidebar.markdown("# 🔧 Apps")

menu_apps = st.sidebar.selectbox(label="Opciones:",
                                 options=options_menu_apps,
                                 placeholder="Seleccione una opción",
                                 index=None)

if menu_apps == options_menu_apps[0]:
    del_session_state(option="app_2_option")

    if 'app_1_option_1_var_flagAccept' not in st.session_state:
        st.session_state.app_1_option_1_var_flagAccept = False

    photovoltaic.page_apps_main(title=options_menu_apps[0])
                
elif menu_apps == options_menu_apps[1]:
    del_session_state(option="app_1_option")
    battery.page_apps_main(title=options_menu_apps[1])
