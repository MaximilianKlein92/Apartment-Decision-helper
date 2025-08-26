import streamlit as st

def page_start_body(app):
    st.image("Media/logo.png", use_container_width=True)
    st.markdown("# Choose your section")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 Housing", use_container_width=True):
            app.go("Housing")
    with c2:
        if st.button("✈️ Hotels", use_container_width=True):
            app.go("Hotels")
    with c3:
        if st.button("🏃 Activities", use_container_width=True):
            app.go("Activities")