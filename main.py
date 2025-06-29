import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List
import json

from bedrock_service import bedrock_service
from data_utils import (
    analyze_dataframe, 
    append_rows_to_dataframe, 
    create_download_link,
    detect_potential_biases,
    shuffle_dataframe_sample
)
from config import MAX_FILE_SIZE_MB, SAMPLE_ROWS_DISPLAY, DEFAULT_SUGGESTED_ROWS

# Page configuration
st.set_page_config(
    page_title="GenAI CSV Enhancer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚀 GenAI CSV Enhancer")
st.markdown("*Enhance your datasets with AI-generated rows using Amazon Bedrock*")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # AWS Configuration check
    if bedrock_service.bedrock_runtime is None:
        st.error("⚠️ AWS Bedrock not configured!")
        st.markdown("""
        **Setup Instructions:**
        1. Configure AWS credentials
        2. Ensure Bedrock access in your region
        3. Check the model permissions
        """)
    else:
        st.success("✅ AWS Bedrock Connected")
    
    # Settings
    st.subheader("Generation Settings")
    num_rows_to_generate = st.slider("Number of rows to generate", 1, 20, DEFAULT_SUGGESTED_ROWS)
    
    show_bias_analysis = st.checkbox("Show bias analysis", value=True)
    show_charts = st.checkbox("Show distribution charts", value=True)

# Initialize session state
if 'original_df' not in st.session_state:
    st.session_state.original_df = None
if 'generated_rows' not in st.session_state:
    st.session_state.generated_rows = []
if 'generation_explanation' not in st.session_state:
    st.session_state.generation_explanation = ""
if 'enhanced_df' not in st.session_state:
    st.session_state.enhanced_df = None

# 1. CSV Upload Section
st.header("📂 Upload CSV Dataset")
uploaded_file = st.file_uploader(
    "Choose your CSV file", 
    type=["csv"],
    help=f"Maximum file size: {MAX_FILE_SIZE_MB}MB"
)

if uploaded_file:
    try:
        # Load the CSV
        df = pd.read_csv(uploaded_file)
        st.session_state.original_df = df
        
        # 2. Schema & Sample Viewer
        st.header("🔍 Dataset Analysis")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📋 Schema Information")
            analysis = analyze_dataframe(df)
            
            st.metric("Total Rows", analysis['shape'][0])
            st.metric("Total Columns", analysis['shape'][1])
            
            # Column types
            st.write("**Column Types:**")
            for col, dtype in analysis['dtypes'].items():
                st.write(f"• `{col}`: {dtype}")
        
        with col2:
            st.subheader("📊 Sample Data")
            st.dataframe(df.head(SAMPLE_ROWS_DISPLAY), use_container_width=True)
            
            # Missing values info
            missing_data = analysis['missing_values']
            if any(missing_data.values()):
                st.write("**Missing Values:**")
                for col, missing_count in missing_data.items():
                    if missing_count > 0:
                        st.write(f"• `{col}`: {missing_count} missing")
        
        # Distribution charts
        if show_charts and len(df.columns) > 0:
            st.subheader("📈 Data Distributions")
            
            # Select columns for visualization
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
            
            if numeric_cols:
                chart_col = st.selectbox("Select column for distribution chart", 
                                       numeric_cols + categorical_cols[:3])  # Limit categorical
                
                if chart_col in numeric_cols:
                    fig = px.histogram(df, x=chart_col, title=f"Distribution of {chart_col}")
                    st.plotly_chart(fig, use_container_width=True)
                elif chart_col in categorical_cols:
                    value_counts = df[chart_col].value_counts().head(10)
                    fig = px.bar(x=value_counts.index, y=value_counts.values, 
                               title=f"Top values in {chart_col}")
                    fig.update_xaxis(title=chart_col)
                    fig.update_yaxis(title="Count")
                    st.plotly_chart(fig, use_container_width=True)
        
        # 3. LLM-based Row Generation
        st.header("🤖 AI-Powered Row Generation")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🎯 Generate New Rows", type="primary", use_container_width=True):
                with st.spinner("🔮 AI is analyzing your data and generating new rows..."):
                    generated_rows, explanation = bedrock_service.generate_csv_rows(
                        df, num_rows_to_generate
                    )
                    
                    st.session_state.generated_rows = generated_rows
                    st.session_state.generation_explanation = explanation
        
        with col2:
            if st.button("🔄 Regenerate with New Sample", use_container_width=True):
                if len(df) > SAMPLE_ROWS_DISPLAY:
                    # Use a different sample
                    shuffled_df = shuffle_dataframe_sample(df, SAMPLE_ROWS_DISPLAY * 2)
                    with st.spinner("🔮 Generating with new data sample..."):
                        generated_rows, explanation = bedrock_service.generate_csv_rows(
                            shuffled_df, num_rows_to_generate
                        )
                        
                        st.session_state.generated_rows = generated_rows
                        st.session_state.generation_explanation = explanation
                else:
                    st.warning("Dataset too small for regeneration with new sample")
        
        with col3:
            if st.button("🗑️ Clear Generated Rows", use_container_width=True):
                st.session_state.generated_rows = []
                st.session_state.generation_explanation = ""
                st.session_state.enhanced_df = None
        
        # 4. Display Generated Rows
        if st.session_state.generated_rows:
            st.header("✨ Generated Rows")
            
            # Show explanation
            if st.session_state.generation_explanation:
                st.info(f"**AI Reasoning:** {st.session_state.generation_explanation}")
            
            # Display generated rows in an editable format
            generated_df = pd.DataFrame(st.session_state.generated_rows)
            
            st.subheader("📝 Review & Edit Generated Data")
            edited_df = st.data_editor(
                generated_df,
                use_container_width=True,
                num_rows="dynamic",
                key="generated_rows_editor"
            )
            
            # Update session state with edited data
            st.session_state.generated_rows = edited_df.to_dict('records')
            
            # Bias analysis
            if show_bias_analysis:
                biases = detect_potential_biases(df, edited_df)
                if biases:
                    st.warning("⚠️ **Potential Bias Considerations:**")
                    for bias in biases:
                        st.write(f"• {bias}")
                else:
                    st.success("✅ No obvious biases detected")
            
            # 5. Append & Download
            st.header("💾 Export Enhanced Dataset")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("🔗 Preview Enhanced Dataset", type="secondary", use_container_width=True):
                    enhanced_df = append_rows_to_dataframe(df, st.session_state.generated_rows)
                    st.session_state.enhanced_df = enhanced_df
                    
                    st.success(f"✅ Enhanced dataset ready! Original: {len(df)} rows → Enhanced: {len(enhanced_df)} rows")
            
            with col2:
                if st.session_state.enhanced_df is not None:
                    csv_data, filename = create_download_link(st.session_state.enhanced_df)
                    
                    st.download_button(
                        label="⬇️ Download Enhanced CSV",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv",
                        type="primary",
                        use_container_width=True
                    )
            
            # Show enhanced dataset preview
            if st.session_state.enhanced_df is not None:
                st.subheader("👀 Enhanced Dataset Preview")
                
                # Highlight new rows
                total_rows = len(st.session_state.enhanced_df)
                original_rows = len(df)
                new_rows = total_rows - original_rows
                
                st.info(f"📊 Showing last {min(10, total_rows)} rows (including {new_rows} new AI-generated rows)")
                st.dataframe(
                    st.session_state.enhanced_df.tail(10),
                    use_container_width=True
                )
                
                # Comparison charts
                if show_charts and len(df.columns) > 0:
                    st.subheader("📊 Before vs After Comparison")
                    
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    if numeric_cols:
                        comparison_col = st.selectbox(
                            "Select column for before/after comparison",
                            numeric_cols,
                            key="comparison_column"
                        )
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            fig1 = px.histogram(df, x=comparison_col, title=f"Original: {comparison_col}")
                            st.plotly_chart(fig1, use_container_width=True)
                        
                        with col2:
                            fig2 = px.histogram(st.session_state.enhanced_df, x=comparison_col, 
                                             title=f"Enhanced: {comparison_col}")
                            st.plotly_chart(fig2, use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ Error loading CSV: {str(e)}")
        st.info("Please ensure your CSV file is properly formatted with headers.")

else:
    st.info("👆 Please upload a CSV file to get started.")
    
    # Show example of what the app can do
    st.markdown("""
    ## 🎯 What this app does:
    
    1. **📂 Upload CSV**: Upload your dataset with headers
    2. **🔍 Analyze**: View schema, sample data, and distributions  
    3. **🤖 Generate**: AI creates new realistic rows based on your data patterns
    4. **✏️ Edit**: Review and modify generated rows before export
    5. **💾 Export**: Download your enhanced dataset
    
    ### 🔧 Features:
    - **AWS Bedrock Integration**: Uses Claude 3 Sonnet for intelligent row generation
    - **Bias Detection**: Flags potential biases in generated data
    - **Interactive Editing**: Modify generated rows before export
    - **Visual Analytics**: Compare before/after distributions
    - **Flexible Generation**: Regenerate with different samples
    """)

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit, AWS Bedrock, and ❤️*")