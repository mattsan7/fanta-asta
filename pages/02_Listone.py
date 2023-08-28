import streamlit as st
# from pandas.api.types import is_categorical_dtype, is_datetime64_any_dtype, is_numeric_dtype, is_object_dtype
import pandas as pd

from utils import helpers

helpers.page_init('Listone', layout='wide')

# UI for filtering dataframe in-app
# credits to: https://blog.streamlit.io/auto-generate-a-dataframe-filtering-ui-in-streamlit-with-filter_dataframe/


def filter_dataframe(df: pd.DataFrame, admissible_columns: list = None) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe
        admissible_columns (list):

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters", value=True)

    if not modify:
        return df

    df = df.copy()

    modification_container = st.container()

    with modification_container:

        if admissible_columns is None:
            admissible_columns = [_c for _c in df.columns if df.dtypes[_c] == 'object']
        to_filter_columns = st.multiselect("Filtra tabella:", admissible_columns, default=admissible_columns)

        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Valori in {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )

                df = df[df[column].isin(user_cat_input)]

            else:
                user_text_input = right.text_input(
                    f"Testo da cercare in {column}",
                )
                if user_text_input:

                    df = df[df[column].astype(str).str.lower().str.contains(user_text_input)]

    return df


with helpers.get_db_engine() as conn:
    results = conn.execute("""SELECT player_name, player_role, team, owner, price FROM players""").fetchall()

listone = pd.DataFrame(results, columns=['Nome', 'Ruolo', 'Squadra', 'Proprietario', 'Costo'])

st.dataframe(filter_dataframe(listone, admissible_columns=['Nome', 'Ruolo', 'Squadra', 'Proprietario']),
             hide_index=True, width=1000)
