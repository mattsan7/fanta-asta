import streamlit as st


def page_init(title: str):
    st.set_page_config(
        page_title=f"{title} - Fanta Asta",
        page_icon="💲",
        initial_sidebar_state="auto",
        menu_items=None,
    )

    st.header(title)
