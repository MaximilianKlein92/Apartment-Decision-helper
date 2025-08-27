import streamlit as st
import pandas as pd
import io
from urllib.parse import quote_plus
import plotly.graph_objects as go

# ------------------------ Config ------------------------

CSV_PATH = "Data/Housing.csv"
EXPECTED_COLUMNS = [
    "Name", "Link", "Adress", "Rent", "Distance", "Rooms", "Size",
    "Kitchen", "Furnished", "Rental Period", "Parking", "Custom"
]

DTYPES = {
    "Name": str,
    "Link": str,
    "Adress": str,  # CSV uses 'Adress'
    "Rent": int,
    "Distance": float,
    "Rooms": float,
    "Size": float,
    "Kitchen": bool,
    "Furnished": bool,
    "Rental Period": str,
    "Parking": bool,
    "Custom": str,
}

# ------------------------ Helpers ------------------------

def maps_place_url(addr) -> str:
    """Build Google Maps 'place' URL from a free-text address."""
    if pd.isna(addr):
        return ""
    s = str(addr).strip()
    if s == "" or s.lower() == "nan":
        return ""
    return f"https://www.google.com/maps/place/{quote_plus(s)}"

def add_maps_link_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add/refresh generated clickable link column."""
    df = df.copy()
    df["Adress_Link"] = df["Adress"].apply(maps_place_url)
    return df

def validate_columns(df: pd.DataFrame) -> bool:
    return all(col in df.columns for col in EXPECTED_COLUMNS)

def load_housing(path: str = CSV_PATH) -> pd.DataFrame:
    return pd.read_csv(path, dtype=DTYPES)

def save_housing(df: pd.DataFrame, path: str = CSV_PATH) -> None:
    df.to_csv(path, index=False)

def parse_uploaded_csv(uploaded_file) -> pd.DataFrame:
    """Read uploaded CSV from a fresh BytesIO stream."""
    data = uploaded_file.getvalue()
    return pd.read_csv(io.BytesIO(data))

# ------------------------ UI Blocks ------------------------

def uploader_block():
    uploaded = st.file_uploader(
        "Upload CSV", type=["csv"], key="housing_uploader",
        help="Upload a CSV file to replace the current housing data."
    )
    if uploaded is not None:
        try:
            up_df = parse_uploaded_csv(uploaded)
            if not validate_columns(up_df):
                st.error("Uploaded CSV must contain: " + ", ".join(EXPECTED_COLUMNS))
                return
            up_df = up_df[EXPECTED_COLUMNS]
            save_housing(up_df)
            st.success("File uploaded and data replaced successfully!")
            st.session_state.pop("housing_uploader", None)  # clear used stream
            st.rerun()
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")

def editor_block(df: pd.DataFrame) -> pd.DataFrame:
    """Render editor (with clickable link column). Return edited df."""
    df_with_links = add_maps_link_column(df)

    edited = st.data_editor(
        df_with_links,
        num_rows="dynamic",
        key="housing_editor",
        column_config={
            "Link": st.column_config.LinkColumn("Link", display_text="Open"),
            "Adress": st.column_config.TextColumn("Adress"),
            "Adress_Link": st.column_config.LinkColumn("Adress (Maps)", display_text="Open in Maps"),
        },
        column_order=[
            "Name", "Link", "Adress", "Adress_Link", "Rent", "Distance", "Rooms", "Size",
            "Kitchen", "Furnished", "Rental Period", "Parking", "Custom"
        ],
        use_container_width=True,
        disabled=["Adress_Link"],  # generated
    )

    # refresh generated column after edits
    edited["Adress_Link"] = edited["Adress"].apply(maps_place_url)
    return edited

def actions_block(edited: pd.DataFrame):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Changes"):
            to_save = edited.drop(columns=["Adress_Link"], errors="ignore")
            save_housing(to_save)
            st.success("Changes saved!")
            st.rerun()
    with col2:
        # Download what is currently shown (without generated column)
        to_download = edited.drop(columns=["Adress_Link"], errors="ignore")
        csv_bytes = to_download.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv_bytes, file_name="Housing.csv", mime="text/csv")

def delete_block(edited: pd.DataFrame):
    st.markdown("#### Delete a Row")
    c1, c2 = st.columns(2)
    with c1:
        max_idx = max(len(edited) - 1, 0)
        row_to_delete = st.number_input(
            "Enter row index to delete (First Row = 0)",
            min_value=0, max_value=max_idx, step=1
        )
    with c2:
        if st.button("Delete Selected Row"):
            df_del = edited.drop(index=row_to_delete).reset_index(drop=True)
            df_del = df_del.drop(columns=["Adress_Link"], errors="ignore")
            save_housing(df_del)
            st.success(f"Deleted row {row_to_delete}")
            st.rerun()

def add_sidebar_block():
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
                "Custom": custom,
            }
            base = load_housing()
            base = pd.concat([base, pd.DataFrame([new_row])], ignore_index=True)
            save_housing(base)
            st.sidebar.success("New housing option added!")
            st.rerun()

def plotly_block():
    df = load_housing()
    if df.empty:
        st.info("No data to plot. Please add housing options first.")
        return

    axis_options = ["Distance", "Rent", "Rooms", "Size"]
    hue_options = ["Rooms", "Size", "Kitchen", "Furnished", "Parking"]
    size_options = ["Size", "Rent", "Distance", "Rooms"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        x_axis = st.selectbox("X Axis", axis_options, index=0)
    with col2:
        y_axis = st.selectbox("Y Axis", axis_options, index=1)
    with col3:
        hue = st.selectbox("Hue (Color)", hue_options, index=0)
    with col4:
        bubble_size = st.selectbox("Bubble Size", size_options, index=3)

    # Prepare hover text with all info for each point
    hover_text = [
        "<br>".join([
            f"Name: {row['Name']}",
            f"Adress: {row['Adress']}",
            f"Rent: {row['Rent']}",
            f"Distance: {row['Distance']}",
            f"Rooms: {row['Rooms']}",
            f"Size: {row['Size']}",
            f"Kitchen: {row['Kitchen']}",
            f"Furnished: {row['Furnished']}",
            f"Rental Period: {row['Rental Period']}",
            f"Parking: {row['Parking']}",
            f"Custom: {row['Custom']}"
        ])
        for _, row in df.iterrows()
    ]

    # Handle boolean columns for color/hue
    marker_color = df[hue]
    if marker_color.dtype == bool:
        marker_color = marker_color.astype(int)

    marker_size = df[bubble_size]
    # Normalize marker size for better visualization
    marker_size = (marker_size - marker_size.min()) / (marker_size.max() - marker_size.min() + 1e-6) * 40 + 10

    fig = go.Figure(data=go.Scatter(
        x=df[x_axis],
        y=df[y_axis],
        mode="markers",
        marker=dict(
            size=marker_size,
            color=marker_color,
            showscale=True,
            colorscale="Viridis"
        ),
        text=hover_text,
        hovertemplate="%{text}<extra></extra>"
    ))
    fig.update_layout(
        title=f"Housing Options: {y_axis} vs {x_axis} (Size: {bubble_size}, Color: {hue})",
        xaxis_title=x_axis,
        yaxis_title=y_axis
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------ Page ------------------------

def page_housing_body(app):
    st.write("---")

    col1, col2 = st.columns(2)
    with col1:
        st.header("Housing Options")
    with col2:
        uploader_block()


    plotly_block()
    st.info("Hover over a marker to see all details. Use the table below to open the link.")

    st.write("---")
    st.markdown("### View, Add and Edit your Housing Data:")

    df = load_housing()
    edited = editor_block(df)
    actions_block(edited)
    delete_block(edited)
    add_sidebar_block()
