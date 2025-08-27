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

    st.markdown("### View, Add and Edit your Housing Data:")

    # Make the 'Link' column clickable
    df["Link"] = df["Link"].apply(lambda x: f"[Link]({x})" if pd.notnull(x) and str(x).strip() not in ["", "nan"] else "")
    
    # Display the editable dataframe
    edit_df = st.data_editor(df, num_rows="dynamic", key="housing_editor",
                            # make the 'Link' column clickable
                            column_config={"Link": st.column_config.LinkColumn(
                                "Link", display_text="Open"
                            )})

    if st.button("Save Changes"):
        edit_df.to_csv("Data/Housing.csv", index=False)
        st.success("Changes saved!")

    # Add delete buttons next to the dataframe
    st.markdown("#### Delete a Row")
    
    col1, col2 = st.columns(2)
    with col1:
        row_to_delete = st.number_input("Enter row index to delete (First Row = 0)", min_value=0, max_value=len(edit_df)-1, step=1)
    with col2:
        if st.button("Delete Selected Row"):
            edit_df = edit_df.drop(row_to_delete)
            edit_df.to_csv("Data/Housing.csv", index=False)
            st.success(f"Deleted row {row_to_delete}")
            st.rerun()

    st.sidebar.markdown("### Add New Housing Option")
    with st.sidebar.form("add_housing_form"):
        name = st.text_input("Name")
        link = st.text_input("Link")
        adress = st.text_input("Adress")
        rent = st.number_input("Rent", min_value=0, step=1)
        distance = st.number_input("Distance", min_value=0.0, step=0.1)
        rooms = st.number_input("Rooms", min_value=0.0, step=0.5)
        size = st.number_input("Size", min_value=0.0, step=0.1)
        kitchen = st.checkbox("Kitchen")
        furnished = st.checkbox("Furnished")
        rental_period = st.text_input("Rental Period")
        parking = st.checkbox("Parking")
        custom = st.text_input("Custom")
        submitted = st.form_submit_button("Add")

        if submitted:
            new_row = {
                "Name": name,
                "Link": link,
                "Adress": adress,
                "Rent": int(rent),
                "Distance": float(distance),
                "Rooms": float(rooms),
                "Size": float(size),
                "Kitchen": kitchen,
                "Furnished": furnished,
                "Rental Period": rental_period,
                "Parking": parking,
                "Custom": custom
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv("Data/Housing.csv", index=False)
            st.sidebar.success("New housing option added!")
            st.rerun()
    