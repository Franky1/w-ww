import streamlit as st
import pandas as pd
import seaborn as sb
import base64
from dataprep.eda import create_report
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# more algorithms to be implemented later

#st.set_option('deprecation.showPyplotGlobalUse', False)

#---------------------------------#
# User Authentication Section

# DB Management
import sqlite3
conn = sqlite3.connect('data.db', check_same_thread=False)
c = conn.cursor()

def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')

def add_userdata(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data

def load_view():
    menu = ["Home", "Login", "Sign Up"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        app()

    elif choice == "Login":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.button("Login"):
            create_usertable()
            result = login_user(username,password)
            if result:
                st.success("Logged in as {}".format(username))

                task = st.selectbox("Task", ["Create New Project", "View Existing Projects"])
                if task == "Create New Project":
                    form()
                elif task == "View Existing Projects":
                    st.subheader("Select Existing Project")
            else:
                st.sidebar.warning("Incorrect Username/Password")
        app()

    elif choice == "Sign Up":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password",type='password')

        if st.button("Create Account"):
            create_usertable()
            add_userdata(new_user,new_password)
            st.success("You have successfully created a new account")
            st.info("Go to Login Menu to login")

def form():
    with st.form(key = "create"):
        name = st.text_input(label = "Enter the model name")
        submit = st.form_submit_button(label= "Create Project")
        if submit:
            app()

#---------------------------------#
# Home Page

def app():
    #---------------------------------#
    st.write("""
    # Machine Learning App

    In this implementation, the *RandomForestRegressor()* function is used in this app for build a regression model using the **Random Forest** algorithm.

    Try adjusting the hyperparameters!

    """)

    #---------------------------------#
    # Sidebar - Collects user input features into dataframe
    with st.sidebar.header('1. Upload your CSV data'):
        uploaded_file = st.sidebar.file_uploader("Upload your input CSV file", type=["csv"])
        st.sidebar.markdown("""
    [Example CSV input file](https://raw.githubusercontent.com/zhangandrew37/ML-web-app/main/Data-AI-1.csv?token=ANATUZW67F4KGSLYWO73LMTBFBL6K)
    """)

    # Sidebar - Specify parameter settings
    with st.sidebar.header('2. Set Parameters'):
        split_size = st.sidebar.slider('Data split ratio (% for Training Set)', 10, 90, 80, 5)

    with st.sidebar.subheader('2.1. Learning Parameters'):
        parameter_n_estimators = st.sidebar.slider('Number of estimators (n_estimators)', 0, 1000, 100, 100)
        parameter_max_features = st.sidebar.select_slider('Max features (max_features)', options=['auto', 'sqrt', 'log2'])
        parameter_min_samples_split = st.sidebar.slider('Minimum number of samples required to split an internal node (min_samples_split)', 1, 10, 2, 1)
        parameter_min_samples_leaf = st.sidebar.slider('Minimum number of samples required to be at a leaf node (min_samples_leaf)', 1, 10, 2, 1)

    with st.sidebar.subheader('2.2. General Parameters'):
        parameter_random_state = st.sidebar.slider('Seed number (random_state)', 0, 1000, 42, 1)
        parameter_criterion = st.sidebar.select_slider('Performance measure (criterion)', options=['mse', 'mae'])
        parameter_bootstrap = st.sidebar.select_slider('Bootstrap samples when building trees (bootstrap)', options=[True, False])
        parameter_oob_score = st.sidebar.select_slider('Whether to use out-of-bag samples to estimate the R^2 on unseen data (oob_score)', options=[False, True])
        parameter_n_jobs = st.sidebar.select_slider('Number of jobs to run in parallel (n_jobs)', options=[1, -1])

    #---------------------------------#
    # Main panel

    #---------------------------------#
    # Model building
    def build_model():
        X = df.iloc[:,:-1] # Using all column except for the last column as X
        Y = df.iloc[:,-1] # Selecting the last column as Y

        # Data splitting
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=(100-split_size)/100)

        st.markdown('**1.2. Data splits**')
        st.write('Training set')
        st.info(X_train.shape)
        st.write('Test set')
        st.info(X_test.shape)

        st.markdown('**1.3. Variable details**:')
        st.write('X variable')
        st.info(list(X.columns))
        st.write('Y variable')
        st.info(Y.name)

        rf = RandomForestRegressor(n_estimators=parameter_n_estimators,
            random_state=parameter_random_state,
            max_features=parameter_max_features,
            criterion=parameter_criterion,
            min_samples_split=parameter_min_samples_split,
            min_samples_leaf=parameter_min_samples_leaf,
            bootstrap=parameter_bootstrap,
            oob_score=parameter_oob_score,
            n_jobs=parameter_n_jobs)

        rf.fit(X_train, Y_train)
        score = rf.score(X_train, Y_train)
        st.write('Prediction Performance Score:')
        st.write(score);

        st.subheader('2. Model Performance')

        st.markdown('**2.1. Training set**')
        Y_pred_train = rf.predict(X_train)
        st.write('Coefficient of determination ($R^2$):')
        st.info( r2_score(Y_train, Y_pred_train) )

        st.write('Error (MSE or MAE):')
        st.info( mean_squared_error(Y_train, Y_pred_train) )

        st.markdown('**2.2. Test set**')
        Y_pred_test = rf.predict(X_test)
        st.write('Coefficient of determination ($R^2$):')
        st.info( r2_score(Y_test, Y_pred_test) )

        st.write('Error (MSE or MAE):')
        st.info( mean_squared_error(Y_test, Y_pred_test) )

        st.subheader('3. Model Parameters')
        st.write(rf.get_params())

    def generate_report():
        left, right = st.columns(2)
        with left:
            if st.button('View detailed report in new tab'):
                report = create_report(df)
                report.show_browser()
        with right:
            if st.button('Download detailed report'):
                    report = create_report(df)
                    report.save('Report')
                    report.show_browser()

    def generate_plot():
        numeric_columns = df.select_dtypes(['float', 'int']).columns
        st.sidebar.subheader("3. Scatter Plot Setup")
        select_box1 = st.sidebar.selectbox(label='X axis', options=numeric_columns)
        select_box2 = st.sidebar.selectbox(label='Y axis', options=numeric_columns)
        g = sb.relplot(x=select_box1, y=select_box2, data=df, height=6, aspect=11.7/8.27)
        st.pyplot()

    # Displays the dataset
    st.subheader('1. Dataset')

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        generate_report()
        generate_plot()
        st.markdown('**1.1. Glimpse of dataset**')
        st.write(df)
        build_model()

    else:
        st.info('Awaiting for CSV file to be uploaded.')
        example_data = open("Data-AI-1.csv")
        df = pd.read_csv(example_data)
        st.markdown('*Sample dataset provided below.*')
        temp_df = pd.DataFrame(df)
        csv = temp_df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}">Download sample CSV File</a> (right-click and save as &lt;file_name&gt;.csv)'
        st.markdown(href, unsafe_allow_html=True)

        generate_report()
        generate_plot()

        st.markdown('**1.1. Glimpse of dataset**')
        st.write("Wastewater treatment plant data")
        st.write(df)
        build_model()
