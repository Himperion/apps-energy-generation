# -*- coding: utf-8 -*-

import streamlit as st


text = {
    "subheader_1" : "Implementación del proyecto **Diseño de un aplicativo para la estimación de la operación de sistemas de generación eléctrica a partir de balances de potencia y energía**"
}

st.sidebar.link_button(":violet-badge[**Ir a la app de herramientas**]", "https://app-nasa-power.streamlit.app/", icon="🔧")

st.markdown("# 🏠 Inicio")

tab1, tab2 = st.tabs(["Descripción", "Equipo humano"])

with tab1:
    st.markdown(text["subheader_1"])

    st.link_button(":orange-badge[**Presentación TdeG**]", "https://www.canva.com/design/DAGmHexFq7U/mIh7Px5eheIPUwhtWkfnmw/edit?utm_content=DAGmHexFq7U&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton", icon="👨‍🏫")

with tab2:

    with st.container(border=True):
        col1, col2 = st.columns([0.3, 0.7], vertical_alignment="center")

        with col1:
            st.image("images/member2.jpg", width=200)

        with col2:
            st.subheader("Darío Fernando Gonzalez Fontecha", divider=True)
            st.caption("Comprometido con el desarrollo sostenible, energias renovables y la implementación de tecnologías innovadoras para el sector agropecuario. Con conocimientos en MATLAB, Python y desarrollo Web, oriento mis habilidades hacia el uso de Big Data y computación en la nube para transformar el campo colombiano.")
            st.markdown("📧 dario.gonzalez@correo.uis.edu.co")

    with st.container(border=True):
        col1, col2 = st.columns([0.3, 0.7], vertical_alignment="center")

        with col1:
            st.image("images/member1.jpg", width=200)

        with col2:
            st.subheader("José Camilo Rojas Páez", divider=True)
            st.caption("Estudiante de último semestre de Ingeniería Eléctrica en la Universidad Industrial de Santander, con una sólida base en matemáticas y lógica de programación aplicadas a la resolución de problemas. Experiencia en el uso de herramientas de software y programación, como MATLAB, Python, Streamlit y Power BI, para el análisis y procesamiento de datos.")
                
            st.markdown("📧 jose.rojas9@correo.uis.edu.co")
            st.markdown("🐈‍⬛ https://github.com/Himperion")

    with st.container(border=True):
        col1, col2 = st.columns([0.3, 0.7], vertical_alignment="center")

        with col1:
            st.image("images/member3.jpg", width=200)

        with col2:
            st.subheader("German Alfonso Osma Pinto", divider=True)
            st.caption("Investigador Senior MINCIENCIAS y miembro del Grupo de Investigación en Sistemas de Energía Eléctrica Eléctrica – GISEL. Cuenta con más de 10 años de experiencia docente en pregrado y posgrado. Ha participado en diversos proyectos con financiación MINCIENCIAS y UIS. Lleva más de 15 años en el quehacer investigativo relacionado con la generación renovable y construcción sostenible. Actualmente, apoya el Semillero de Investigación en Recursos Energéticos Distribuidos - SIRED.")
            st.markdown("📧 gealosma@uis.edu.co")

