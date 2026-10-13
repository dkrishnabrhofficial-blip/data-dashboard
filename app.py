import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from pypdf import PdfReader
import io

# Page Configuration
st.set_page_config(
    page_title="DataInsight Pro | Multi-Format Analytics Engine",
    page_icon="📊",
    layout="wide"
)

st.title("📊 DataInsight Pro: Multi-Format Data Analytics Dashboard")
st.markdown("An advanced exploratory data analysis tool supporting CSV, Excel, and PDF document parsing for comprehensive insights.")

# Sidebar Controls
st.sidebar.header("📁 Data Source & Ingestion")

input_type = st.sidebar.radio(
    "Select Input Format",
    ["Use Sample Dataset", "Upload CSV / Excel File", "Upload PDF Document / Report"]
)

@st.cache_data
def load_sample_data():
    np.random.seed(42)
    dates = pd.date_range(start="2026-01-01", periods=200)
    regions = ["North", "South", "East", "West", "Central"]
    categories = ["Electronics", "Software", "Hardware", "Cloud Services"]
    
    data = {
        "Date": np.random.choice(dates, 200),
        "Region": np.random.choice(regions, 200),
        "Category": np.random.choice(categories, 200),
        "Units_Sold": np.random.randint(10, 150, 200),
        "Unit_Price": np.random.uniform(50.0, 1200.0, 200),
        "Customer_Rating": np.random.uniform(3.0, 5.0, 200)
    }
    df = pd.DataFrame(data)
    df["Total_Revenue"] = df["Units_Sold"] * df["Unit_Price"]
    return df

df = None
pdf_text_content = ""

if input_type == "Use Sample Dataset":
    df = load_sample_data()

elif input_type == "Upload CSV / Excel File":
    uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.sidebar.success("File uploaded successfully!")
        except Exception as e:
            st.sidebar.error(f"Error reading file: {e}")
    else:
        st.info("👈 Please upload a CSV or Excel file from the sidebar.")
        df = load_sample_data()

elif input_type == "Upload PDF Document / Report":
    pdf_file = st.sidebar.file_uploader("Upload PDF Report", type=["pdf"])
    if pdf_file is not None:
        try:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pdf_text_content += text + "\n"
            st.sidebar.success(f"PDF Processed ({len(reader.pages)} Pages Extracted)")
        except Exception as e:
            st.sidebar.error(f"Error reading PDF: {e}")

# --- DISPLAY LOGIC BASED ON INPUT ---
if input_type == "Upload PDF Document / Report":
    st.markdown("---")
    st.subheader("📄 Extracted PDF Document Analysis")
    if pdf_text_content:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("#### Document Text Preview")
            st.text_area("Extracted Content", value=pdf_text_content[:4000], height=300)
        with col2:
            st.markdown("#### PDF Quick Stats")
            st.metric("Total Characters", f"{len(pdf_text_content):,}")
            st.metric("Estimated Words", f"{len(pdf_text_content.split()):,}")
            st.info("Tip: You can upload study notes, research papers, or financial PDF reports here!")
    else:
        st.info("👈 Upload a PDF file from the sidebar to view its extracted content and text metrics.")

elif df is not None:
    # --- DATA HEALTH METRICS ---
    st.markdown("---")
    st.subheader("🔍 Dataset Health & Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rows", f"{df.shape[0]:,}")
    with col2:
        st.metric("Total Columns", f"{df.shape[1]}")
    with col3:
        missing_count = int(df.isnull().sum().sum())
        st.metric("Missing Values", f"{missing_count}")
    with col4:
        duplicates = int(df.duplicated().sum())
        st.metric("Duplicate Rows", f"{duplicates}")

    # --- SIDEBAR FILTERS ---
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Data Slicing & Filtering")
    
    filtered_df = df.copy()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    
    if categorical_cols:
        selected_cat_col = st.sidebar.selectbox("Filter by Category Column", ["None"] + categorical_cols)
        if selected_cat_col != "None":
            unique_vals = df[selected_cat_col].unique().tolist()
            selected_vals = st.sidebar.multiselect(f"Select {selected_cat_col}", unique_vals, default=unique_vals)
            if selected_vals:
                filtered_df = filtered_df[filtered_df[selected_cat_col].isin(selected_vals)]

    # --- MAIN TABS LAYOUT ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Raw Data Preview", 
        "📈 Statistical Summary", 
        "📊 Interactive Visualizations", 
        "📥 Export Filtered Data"
    ])

    with tab1:
        st.subheader("Filtered Dataset Preview")
        st.dataframe(filtered_df, use_container_width=True)

    with tab2:
        st.subheader("Statistical Breakdown")
        st.dataframe(filtered_df.describe(), use_container_width=True)
        
        st.markdown("Column Data Types & Non-Null Counts:")
        buffer = []
        for col in filtered_df.columns:
            buffer.append({
                "Column Name": col,
                "Data Type": str(filtered_df[col].dtype),
                "Non-Null Count": int(filtered_df[col].notnull().sum()),
                "Unique Values": int(filtered_df[col].nunique())
            })
        st.dataframe(pd.DataFrame(buffer), use_container_width=True)

    with tab3:
        st.subheader("Advanced Visual Analytics")
        numeric_cols = filtered_df.select_dtypes(include=["number"]).columns.tolist()
        
        if len(numeric_cols) >= 2:
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown("#### Scatter Plot Analysis")
                x_axis = st.selectbox("X-Axis", numeric_cols, index=0)
                y_axis = st.selectbox("Y-Axis", numeric_cols, index=1 if len(numeric_cols) > 1 else 0)
                color_col = categorical_cols[0] if categorical_cols else None
                
                fig_scatter = px.scatter(
                    filtered_df, x=x_axis, y=y_axis, color=color_col,
                    template="plotly_dark", title=f"{y_axis} vs {x_axis}"
                )
                st.plotly_chart(fig_scatter, use_container_width=True)

            with c2:
                st.markdown("#### Distribution / Histogram")
                hist_col = st.selectbox("Select Numeric Column for Distribution", numeric_cols, index=0)
                fig_hist = px.histogram(
                    filtered_df, x=hist_col, marginal="box",
                    template="plotly_dark", title=f"Distribution of {hist_col}"
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
            st.markdown("#### Correlation Matrix Heatmap")
            corr = filtered_df[numeric_cols].corr()
            fig_corr = px.imshow(
                corr, text_auto=True, aspect="auto",
                color_continuous_scale="RdBu_r", template="plotly_dark",
                title="Numerical Feature Correlation Matrix"
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.warning("Dataset requires at least 2 numerical columns to render visual charts.")

    with tab4:
        st.subheader("Export Cleaned / Filtered Data")
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered CSV Report",
            data=csv_data,
            file_name="filtered_data_report.csv",
            mime="text/csv",
            type="primary"
        )
