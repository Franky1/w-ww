import streamlit as st
from views import data


def load_view():
    empty0 = st.empty()
    empty0.title('Create an ML project')
    with st.form(key = "create", clear_on_submit=False):
        empty1 = st.empty()
        empty2 = st.empty()
        empty3 = st.empty()
        empty4 = st.empty()
        name = empty1.text_input(label = "Enter the model name")
        type = empty2.selectbox("Type of ML modeling", ('Regression', 'Classification'))
        df = empty3.file_uploader("Upload your data (CSV)")
        submit = empty4.form_submit_button(label= "Create Project")
        if (submit):
            empty0.empty()
            empty1.empty()
            empty2.empty()
            empty3.empty()
            empty4.empty()
            data.load_view_external()
            st.write("If the data is not showing up or if you encounter other issues, please use the navbar at the top to navigate through the app.")
            submit = st.form_submit_button(label= "Cancel")
