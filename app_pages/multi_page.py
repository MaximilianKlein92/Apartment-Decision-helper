import streamlit as st

class Multipage:
    def __init__(self, app_name: str, page_icon=":compass:") -> None:
        # List to store pages as dicts with title and function
        self.pages = []   # [{"title":..., "function":...}]
        self.app_name = app_name
        # Set Streamlit page config
        st.set_page_config(page_title=self.app_name, page_icon=page_icon)
        # Initialize page index in session state if not present
        if "page_index" not in st.session_state:
            st.session_state.page_index = 0

    def add_page(self, title: str, func) -> None:
        # Add a new page with title and function
        self.pages.append({"title": title, "function": func})

    def index_of(self, title: str) -> int:
        # Find index of page by title
        for i, p in enumerate(self.pages):
            if p["title"] == title:
                return i
        # Raise error if page not found
        raise ValueError(f"Page '{title}' not found")

    def go(self, title_or_index):
        # Change current page by title or index and rerun Streamlit
        idx = title_or_index if isinstance(title_or_index, int) else self.index_of(title_or_index)
        st.session_state.page_index = idx
        st.rerun()

    def run(self):
        # Display app title
        st.title(self.app_name)
        # Sidebar selectbox for page navigation
        sel = st.sidebar.selectbox(
            "Sections",
            options=list(range(len(self.pages))),
            format_func=lambda i: self.pages[i]["title"],
            index=st.session_state.page_index,
        )
        # Update page index if selection changed
        if sel != st.session_state.page_index:
            st.session_state.page_index = sel

        # Call the function of the selected page, passing self (the app)
        self.pages[st.session_state.page_index]["function"](self)
