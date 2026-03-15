# -*- coding: utf-8 -*-
import streamlit as st



pages = {
    "Inicio": [
        st.Page("pages_Home//generalities.py", title="Generalidades", icon=":material/home:"),
        st.Page("pages_Home//resources.py", title="Recursos", icon=":material/laptop_windows:")
    ],
    "Componentes": [
        st.Page("pages_Original//01_Componentes.py", title="Listado", icon=":material/format_list_numbered:"),
    ],
    "Generación": [
        st.Page("pages_Original//08_Generación On-Grid.py", title="On-Grid", icon=":material/flash_on:"),
        st.Page("pages_Original//09_Generación Off-Grid.py", title="Off-Grid", icon=":material/flash_off:"),
    ],
}

pg = st.navigation(pages, expanded=False)
pg.run()