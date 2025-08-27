import streamlit as st
import pandas as pd

def page_housing_body(app):
    st.header("Housing Options")
    st.write("Welcome to the Housing Comparison page")

    df = pd.read_csv("Data/Housing.csv", dtype = {
        "row_id": int,
        "Name": str,
        "Link": str,
        "Adress": str,
        "Rent": int,
        "Distance": float,
        "Rooms": float,
        "Size": float,
        "Kitchen": bool,
        "Furnished": bool,
        "Rental Period": str,
        "Parking": bool,
        "Custom": str
    })

    edit_df = st.data_editor(df, num_rows="dynamic")

    if st.button("Save Changes"):
        edit_df.to_csv("Data/Housing.csv", index=False)
        st.success("Changes saved!")