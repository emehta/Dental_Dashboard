import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Revenue Performance", page_icon="💰", layout="wide")

st.title("Revenue Performance Analysis")

# Load data
@st.cache_data
def load_data():
    try:
        return pd.read_csv('data/Pat_App_Data.csv')
    except Exception as e:
        st.error(f"Failed to load data from Pat_App_Data.csv: {e}")
        return None

df = load_data()

if df is not None:
    # Convert date column to datetime
    df['Date_of_Service'] = pd.to_datetime(df['Date_of_Service'], errors='coerce')
    
    # Convert treatment plan dates to datetime
    date_columns = ['Treatment_Plan_Creation_Date', 'Treatment_Plan_Completion_Date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Extract month and year
    df['Month_Year'] = df['Date_of_Service'].dt.strftime('%Y-%m')
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter
    min_date = df['Date_of_Service'].min().date()
    max_date = df['Date_of_Service'].max().date()
    
    start_date = st.sidebar.date_input("Start Date", min_date)
    end_date = st.sidebar.date_input("End Date", max_date)
    
    # Location filter
    locations = ['All'] + sorted(df['Location_Name'].unique().tolist())
    selected_location = st.sidebar.selectbox("Select Location", locations)
    
    # Provider filter
    providers = ['All'] + sorted(df['Provider_ID'].unique().tolist())
    selected_provider = st.sidebar.selectbox("Select Provider", providers)
    
    # Insurance filter
    insurance_options = ['All'] + sorted(df['Insurance_Provider'].unique().tolist())
    selected_insurance = st.sidebar.selectbox("Select Insurance", insurance_options)
    
    
    # Apply filters
    filtered_df = df.copy()
    
    # Date filter
    filtered_df = filtered_df[(filtered_df['Date_of_Service'].dt.date >= start_date) & 
                             (filtered_df['Date_of_Service'].dt.date <= end_date)]
    
    # Location filter
    if selected_location != 'All':
        filtered_df = filtered_df[filtered_df['Location_Name'] == selected_location]
    
    # Provider filter
    if selected_provider != 'All':
        filtered_df = filtered_df[filtered_df['Provider_ID'] == selected_provider]
    
    # Insurance filter
    if selected_insurance != 'All':
        filtered_df = filtered_df[filtered_df['Insurance_Provider'] == selected_insurance]
    
    # Group data by Month and Procedure Type
    revenue_by_month_procedure = filtered_df.groupby(['Month_Year', 'Procedure_Description'])['Charged_Amount'].sum().reset_index()
    
    # Prepare data for profitability analysis
    filtered_df['Collected_Amount'] = filtered_df['Insurance_Covered_Amount'] + filtered_df['Out_of_Pocket'] - filtered_df['Discount_Applied']
    filtered_df['Collection_Rate'] = (filtered_df['Collected_Amount'] / filtered_df['Charged_Amount']).fillna(0) * 100
    
    # Calculate profitability by procedure
    profitability = filtered_df.groupby('Procedure_Description').agg({
        'Charged_Amount': 'sum',
        'Collected_Amount': 'sum'
    }).reset_index()
    
    profitability['Collection_Rate'] = (profitability['Collected_Amount'] / profitability['Charged_Amount']).fillna(0) * 100
    profitability = profitability.sort_values('Collected_Amount', ascending=False)
    
    # Calculate monthly totals for trend line
    monthly_revenue = filtered_df.groupby('Month_Year').agg({
        'Charged_Amount': 'sum',
        'Collected_Amount': 'sum'
    }).reset_index()
    
    # Sort by month-year
    monthly_revenue['Month_Year_dt'] = pd.to_datetime(monthly_revenue['Month_Year'] + '-01')
    monthly_revenue = monthly_revenue.sort_values('Month_Year_dt')
    
    # Calculate month-over-month growth
    if len(monthly_revenue) > 1:
        monthly_revenue['MoM_Growth'] = monthly_revenue['Collected_Amount'].pct_change() * 100
    else:
        monthly_revenue['MoM_Growth'] = 0
    
    # Key metrics
    total_revenue = filtered_df['Charged_Amount'].sum()
    total_collected = filtered_df['Collected_Amount'].sum()
    overall_collection_rate = (total_collected / total_revenue * 100) if total_revenue > 0 else 0
    
    # Get top procedures by revenue
    top_procedures = filtered_df.groupby('Procedure_Description')['Charged_Amount'].sum().sort_values(ascending=False).head(3)
    
    # Get latest month's growth rate
    latest_mom_growth = monthly_revenue['MoM_Growth'].iloc[-1] if len(monthly_revenue) > 1 else 0
    
    # Display metrics in three columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Billed Revenue", f"${total_revenue:,.2f}")
        
    with col2:
        st.metric("Total Collected Revenue", f"${total_collected:,.2f}")
        
    with col3:
        st.metric("Overall Collection Rate", f"{overall_collection_rate:.1f}%", 
                 delta=f"{latest_mom_growth:.1f}%" if not pd.isna(latest_mom_growth) else None)
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Revenue Breakdown", 
        "Profitability Analysis",
        "Location Performance",
        "Insurance Analysis",
        "Treatment Plan Analysis"
    ])
    
    with tab1:
        st.subheader("Monthly Revenue by Procedure Type")
        
        if not revenue_by_month_procedure.empty:
            fig = px.bar(
                revenue_by_month_procedure, 
                x='Month_Year', 
                y='Charged_Amount',
                color='Procedure_Description',
                title="Monthly Revenue Breakdown by Procedure",
                labels={'Month_Year': 'Month', 'Charged_Amount': 'Revenue ($)', 'Procedure_Description': 'Procedure'},
            )
            
            # Add forecast if we have enough data
            if len(monthly_revenue) > 3:
                # Simple forecast - last 3 months average for next 3 months
                last_months = monthly_revenue.tail(3)
                avg_revenue = last_months['Collected_Amount'].mean()
                
                last_date = monthly_revenue['Month_Year_dt'].max()
                forecast_dates = [last_date + timedelta(days=30*i) for i in range(1, 4)]
                forecast_months = [d.strftime('%Y-%m') for d in forecast_dates]
                
                # Add to the plot as a line
                for i, month in enumerate(forecast_months):
                    fig.add_trace(
                        go.Scatter(
                            x=[month], 
                            y=[avg_revenue],
                            mode='markers+lines',
                            line=dict(dash='dot', color='red'),
                            name='Forecast',
                            showlegend=i==0
                        )
                    )
            
            # Improve layout
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Revenue ($)",
                legend_title="Procedure Type",
                barmode='stack'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
                
        else:
            st.warning("No data available for the selected filters")
    
    with tab2:
        st.subheader("Procedure Profitability Analysis")
        
        # Create profitability chart
        if not profitability.empty:
            fig = px.bar(
                profitability.head(10),
                x='Procedure_Description',
                y=['Charged_Amount', 'Collected_Amount'],
                barmode='group',
                title="Billed vs. Collected Revenue by Procedure",
                labels={
                    'Procedure_Description': 'Procedure',
                    'value': 'Amount ($)',
                    'variable': 'Revenue Type'
                }
            )
            
            # Add collection rate as a line
            fig.add_trace(
                go.Scatter(
                    x=profitability.head(10)['Procedure_Description'],
                    y=profitability.head(10)['Collection_Rate'],
                    mode='lines+markers',
                    name='Collection Rate (%)',
                    yaxis='y2'
                )
            )
            
            # Set up secondary y-axis
            fig.update_layout(
                yaxis2=dict(
                    title='Collection Rate (%)',
                    overlaying='y',
                    side='right',
                    range=[0, 100]
                ),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show procedures with highest and lowest collection rates
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Top 5 Procedures by Collection Rate")
                top_collection = profitability[profitability['Charged_Amount'] > 100].sort_values('Collection_Rate', ascending=False).head(5)
                
                for _, row in top_collection.iterrows():
                    st.write(f"- {row['Procedure_Description']}: {row['Collection_Rate']:.1f}% (${row['Collected_Amount']:,.2f})")
            
            with col2:
                st.subheader("Bottom 5 Procedures by Collection Rate")
                bottom_collection = profitability[profitability['Charged_Amount'] > 100].sort_values('Collection_Rate').head(5)
                
                for _, row in bottom_collection.iterrows():
                    st.write(f"- {row['Procedure_Description']}: {row['Collection_Rate']:.1f}% (${row['Collected_Amount']:,.2f})")
        
        else:
            st.warning("No data available for the selected filters")
    
    # Location-Based Performance Analysis
    with tab3:
        st.subheader("Location-Based Performance Analysis")
        
        if 'Location_Name' in filtered_df.columns and 'Google_Rating' in filtered_df.columns:
            # Group by location to get key metrics
            location_performance = filtered_df.groupby('Location_Name').agg({
                'Charged_Amount': 'sum',
                'Collected_Amount': 'sum',
                'Google_Rating': 'first',
                'Visit_ID': 'nunique'
            }).reset_index()
            
            # Calculate metrics
            location_performance['Collection_Rate'] = (location_performance['Collected_Amount'] / location_performance['Charged_Amount']).fillna(0) * 100
            location_performance['Revenue_Per_Visit'] = (location_performance['Collected_Amount'] / location_performance['Visit_ID']).fillna(0)
            
            # Create scatter plot of Google Rating vs Revenue
            fig1 = px.scatter(
                location_performance,
                x='Google_Rating',
                y='Revenue_Per_Visit',
                size='Collected_Amount',
                color='Collection_Rate',
                hover_name='Location_Name',
                title="Revenue Performance vs. Google Rating",
                labels={
                    'Google_Rating': 'Google Rating',
                    'Revenue_Per_Visit': 'Avg. Revenue Per Visit ($)',
                    'Collected_Amount': 'Total Collected Revenue ($)',
                    'Collection_Rate': 'Collection Rate (%)'
                }
            )
            
            st.plotly_chart(fig1, use_container_width=True)
            
            # Location performance table
            st.subheader("Location Performance Metrics")
            
            # Format for display
            display_df = location_performance.copy()
            display_df['Collection_Rate'] = display_df['Collection_Rate'].apply(lambda x: f"{x:.1f}%")
            display_df['Charged_Amount'] = display_df['Charged_Amount'].apply(lambda x: f"${x:,.2f}")
            display_df['Collected_Amount'] = display_df['Collected_Amount'].apply(lambda x: f"${x:,.2f}")
            display_df['Revenue_Per_Visit'] = display_df['Revenue_Per_Visit'].apply(lambda x: f"${x:,.2f}")
            
            # Rename columns for better readability
            display_df = display_df.rename(columns={
                'Location_Name': 'Location',
                'Charged_Amount': 'Billed Revenue',
                'Collected_Amount': 'Collected Revenue',
                'Visit_ID': 'Number of Visits',
                'Google_Rating': 'Google Rating',
                'Revenue_Per_Visit': 'Avg. Revenue/Visit',
                'Collection_Rate': 'Collection Rate'
            })
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("Location data not available in the dataset")
    
    # Insurance Analysis
    with tab4:
        st.subheader("Procedure Profitability by Insurance Provider")
        
        if 'Insurance_Provider' in filtered_df.columns and 'Procedure_Description' in filtered_df.columns:
            # Group data by insurance provider and procedure
            insurance_procedure = filtered_df.groupby(['Insurance_Provider', 'Procedure_Description']).agg({
                'Charged_Amount': 'sum',
                'Insurance_Covered_Amount': 'sum',
                'Collected_Amount': 'sum',
                'Visit_ID': 'nunique'
            }).reset_index()
            
            # Calculate reimbursement rate
            insurance_procedure['Reimbursement_Rate'] = (insurance_procedure['Insurance_Covered_Amount'] / 
                                                        insurance_procedure['Charged_Amount']).fillna(0) * 100
            
            # Calculate total collection rate (including patient portion)
            insurance_procedure['Collection_Rate'] = (insurance_procedure['Collected_Amount'] / 
                                                    insurance_procedure['Charged_Amount']).fillna(0) * 100
            
            # Get list of top 10 procedures by volume
            top_procedures = filtered_df['Procedure_Description'].value_counts().head(10).index.tolist()
            
            # Let user select a procedure to analyze
            selected_procedure = st.selectbox(
                "Select Procedure to Analyze",
                options=top_procedures,
                index=0
            )
            
            # Filter data for selected procedure
            procedure_data = insurance_procedure[insurance_procedure['Procedure_Description'] == selected_procedure]
            
            if not procedure_data.empty:
                # Sort by reimbursement rate
                procedure_data = procedure_data.sort_values('Reimbursement_Rate', ascending=False)
                
                # Create horizontal bar chart comparing insurance providers
                fig = px.bar(
                    procedure_data,
                    y='Insurance_Provider',
                    x='Reimbursement_Rate',
                    title=f"Insurance Reimbursement Rates for {selected_procedure}",
                    labels={
                        'Insurance_Provider': 'Insurance Provider',
                        'Reimbursement_Rate': 'Reimbursement Rate (%)'
                    },
                    orientation='h',
                    color='Reimbursement_Rate',
                    color_continuous_scale=px.colors.sequential.Viridis
                )
                
                fig.update_layout(xaxis_range=[0, 100])
                st.plotly_chart(fig, use_container_width=True)
                
                # Create a comparison table
                st.subheader("Detailed Insurance Comparison")
                
                # Format for display
                display_df = procedure_data.copy()
                display_df['Reimbursement_Rate'] = display_df['Reimbursement_Rate'].apply(lambda x: f"{x:.1f}%")
                display_df['Collection_Rate'] = display_df['Collection_Rate'].apply(lambda x: f"{x:.1f}%")
                display_df['Charged_Amount'] = display_df['Charged_Amount'].apply(lambda x: f"${x:,.2f}")
                display_df['Insurance_Covered_Amount'] = display_df['Insurance_Covered_Amount'].apply(lambda x: f"${x:,.2f}")
                display_df['Collected_Amount'] = display_df['Collected_Amount'].apply(lambda x: f"${x:,.2f}")
                
                # Rename columns for better readability
                display_df = display_df.rename(columns={
                    'Insurance_Provider': 'Insurance Provider',
                    'Charged_Amount': 'Billed Amount',
                    'Insurance_Covered_Amount': 'Insurance Covered',
                    'Collected_Amount': 'Total Collected',
                    'Visit_ID': 'Number of Procedures',
                    'Reimbursement_Rate': 'Insurance Reimbursement %',
                    'Collection_Rate': 'Total Collection %'
                })
                
                st.dataframe(display_df, use_container_width=True)
                
                # Get the best and worst insurance providers for this procedure
                if len(procedure_data) > 1:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Best Reimbursement")
                        best_provider = procedure_data.iloc[0]
                        st.write(f"**{best_provider['Insurance_Provider']}**")
                        st.write(f"Reimbursement Rate: {best_provider['Reimbursement_Rate']:.1f}%")
                        st.write(f"Average Insurance Payment: ${best_provider['Insurance_Covered_Amount']/best_provider['Visit_ID']:,.2f}")
                    
                    with col2:
                        st.subheader("Lowest Reimbursement")
                        worst_provider = procedure_data.iloc[-1]
                        st.write(f"**{worst_provider['Insurance_Provider']}**")
                        st.write(f"Reimbursement Rate: {worst_provider['Reimbursement_Rate']:.1f}%")
                        st.write(f"Average Insurance Payment: ${worst_provider['Insurance_Covered_Amount']/worst_provider['Visit_ID']:,.2f}")
            else:
                st.info(f"No data available for {selected_procedure}")
            
            # Compare top procedures across insurance providers
            st.subheader("Top Procedures by Insurance Provider")
            
            # Get all insurance providers
            insurance_providers = filtered_df['Insurance_Provider'].unique()
            
            # Let user select an insurance provider to analyze
            selected_insurance_provider = st.selectbox(
                "Select Insurance Provider",
                options=insurance_providers,
                index=0
            )
            
            # Filter data for selected insurance provider
            provider_data = insurance_procedure[insurance_procedure['Insurance_Provider'] == selected_insurance_provider]
            
            if not provider_data.empty:
                # Sort by reimbursement rate and get top 10
                provider_data = provider_data.sort_values('Reimbursement_Rate', ascending=False).head(10)
                
                # Create horizontal bar chart
                fig = px.bar(
                    provider_data,
                    y='Procedure_Description',
                    x='Reimbursement_Rate',
                    title=f"Best Reimbursed Procedures for {selected_insurance_provider}",
                    labels={
                        'Procedure_Description': 'Procedure',
                        'Reimbursement_Rate': 'Reimbursement Rate (%)'
                    },
                    orientation='h',
                    color='Reimbursement_Rate',
                    color_continuous_scale=px.colors.sequential.Viridis
                )
                
                fig.update_layout(xaxis_range=[0, 100])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No data available for {selected_insurance_provider}")
        else:
            st.warning("Insurance provider data not available in the dataset")
    
    # Treatment Plan Analysis
    with tab5:
        st.subheader("Treatment Plan Completion Analysis")
        
        if ('Treatment_Plan_ID' in filtered_df.columns and 
            'Treatment_Plan_Completion_Rate' in filtered_df.columns and 
            'Estimated_Total_Cost' in filtered_df.columns):
            
            # Filter out rows without treatment plan data
            treatment_df = filtered_df[filtered_df['Treatment_Plan_ID'].notna()]
            
            if not treatment_df.empty:
                # Calculate metrics
                treatment_df['Forecasting_Accuracy'] = (treatment_df['Collected_Amount'] / 
                                                     treatment_df['Estimated_Total_Cost']).fillna(0) * 100
                
                # Calculate treatment plan duration where completion date exists
                treatment_df['Plan_Duration_Days'] = None
                mask = (treatment_df['Treatment_Plan_Creation_Date'].notna() & 
                       treatment_df['Treatment_Plan_Completion_Date'].notna())
                
                if any(mask):
                    treatment_df.loc[mask, 'Plan_Duration_Days'] = (
                        treatment_df.loc[mask, 'Treatment_Plan_Completion_Date'] - 
                        treatment_df.loc[mask, 'Treatment_Plan_Creation_Date']
                    ).dt.days
                
                # Create scatter plot of completion rate vs revenue
                st.subheader("Treatment Plan Completion vs. Revenue")
                
                fig1 = px.scatter(
                    treatment_df,
                    x='Treatment_Plan_Completion_Rate',
                    y='Collected_Amount',
                    size='Estimated_Total_Cost',
                    hover_name='Treatment_Plan_ID',
                    title="Revenue vs. Treatment Plan Completion Rate",
                    labels={
                        'Treatment_Plan_Completion_Rate': 'Plan Completion Rate (%)',
                        'Collected_Amount': 'Collected Revenue ($)',
                        'Estimated_Total_Cost': 'Estimated Cost ($)'
                    }
                )
                
                st.plotly_chart(fig1, use_container_width=True)
                
                # Forecasting accuracy analysis
                st.subheader("Treatment Plan Forecasting Accuracy")
                
                # Group by treatment plan ID
                forecasting_df = treatment_df.groupby('Treatment_Plan_ID').agg({
                    'Estimated_Total_Cost': 'first',
                    'Collected_Amount': 'sum',
                    'Treatment_Plan_Completion_Rate': 'first'
                }).reset_index()
                
                # Calculate forecasting accuracy
                forecasting_df['Forecasting_Accuracy'] = (forecasting_df['Collected_Amount'] / 
                                                       forecasting_df['Estimated_Total_Cost']).fillna(0) * 100
                
                # Create bar chart comparing estimated vs actual revenue
                fig2 = px.bar(
                    forecasting_df.head(10),
                    x='Treatment_Plan_ID',
                    y=['Estimated_Total_Cost', 'Collected_Amount'],
                    barmode='group',
                    title="Estimated vs. Actual Revenue",
                    labels={
                        'Treatment_Plan_ID': 'Treatment Plan',
                        'value': 'Amount ($)',
                        'variable': 'Revenue Type'
                    }
                )
                
                # Add completion rate as a line
                fig2.add_trace(
                    go.Scatter(
                        x=forecasting_df.head(10)['Treatment_Plan_ID'],
                        y=forecasting_df.head(10)['Treatment_Plan_Completion_Rate'],
                        mode='lines+markers',
                        name='Completion Rate (%)',
                        yaxis='y2'
                    )
                )
                
                # Set up secondary y-axis
                fig2.update_layout(
                    yaxis2=dict(
                        title='Completion Rate (%)',
                        overlaying='y',
                        side='right',
                        range=[0, 100]
                    ),
                    legend=dict(
                        orientation='h',
                        yanchor='bottom',
                        y=1.02,
                        xanchor='right',
                        x=1
                    )
                )
                
                st.plotly_chart(fig2, use_container_width=True)
                
                # Treatment plan duration analysis
                st.subheader("Treatment Plan Duration Analysis")
                
                # Filter for completed plans with duration data
                completed_plans = treatment_df[treatment_df['Plan_Duration_Days'].notna()]
                
                if not completed_plans.empty:
                    # Create histogram of plan durations
                    fig3 = px.histogram(
                        completed_plans,
                        x='Plan_Duration_Days',
                        title="Distribution of Treatment Plan Durations",
                        labels={'Plan_Duration_Days': 'Duration (Days)'},
                        marginal='box'
                    )
                    
                    st.plotly_chart(fig3, use_container_width=True)
                    
                    # Create a scatter plot of duration vs completion rate
                    fig4 = px.scatter(
                        completed_plans,
                        x='Plan_Duration_Days',
                        y='Treatment_Plan_Completion_Rate',
                        color='Collected_Amount',
                        size='Estimated_Total_Cost',
                        hover_name='Treatment_Plan_ID',
                        title="Plan Duration vs. Completion Rate",
                        labels={
                            'Plan_Duration_Days': 'Duration (Days)',
                            'Treatment_Plan_Completion_Rate': 'Completion Rate (%)',
                            'Collected_Amount': 'Collected Amount ($)',
                            'Estimated_Total_Cost': 'Estimated Cost ($)'
                        }
                    )
                    
                    st.plotly_chart(fig4, use_container_width=True)
                else:
                    st.info("No completed treatment plan data available")
                
                # Summary statistics in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_completion = treatment_df['Treatment_Plan_Completion_Rate'].mean()
                    st.metric("Average Completion Rate", f"{avg_completion:.1f}%")
                
                with col2:
                    avg_forecasting = treatment_df['Forecasting_Accuracy'].mean()
                    st.metric("Average Forecasting Accuracy", f"{avg_forecasting:.1f}%")
                
                with col3:
                    if not completed_plans.empty:
                        avg_duration = completed_plans['Plan_Duration_Days'].mean()
                        st.metric("Average Treatment Duration", f"{avg_duration:.1f} days")
                    else:
                        st.metric("Average Treatment Duration", "N/A")
                
                # Completion rate segments
                st.subheader("Treatment Plan Completion Rate Segments")
                
                # Create segments
                treatment_df['Completion_Segment'] = pd.cut(
                    treatment_df['Treatment_Plan_Completion_Rate'],
                    bins=[0, 25, 50, 75, 100],
                    labels=['0-25%', '26-50%', '51-75%', '76-100%']
                )
                
                # Group by segment
                segment_data = treatment_df.groupby('Completion_Segment').agg({
                    'Treatment_Plan_ID': 'count',
                    'Estimated_Total_Cost': 'sum',
                    'Collected_Amount': 'sum'
                }).reset_index()
                
                # Calculate metrics
                segment_data['Collection_Rate'] = (segment_data['Collected_Amount'] / 
                                                 segment_data['Estimated_Total_Cost']).fillna(0) * 100
                
                # Create stacked bar chart
                fig5 = px.bar(
                    segment_data,
                    x='Completion_Segment',
                    y=['Estimated_Total_Cost', 'Collected_Amount'],
                    barmode='group',
                    title="Revenue by Treatment Plan Completion Segment",
                    labels={
                        'Completion_Segment': 'Completion Rate Segment',
                        'value': 'Amount ($)',
                        'variable': 'Revenue Type'
                    }
                )
                
                st.plotly_chart(fig5, use_container_width=True)
            else:
                st.info("No treatment plan data available in the selected date range")
        else:
            st.warning("Treatment plan data not available in the dataset")
    
    # Show filtered data
    with st.expander("View Filtered Data"):
        st.dataframe(filtered_df)

else:
    st.error("No data available. Please check your data files.")