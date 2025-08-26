import streamlit as st

class Multipage:
    def __init__(self, app_name: str, page_icon=":compass:") -> None:
        self.pages = []   # [{"title":..., "function":...}]
        self.app_name = app_name
        st.set_page_config(page_title=self.app_name, page_icon=page_icon)
        if "page_index" not in st.session_state:
            st.session_state.page_index = 0

    def add_page(self, title: str, func) -> None:
        self.pages.append({"title": title, "function": func})

    def index_of(self, title: str) -> int:
        for i, p in enumerate(self.pages):
            if p["title"] == title:
                return i
        raise ValueError(f"Page '{title}' not found")

    def go(self, title_or_index):
        idx = title_or_index if isinstance(title_or_index, int) else self.index_of(title_or_index)
        st.session_state.page_index = idx
        st.rerun()

    def run(self):
        st.title(self.app_name)
        sel = st.sidebar.selectbox(
            "Sections",
            options=list(range(len(self.pages))),
            format_func=lambda i: self.pages[i]["title"],
            index=st.session_state.page_index,
        )
        if sel != st.session_state.page_index:
            st.session_state.page_index = sel

        # app an Page-Funktionen übergeben
        self.pages[st.session_state.page_index]["function"](self)
