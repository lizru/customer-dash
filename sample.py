import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import streamlit as st
import math
import numpy as np

sns.set_theme(style="darkgrid", palette="PuBuGn_r") 

def check_validity(df):
    # Check if all required columns are in the DataFrame
    required_columns = ["CustomerID","Age","Gender","ProductCategory","PurchaseAmount","PurchaseDate"]
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.warning(f"Warning: The following required columns are missing: {', '.join(missing_cols)}")
        return False
    return True

def preprocess(uploaded_file):
    df = pd.read_csv(uploaded_file)
    if check_validity(df):
        df = df.dropna()
        df['PurchaseDate'] = pd.to_datetime(df['PurchaseDate'], errors='coerce')
        df['CleanedGender'] = df['Gender'].apply(lambda x: x if x in ['Male', 'Female'] else 'Other')
        df.reset_index(drop=True, inplace=True)
        return df

    else:
        st.subheader("Error: data does not match specified format, please ensure a valid upload")
        st.exit()

def data_summary(df, col_name):
    mean = df[col_name].mean()
    med = df[col_name].median()
    min = df[col_name].min()
    max = df[col_name].max()
    std = df[col_name].std()
    return mean, med, min, max, std


# visualizing data

def plot_purchase_hist(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    bin_size = math.ceil(math.log2(len(df)) + 1) 
    hist_plot = sns.histplot(df['PurchaseAmount'], bins=bin_size, kde=False, ax=ax)
    bin_edges = [patch.get_x() + patch.get_width() for patch in hist_plot.patches]
    ax.set_xticks(bin_edges)        
    ax.set_xlabel("Amount in $")
    ax.set_ylabel("Count")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xticks(rotation=45)
    st.pyplot(fig)

def plot_product_category_pie(df):
    fig, ax = plt.subplots(figsize=(3, 3))
    category_counts = df['ProductCategory'].value_counts()
    ax.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=140,textprops={'fontsize': 6})
    st.pyplot(fig)

def plot_gender_pie(df):
    fig, ax = plt.subplots(figsize=(3, 3))
    gender_counts = df['CleanedGender'].value_counts()
    ax.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=140,textprops={'fontsize': 6})
    st.pyplot(fig)

def plot_age_kde(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    bw = max(0.3, min(1.0, df['Age'].std() / df['Age'].mean()))
    sns.kdeplot(df['Age'], fill=True, ax=ax,bw_adjust=.5)
    ax.set_xlabel("Age")
    ax.set_ylabel("Density")
    plt.tight_layout()  
    st.pyplot(fig)

def plot_purchase_times(df):
    daily_totals = df.groupby(pd.Grouper(key='PurchaseDate', freq='W'))['PurchaseAmount'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=daily_totals, x='PurchaseDate', y='PurchaseAmount', ax=ax)
    ax.set_xlabel("Week")
    ax.set_ylabel("Total $")
    plt.xticks(rotation=45, ha='right', fontsize = '6')
    plt.tight_layout()
    st.pyplot(fig)



# streamlit ui

st.header("Customer Data Dashboard")
uploaded_file = st.file_uploader("Upload valid CSV file", type=["csv", "txt"])
if uploaded_file is not None:
    df = preprocess(uploaded_file)

    left, right = st.columns(2)
    #with left:
    st.write("Preview of Data", df.head())
    #with right:
    

 
    st.header("Customer Demographics")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Age Distribution")
        age_mean, age_med, age_min, age_max, age_std = data_summary(df, "Age")
        st.write(f"*The typical customer is {age_med:.0f} years old.*")
        plot_age_kde(df)
        st.write(f"*Mean: {age_mean:.0f}, Median: {age_med:.0f}, Min: {age_min}, Max: {age_max}, Standard Deviation: {age_std:.1f}*")
    with col2:
        st.subheader("Gender Distribution")
        plot_gender_pie(df)

    st.markdown("<br>", unsafe_allow_html=True)

    st.header("Historical Purchase Data")
    st.markdown("<br>", unsafe_allow_html=True)
 
    st.subheader("Purchases over Time")
    plot_purchase_times(df)
    st.markdown("<br>", unsafe_allow_html=True)


    left, right = st.columns(2)
    with left:
        st.subheader("Purchase By $ Spent")
        plot_purchase_hist(df)

    with right:
        st.subheader("Purchases by Category")
        plot_product_category_pie(df)
        
