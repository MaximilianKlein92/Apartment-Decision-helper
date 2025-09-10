# ------------------------ Language Support ------------------------

LANGUAGES = {
    "en": {
        "flag": "🇬🇧",
        "header": "Housing Options",
        "upload_csv": "Upload CSV",
        "upload_help": "Upload a CSV file to replace the current housing data.",
        "upload_error": "Uploaded CSV must contain: ",
        "upload_success": "File uploaded and data replaced successfully!",
        "upload_read_error": "Error reading uploaded file",
        "hover_info": "Hover over a marker to see all details. Use the table below to open the link or maps.",
        "edit_title": "### View, Edit or Delete your Housing Data:",
        "edit_info": "Use the Add form in the sidebar to add new housing options to ensure functionality.",
    },
    "de": {
        "flag": "🇩🇪",
        "header": "Wohnungsoptionen",
        "upload_csv": "CSV hochladen",
        "upload_help": "Laden Sie eine CSV-Datei hoch, um die aktuellen Wohnungsdaten zu ersetzen.",
        "upload_error": "Hochgeladene CSV muss enthalten: ",
        "upload_success": "Datei hochgeladen und Daten erfolgreich ersetzt!",
        "upload_read_error": "Fehler beim Lesen der hochgeladenen Datei",
        "hover_info": "Fahren Sie mit der Maus über einen Marker, um alle Details zu sehen. Verwenden Sie die Tabelle unten, um den Link oder die Karte zu öffnen.",
        "edit_title": "### Wohnungsdaten anzeigen, bearbeiten oder löschen:",
        "edit_info": "Verwenden Sie das Hinzufügen-Formular in der Seitenleiste, um neue Wohnungsoptionen hinzuzufügen.",
    }
}
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

def uploader_block(texts):
    uploaded = st.file_uploader(
        texts["upload_csv"], type=["csv"], key="housing_uploader",
        help=texts["upload_help"]
    )
    if uploaded is not None:
        try:
            up_df = parse_uploaded_csv(uploaded)
            if not validate_columns(up_df):
                st.error(texts["upload_error"] + ", ".join(EXPECTED_COLUMNS))
                return
            up_df = up_df[EXPECTED_COLUMNS]
            save_housing(up_df)
            st.success(texts["upload_success"])
            st.session_state.pop("housing_uploader", None)  # clear used stream
            st.rerun()
        except Exception as e:
            st.error(f"{texts['upload_read_error']}: {e}")

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
        disabled=["Adress_Link"],  # generated column
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

def add_sidebar_block():
    st.sidebar.markdown("### Add / Hinzufügen")
    if "add_form_submitted" not in st.session_state:
        st.session_state["add_form_submitted"] = False

    with st.sidebar.form("add_housing_form", clear_on_submit=True):
        name = st.text_input("Name", key="add_name")
        link = st.text_input("Link", key="add_link")
        adress = st.text_input("Adress", key="add_adress")
        rent = st.number_input("Rent / Miete", min_value=0, step=1, key="add_rent")
        distance = st.number_input("Distance", min_value=0.0, step=0.1, key="add_distance")
        rooms = st.number_input("Rooms / Räume", min_value=0.0, step=0.5, key="add_rooms")
        size = st.number_input("Size / Größe", min_value=0.0, step=0.1, key="add_size")
        kitchen = st.checkbox("Kitchen / Küche", key="add_kitchen")
        furnished = st.checkbox("Furnished / Möbliert", key="add_furnished")
        rental_period = st.text_input("Rental Period / Mietzeitraum", key="add_rental_period")
        parking = st.checkbox("Parking / Parkplatz", key="add_parking")
        custom = st.text_input("Custom / Notizen", key="add_custom")
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
            st.session_state["add_form_submitted"] = True
            st.sidebar.success("New housing option added!")
            st.rerun()
    # After rerun, clear the form fields
    if st.session_state.get("add_form_submitted", False):
        for key in [
            "add_name", "add_link", "add_adress", "add_rent", "add_distance",
            "add_rooms", "add_size", "add_kitchen", "add_furnished",
            "add_rental_period", "add_parking", "add_custom"
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state["add_form_submitted"] = False

def plotly_block():
    df = load_housing()
    if df.empty:
        st.info("No data to plot. Please add housing options first.")
        return

    # Multi-select for which rows to display
    all_indices = list(df.index)
    selected_indices = st.multiselect(
        "Select housing options to display / Wählen Sie Wohnungsoptionen aus:", 
        options=all_indices, 
        default=all_indices,
        format_func=lambda idx: f"{idx}: {df.loc[idx, 'Name']}"
    )
    if not selected_indices:
        st.info("No options selected.")
        return
    df = df.loc[selected_indices].reset_index(drop=True)

    axis_options = ["Distance", "Rent", "Rooms", "Size"]
    hue_options = ["Rooms", "Distance", "Size", "Kitchen", "Furnished", "Parking"]
    size_options = ["Rent", "Distance", "Rooms","Size"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        x_axis = st.selectbox("X Axis", axis_options, index=0)
    with col2:
        y_axis = st.selectbox("Y Axis", axis_options, index=1)
    with col3:
        hue = st.selectbox("Color / Farbe", hue_options, index=0)
    with col4:
        bubble_size = st.selectbox("Bubble Size / Blasengröße", size_options, index=3)

    # Prepare hover text with all info for each point
    hover_text = [
        "<br>".join([
            f"Index: {row.name}",
            f"Name: {row['Name']}",
            f"Adress: {row['Adress']}",
            f"Rent / Miete: {row['Rent']}",
            f"Distance: {row['Distance']}",
            f"Rooms: {row['Rooms']}",
            f"Size / Größe: {row['Size']}",
            f"Kitchen / Küche: {row['Kitchen']}",
            f"Furnished / Möbliert: {row['Furnished']}",
            f"Rental Period / Mietdauer: {row['Rental Period']}",
            f"Parking: {row['Parking']}",
            f"Custom / Notizen: {row['Custom']}",
            f"Rent/Size / Quadratmeterpreis: {row['Rent'] / row['Size'] if row['Size'] > 0 else 0:.2f} €/m²"
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

    # Show the scatter plot below the metrics
    fig.update_layout(
        title=(
            f"Housing Options: {y_axis} vs {x_axis} "
            f"(Size: {bubble_size}, Color: {hue})"
        ),
        xaxis_title=x_axis,
        yaxis_title=y_axis,
        height=500
    )

    # Show metrics above the plot, under selection options

    st.plotly_chart(fig, use_container_width=True, key="housing_plot")

    st.markdown("#### Mean's / Mittelwerte")
    col_metrics = st.columns(4)
    with col_metrics[2]:
        mean_rent = df["Rent"].mean()
        st.metric(
            label="",
            value=f"{mean_rent:,.0f} €"
        )
    with col_metrics[1]:
        mean_size = df["Size"].mean()
        st.metric(
            label="",
            value=f"{mean_size:,.2f} m²"
        )
    with col_metrics[3]:
        Prizepersquaremeter = df["Rent"] / df["Size"]
        mean_prizepersqm = Prizepersquaremeter.mean()
        st.metric(
            label="",
            value=f"{mean_prizepersqm:,.2f} €/m²"
        )
    with col_metrics[0]:
        mean_distance = df["Distance"].mean()
        st.metric(
            label="",
            value=f"{mean_distance:,.2f} km"
        )



# ------------------------ Page ------------------------

def page_housing_body(app):
    # Language toggle in top right
    if "lang" not in st.session_state:
        st.session_state["lang"] = "en"
    lang = st.session_state["lang"]
    texts = LANGUAGES[lang]

    flag_cols = st.columns([8, 1, 1])
    with flag_cols[0]:
        st.header(texts["header"])
        uploader_block(texts)
    with flag_cols[1]:
        if st.button("🇬🇧", key="lang_en_btn", use_container_width=True):
            st.session_state["lang"] = "en"
            st.rerun()
        if lang == "en":
            st.markdown("<span style='color:#4CAF50;font-weight:bold;'>EN</span>", unsafe_allow_html=True)
    with flag_cols[2]:
        if st.button("🇩🇪", key="lang_de_btn", use_container_width=True):
            st.session_state["lang"] = "de"
            st.rerun()
        if lang == "de":
            st.markdown("<span style='color:#4CAF50;font-weight:bold;'>DE</span>", unsafe_allow_html=True)

    
    plotly_block()
    st.info(texts["hover_info"])

    st.write("---")
    st.markdown(texts["edit_title"])
    st.info(texts["edit_info"])

    
    df = load_housing()
    edited = editor_block(df)
    actions_block(edited)
    add_sidebar_block()
