import streamlit as st
import pandas as pd
from urllib.parse import quote_plus
import io

def page_housing_body(app):
    
    df = pd.read_csv("Data/Housing.csv", dtype={
        "Name": str,
        "Link": str,
        "Adress": str,           # note the CSV uses 'Adress'
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

    # helper: build Google Maps "place" URL
    def maps_place_url(addr):
        if pd.isna(addr):
            return ""
        s = str(addr).strip()
        if s == "" or s.lower() == "nan":
            return ""
        return f"https://www.google.com/maps/place/{quote_plus(s)}"

    st.write("---" )

    col1, col2 = st.columns(2)
    with col1:
        st.header("Housing Options")
    with col2:
        uploaded = st.file_uploader(
            "Upload CSV", type=["csv"], key="housing_uploader",
            help="Upload a CSV file to replace the current housing data."
        )

        if uploaded is not None:
            try:
                # Variante A: saubere Kopie -> immer frischer Stream
                uploaded_bytes = uploaded.getvalue()
                uploaded_df = pd.read_csv(io.BytesIO(uploaded_bytes))

                # Alternativ (Variante B): Stream zurückspulen
                # uploaded.seek(0)
                # uploaded_df = pd.read_csv(uploaded)

                expected_columns = [
                    "Name", "Link", "Adress", "Rent", "Distance", "Rooms", "Size",
                    "Kitchen", "Furnished", "Rental Period", "Parking", "Custom"
                ]
                if all(col in uploaded_df.columns for col in expected_columns):
                    uploaded_df = uploaded_df[expected_columns]
                    uploaded_df.to_csv("Data/Housing.csv", index=False)
                    st.success("File uploaded and data replaced successfully!")

                    # Wichtig: Uploader-State leeren, damit beim nächsten rerun
                    # nicht erneut aus einem verbrauchten Stream gelesen wird.
                    st.session_state.pop("housing_uploader", None)
                    st.rerun()
                else:
                    st.error(
                        "Uploaded CSV must contain the following columns: "
                        + ", ".join(expected_columns)
                    )
            except Exception as e:
                st.error(f"Error reading uploaded file: {e}")


    st.write("---" )
    st.markdown("### View, Add and Edit your Housing Data:")

    # compute (or recompute) the clickable link column
    df["Adress_Link"] = df["Adress"].apply(maps_place_url)

    edit_df = st.data_editor(
        df,
        num_rows="dynamic",
        key="housing_editor",
        column_config={
            "Link": st.column_config.LinkColumn("Link", display_text="Open"),
            "Adress": st.column_config.TextColumn("Adress"),
            "Adress_Link": st.column_config.LinkColumn("Adress (Maps)", display_text="Open in Maps"),
        },
        column_order=["Name", "Link", "Adress", "Adress_Link", "Rent", "Distance", "Rooms", "Size",
                      "Kitchen", "Furnished", "Rental Period", "Parking", "Custom"],
        use_container_width=True,
        disabled=["Adress_Link"]  # prevent manual edits of the generated URL
    )

    # live recompute after edits so new/changed addresses get a link immediately
    edit_df["Adress_Link"] = edit_df["Adress"].apply(maps_place_url)

    if st.button("Save Changes"):
        to_save = edit_df.drop(columns=["Adress_Link"], errors="ignore")
        to_save.to_csv("Data/Housing.csv", index=False)
        st.success("Changes saved!")
        st.rerun()

    # Add delete buttons below the dataframe
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
    