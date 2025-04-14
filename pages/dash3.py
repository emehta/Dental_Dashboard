import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import calendar
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt

st.set_page_config(page_title="CFO Financial Dashboard", page_icon="💲", layout="wide")

st.title("CFO Financial Analytics Dashboard")

# Load data
@st.cache_data
def load_data():
    try:
        financial_data = pd.read_csv('./data/Financial_Data.csv')
        operations_data = pd.read_csv('data/Operations_Data.csv')
        patient_data = pd.read_csv('data/Pat_App_Data.csv')
        staff_data = pd.read_csv('data/Staff_Hours_Data.csv')
        equipment_data = pd.read_csv('data/Equipment_Usage_Data.csv')
        
        # Convert date column in financial data
        if 'Date' in financial_data.columns:
            financial_data['Date'] = pd.to_datetime(financial_data['Date'], errors='coerce')

        # Convert date column in operations data
        if 'Date' in operations_data.columns:
            operations_data['Date'] = pd.to_datetime(operations_data['Date'], errors='coerce')

        # Convert date columns in patient data
        patient_date_cols = ['Date_of_Service', 'Treatment_Plan_Creation_Date', 'Treatment_Plan_Completion_Date', 
                           'Insurance_Claim_Submission_Date', 'Insurance_Claim_Payment_Date']
        for col in patient_date_cols:
            if col in patient_data.columns:
                patient_data[col] = pd.to_datetime(patient_data[col], errors='coerce')

        # Convert date column in staff data
        if 'Date' in staff_data.columns:
            staff_data['Date'] = pd.to_datetime(staff_data['Date'], errors='coerce')

        # Convert date column in equipment data
        if 'Date' in equipment_data.columns:
            equipment_data['Date'] = pd.to_datetime(equipment_data['Date'], errors='coerce')
        
        # Add month-year for grouping
        for df in [financial_data, operations_data, patient_data, staff_data, equipment_data]:
            date_col = 'Date' if 'Date' in df.columns else 'Date_of_Service' if 'Date_of_Service' in df.columns else None
            if date_col:
                df['Month_Year'] = df[date_col].dt.strftime('%Y-%m')
        
        return financial_data, operations_data, patient_data, staff_data, equipment_data
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None, None

financial_data, operations_data, patient_data, staff_data, equipment_data = load_data()

if all([financial_data is not None, operations_data is not None, patient_data is not None, 
      staff_data is not None, equipment_data is not None]):
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter
    min_date = financial_data['Date'].min().date()
    max_date = financial_data['Date'].max().date()
    
    start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
    
    # Location filter
    locations = ['All'] + sorted(financial_data['Location_Name'].unique().tolist())
    selected_location = st.sidebar.selectbox("Select Location", locations)
    
    # Period filter (Month, Quarter, Year)
    period_options = ['Month', 'Quarter', 'Year', 'All Time']
    selected_period = st.sidebar.selectbox("Select Time Period View", period_options)
    
    # Service line filter
    service_lines = ['All', 'Diagnostic', 'Preventive', 'Restorative', 'Endodontic', 'Periodontic',
                    'Prosthodontic', 'Oral_Surgery', 'Orthodontic', 'Implant', 'Adjunctive']
    selected_service = st.sidebar.selectbox("Select Service Line", service_lines)
    
    # Apply filters to financial data
    filtered_financial = financial_data.copy()
    
    # Date filter
    filtered_financial = filtered_financial[(filtered_financial['Date'].dt.date >= start_date) & 
                                          (filtered_financial['Date'].dt.date <= end_date)]
    
    # Location filter
    if selected_location != 'All':
        filtered_financial = filtered_financial[filtered_financial['Location_Name'] == selected_location]
    
    # Apply the same filters to operations data
    filtered_operations = operations_data[(operations_data['Date'].dt.date >= start_date) & 
                                        (operations_data['Date'].dt.date <= end_date)]
    
    if selected_location != 'All':
        filtered_operations = filtered_operations[filtered_operations['Location_Name'] == selected_location]
    
    # Apply the same filters to patient data
    filtered_patient = patient_data[(patient_data['Date_of_Service'].dt.date >= start_date) & 
                                  (patient_data['Date_of_Service'].dt.date <= end_date)]
    
    if selected_location != 'All':
        filtered_patient = filtered_patient[filtered_patient['Location_Name'] == selected_location]
    
    # Apply the same filters to staff data
    filtered_staff = staff_data[(staff_data['Date'].dt.date >= start_date) & 
                              (staff_data['Date'].dt.date <= end_date)]
    
    if selected_location != 'All':
        filtered_staff = filtered_staff[filtered_staff['Location_ID'].isin(filtered_financial['Location_ID'])]
    
    # Apply the same filters to equipment data
    filtered_equipment = equipment_data[(equipment_data['Date'].dt.date >= start_date) & 
                                      (equipment_data['Date'].dt.date <= end_date)]
    
    if selected_location != 'All':
        filtered_equipment = filtered_equipment[filtered_equipment['Location_ID'].isin(filtered_financial['Location_ID'])]
    
    # Key financial metrics
    total_revenue = filtered_financial['Total_Revenue'].sum()
    total_expenses = filtered_financial['Total_Expenses'].sum()
    total_ebitda = filtered_financial['EBITDA'].sum()
    ebitda_margin = (total_ebitda / total_revenue * 100) if total_revenue > 0 else 0
    avg_collection_rate = filtered_financial['Collection_Rate'].mean()
    avg_dso = filtered_financial['DSO'].mean()
    
    # Display key metrics
    st.markdown("## Key Financial Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.0f}", 
                 delta=f"{filtered_financial['Revenue_YoY_Change'].mean():.1f}%" if 'Revenue_YoY_Change' in filtered_financial.columns else None,
                 delta_color="normal")
    
    with col2:
        st.metric("EBITDA", f"${total_ebitda:,.0f}", 
                 delta=f"{filtered_financial['EBITDA_YoY_Change'].mean():.1f}%" if 'EBITDA_YoY_Change' in filtered_financial.columns else None,
                 delta_color="normal")
    
    with col3:
        st.metric("EBITDA Margin", f"{ebitda_margin:.1f}%")
    
    with col4:
        st.metric("Collection Rate", f"{avg_collection_rate:.1f}%")
    
    with col5:
        st.metric("Avg DSO", f"{avg_dso:.1f} days")
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Revenue Analysis",
        "Profitability & Margins",
        "AR & Collections",
        "Financial KPIs",
        "Financial Forecasting"
    ])
    
    # Tab 1: Revenue Analysis
    with tab1:
        st.subheader("Revenue Analysis")
        
        # Revenue Over Time
        st.markdown("### Revenue Trends")
        
        # Group by date/month depending on the period selected
        if selected_period == 'Month':
            revenue_trends = filtered_financial.groupby('Month_Year').agg({
                'Total_Revenue': 'sum',
                'Revenue_MoM_Change': 'mean'
            }).reset_index()
            revenue_trends = revenue_trends.sort_values('Month_Year')
            x_axis = 'Month_Year'
            title_period = "Monthly"
        elif selected_period == 'Quarter':
            filtered_financial['Quarter'] = filtered_financial['Date'].dt.to_period('Q')
            revenue_trends = filtered_financial.groupby('Quarter').agg({
                'Total_Revenue': 'sum',
                'Revenue_MoM_Change': 'mean'
            }).reset_index()
            revenue_trends['Quarter'] = revenue_trends['Quarter'].astype(str)
            revenue_trends = revenue_trends.sort_values('Quarter')
            x_axis = 'Quarter'
            title_period = "Quarterly"
        elif selected_period == 'Year':
            revenue_trends = filtered_financial.groupby('Year').agg({
                'Total_Revenue': 'sum',
                'Revenue_YoY_Change': 'mean'
            }).reset_index()
            revenue_trends = revenue_trends.sort_values('Year')
            x_axis = 'Year'
            title_period = "Annual"
        else:  # All Time
            revenue_trends = filtered_financial.groupby('Month_Year').agg({
                'Total_Revenue': 'sum'
            }).reset_index()
            revenue_trends = revenue_trends.sort_values('Month_Year')
            x_axis = 'Month_Year'
            title_period = "All Time"
        
        if not revenue_trends.empty:
            # Create revenue trend chart
            fig = px.line(
                revenue_trends,
                x=x_axis,
                y='Total_Revenue',
                title=f"{title_period} Revenue Trend",
                labels={
                    x_axis: "Period",
                    'Total_Revenue': 'Revenue ($)'
                },
                markers=True
            )
            
            # Add annotations for growth rates if available
            if selected_period == 'Month' and 'Revenue_MoM_Change' in revenue_trends.columns:
                for i, row in revenue_trends.iterrows():
                    if not pd.isna(row['Revenue_MoM_Change']):
                        fig.add_annotation(
                            x=row[x_axis],
                            y=row['Total_Revenue'],
                            text=f"{row['Revenue_MoM_Change']:.1f}%",
                            showarrow=False,
                            yshift=10
                        )
            elif selected_period == 'Year' and 'Revenue_YoY_Change' in revenue_trends.columns:
                for i, row in revenue_trends.iterrows():
                    if not pd.isna(row['Revenue_YoY_Change']):
                        fig.add_annotation(
                            x=row[x_axis],
                            y=row['Total_Revenue'],
                            text=f"{row['Revenue_YoY_Change']:.1f}%",
                            showarrow=False,
                            yshift=10
                        )
            
            # Update layout
            fig.update_layout(
                xaxis_title="Period",
                yaxis_title="Revenue ($)",
                yaxis=dict(tickprefix="$")
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No revenue trend data available for the selected filters.")
        
        # Revenue by Service Line
        st.markdown("### Revenue by Service Line")
        
        # Get service line columns
        service_columns = [col for col in filtered_financial.columns if col.startswith('Revenue_') and col != 'Revenue_MoM_Change' and col != 'Revenue_YoY_Change' and col != 'Revenue_Per_Square_Foot' and col != 'Revenue_Per_Patient']
        
        if service_columns:
            # Group by year-month and sum service revenue
            service_revenue = filtered_financial.groupby('Month_Year')[service_columns].sum().reset_index()
            
            # Melt the data for plotting
            service_revenue_melted = pd.melt(
                service_revenue,
                id_vars=['Month_Year'],
                value_vars=service_columns,
                var_name='Service_Line',
                value_name='Revenue'
            )
            
            # Clean service line names
            service_revenue_melted['Service_Line'] = service_revenue_melted['Service_Line'].str.replace('Revenue_', '').str.replace('_', ' ')
            
            # Filter by selected service line
            if selected_service != 'All':
                clean_service = selected_service.replace('_', ' ')
                service_revenue_melted = service_revenue_melted[service_revenue_melted['Service_Line'] == clean_service]
            
            # Create stacked bar chart
            fig = px.bar(
                service_revenue_melted,
                x='Month_Year',
                y='Revenue',
                color='Service_Line',
                title="Revenue by Service Line Over Time",
                labels={
                    'Month_Year': 'Month',
                    'Revenue': 'Revenue ($)',
                    'Service_Line': 'Service Line'
                }
            )
            
            # Update layout
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Revenue ($)",
                yaxis=dict(tickprefix="$"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Create a pie chart of service distribution
            service_totals = service_revenue_melted.groupby('Service_Line')['Revenue'].sum().reset_index()
            service_totals = service_totals.sort_values('Revenue', ascending=False)
            
            fig = px.pie(
                service_totals,
                values='Revenue',
                names='Service_Line',
                title="Revenue Distribution by Service Line",
                hole=0.4
            )
            
            # Add percentage labels
            fig.update_traces(textposition='inside', textinfo='percent+label')
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No service line revenue data available.")
        
        # Revenue by Location
        if selected_location == 'All':
            st.markdown("### Revenue by Location")
            
            # Group by location
            location_revenue = filtered_financial.groupby('Location_Name')['Total_Revenue'].sum().reset_index()
            location_revenue = location_revenue.sort_values('Total_Revenue', ascending=False)
            
            # Create bar chart
            fig = px.bar(
                location_revenue,
                x='Location_Name',
                y='Total_Revenue',
                color='Total_Revenue',
                title="Total Revenue by Location",
                labels={
                    'Location_Name': 'Location',
                    'Total_Revenue': 'Revenue ($)'
                },
                color_continuous_scale=px.colors.sequential.Blues
            )
            
            # Add revenue labels on bars
            fig.update_traces(texttemplate='$%{y:,.0f}', textposition='outside')
            
            # Update layout
            fig.update_layout(
                xaxis_title="Location",
                yaxis_title="Revenue ($)",
                yaxis=dict(tickprefix="$"),
                coloraxis_showscale=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Create a heatmap of service lines by location
            service_by_location = filtered_financial.groupby('Location_Name')[service_columns].sum().reset_index()
            
            # Melt for heatmap
            service_location_melted = pd.melt(
                service_by_location,
                id_vars=['Location_Name'],
                value_vars=service_columns,
                var_name='Service_Line',
                value_name='Revenue'
            )
            
            # Clean service line names
            service_location_melted['Service_Line'] = service_location_melted['Service_Line'].str.replace('Revenue_', '').str.replace('_', ' ')
            
            # Create pivot for heatmap
            service_pivot = service_location_melted.pivot(index='Location_Name', columns='Service_Line', values='Revenue')
            
            # Create heatmap
            fig = px.imshow(
                service_pivot,
                text_auto='.2s',
                aspect="auto",
                color_continuous_scale=px.colors.sequential.Blues,
                title="Service Line Revenue by Location"
            )
            
            # Update layout
            fig.update_layout(
                xaxis_title="Service Line",
                yaxis_title="Location",
                coloraxis_colorbar=dict(title="Revenue ($)")
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 2: Profitability & Margins
    with tab2:
        st.subheader("Profitability & Margins Analysis")
        
        # EBITDA Trends
        st.markdown("### EBITDA & Margin Trends")
        
        # Group by month/period
        if selected_period == 'Month':
            ebitda_trends = filtered_financial.groupby('Month_Year').agg({
                'Total_Revenue': 'sum',
                'EBITDA': 'sum',
                'EBITDA_Margin': 'mean',
                'EBITDA_MoM_Change': 'mean'
            }).reset_index()
            ebitda_trends = ebitda_trends.sort_values('Month_Year')
            x_axis = 'Month_Year'
            title_period = "Monthly"
        elif selected_period == 'Quarter':
            filtered_financial['Quarter'] = filtered_financial['Date'].dt.to_period('Q')
            ebitda_trends = filtered_financial.groupby('Quarter').agg({
                'Total_Revenue': 'sum',
                'EBITDA': 'sum',
                'EBITDA_Margin': 'mean'
            }).reset_index()
            ebitda_trends['Quarter'] = ebitda_trends['Quarter'].astype(str)
            ebitda_trends = ebitda_trends.sort_values('Quarter')
            x_axis = 'Quarter'
            title_period = "Quarterly"
        elif selected_period == 'Year':
            ebitda_trends = filtered_financial.groupby('Year').agg({
                'Total_Revenue': 'sum',
                'EBITDA': 'sum',
                'EBITDA_Margin': 'mean',
                'EBITDA_YoY_Change': 'mean'
            }).reset_index()
            ebitda_trends = ebitda_trends.sort_values('Year')
            x_axis = 'Year'
            title_period = "Annual"
        else:  # All Time
            ebitda_trends = filtered_financial.groupby('Month_Year').agg({
                'Total_Revenue': 'sum',
                'EBITDA': 'sum',
                'EBITDA_Margin': 'mean'
            }).reset_index()
            ebitda_trends = ebitda_trends.sort_values('Month_Year')
            x_axis = 'Month_Year'
            title_period = "All Time"
        
        # Calculate margin if not already in the data
        if 'EBITDA_Margin' not in ebitda_trends.columns:
            ebitda_trends['EBITDA_Margin'] = (ebitda_trends['EBITDA'] / ebitda_trends['Total_Revenue'] * 100).fillna(0)
        
        if not ebitda_trends.empty:
            # Create EBITDA with margin overlay chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=ebitda_trends[x_axis],
                y=ebitda_trends['EBITDA'],
                name='EBITDA',
                marker_color='rgba(0, 123, 255, 0.7)'
            ))
            
            fig.add_trace(go.Scatter(
                x=ebitda_trends[x_axis],
                y=ebitda_trends['EBITDA_Margin'],
                name='EBITDA Margin (%)',
                mode='lines+markers',
                marker=dict(color='red'),
                line=dict(color='red'),
                yaxis='y2'
            ))
            
            # Add annotations for MoM or YoY changes if available
            if selected_period == 'Month' and 'EBITDA_MoM_Change' in ebitda_trends.columns:
                for i, row in ebitda_trends.iterrows():
                    if not pd.isna(row['EBITDA_MoM_Change']):
                        fig.add_annotation(
                            x=row[x_axis],
                            y=row['EBITDA'],
                            text=f"{row['EBITDA_MoM_Change']:.1f}%",
                            showarrow=False,
                            yshift=10
                        )
            elif selected_period == 'Year' and 'EBITDA_YoY_Change' in ebitda_trends.columns:
                for i, row in ebitda_trends.iterrows():
                    if not pd.isna(row['EBITDA_YoY_Change']):
                        fig.add_annotation(
                            x=row[x_axis],
                            y=row['EBITDA'],
                            text=f"{row['EBITDA_YoY_Change']:.1f}%",
                            showarrow=False,
                            yshift=10
                        )
            
            # Update layout
            fig.update_layout(
                title=f"{title_period} EBITDA and Margin Trend",
                xaxis_title="Period",
                yaxis=dict(
                    title="EBITDA ($)",
                    tickprefix="$"
                ),
                yaxis2=dict(
                    title="EBITDA Margin (%)",
                    overlaying='y',
                    side='right',
                    range=[0, 100]
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No EBITDA trend data available for the selected filters.")
        
        # Cost Breakdown Analysis
        st.markdown("### Cost Breakdown Analysis")
        
        # Get expense columns
        expense_columns = [col for col in filtered_financial.columns if col.startswith('Labor_') or 
                         col.startswith('Supplies_') or col == 'Rent_Lease' or 
                         col == 'Utilities' or col == 'Equipment_Costs' or
                         col == 'Marketing' or col == 'Insurance' or
                         col == 'Professional_Fees' or col == 'Lab_Fees' or
                         col == 'Software_IT']
        
        if expense_columns:
            # Group expenses by month
            expense_by_month = filtered_financial.groupby('Month_Year')[expense_columns].sum().reset_index()
            
            # Melt for stacked area chart
            expense_melted = pd.melt(
                expense_by_month,
                id_vars=['Month_Year'],
                value_vars=expense_columns,
                var_name='Expense_Category',
                value_name='Amount'
            )
            
            # Create stacked area chart
            fig = px.area(
                expense_melted,
                x='Month_Year',
                y='Amount',
                color='Expense_Category',
                title="Expense Breakdown Over Time",
                labels={
                    'Month_Year': 'Month',
                    'Amount': 'Expense Amount ($)',
                    'Expense_Category': 'Expense Category'
                }
            )
            
            # Update layout
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Expense Amount ($)",
                yaxis=dict(tickprefix="$"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Create a pie chart of expense distribution
            expense_totals = expense_melted.groupby('Expense_Category')['Amount'].sum().reset_index()
            expense_totals = expense_totals.sort_values('Amount', ascending=False)
            
            fig = px.pie(
                expense_totals,
                values='Amount',
                names='Expense_Category',
                title="Expense Distribution",
                hole=0.4
            )
            
            # Add percentage labels
            fig.update_traces(textposition='inside', textinfo='percent+label')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Cost percentage trends
            st.markdown("### Cost as Percentage of Revenue")
            
            # Calculate cost percentages if they exist
            cost_cols = ['Labor_Cost_Percentage', 'Supply_Cost_Percentage']
            
            if all(col in filtered_financial.columns for col in cost_cols):
                # Group by month for cost percentages
                cost_pct_trends = filtered_financial.groupby('Month_Year')[cost_cols].mean().reset_index()
                cost_pct_trends = cost_pct_trends.sort_values('Month_Year')
                
                # Create line chart
                fig = go.Figure()
                
                for col in cost_cols:
                    fig.add_trace(go.Scatter(
                        x=cost_pct_trends['Month_Year'],
                        y=cost_pct_trends[col],
                        mode='lines+markers',
                        name=col.replace('_Percentage', '').replace('_', ' ')
                    ))
                
                # Add benchmark lines if you have industry benchmarks
                # fig.add_shape(type="line", x0=cost_pct_trends['Month_Year'].min(), y0=27, 
                #              x1=cost_pct_trends['Month_Year'].max(), y1=27,
                #              line=dict(color="green", width=2, dash="dash"),
                #              name="Labor Cost Benchmark (27%)")
                
                # Update layout
                fig.update_layout(
                    title="Cost Percentages Over Time",
                    xaxis_title="Month",
                    yaxis_title="Percentage of Revenue (%)",
                    yaxis=dict(ticksuffix="%"),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Cost percentage data not available.")
        else:
            st.info("No expense breakdown data available.")
        
        # Profitability by Location
        if selected_location == 'All':
            st.markdown("### Profitability by Location")
            
            # Group by location
            location_profit = filtered_financial.groupby('Location_Name').agg({
                'Total_Revenue': 'sum',
                'Total_Expenses': 'sum',
                'EBITDA': 'sum',
                'EBITDA_Margin': 'mean'
            }).reset_index()
            
            # Calculate margin if not already in the data
            if 'EBITDA_Margin' not in location_profit.columns:
                location_profit['EBITDA_Margin'] = (location_profit['EBITDA'] / location_profit['Total_Revenue'] * 100).fillna(0)
            
            # Sort by EBITDA
            location_profit = location_profit.sort_values('EBITDA', ascending=False)
            
            # Create bar chart with margin overlay
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=location_profit['Location_Name'],
                y=location_profit['EBITDA'],
                name='EBITDA',
                marker_color='rgba(0, 123, 255, 0.7)'
            ))
            
            fig.add_trace(go.Scatter(
                x=location_profit['Location_Name'],
                y=location_profit['EBITDA_Margin'],
                name='EBITDA Margin (%)',
                mode='lines+markers',
                marker=dict(color='red'),
                line=dict(color='red'),
                yaxis='y2'
            ))
            
            # Update layout
            fig.update_layout(
                title="EBITDA and Margin by Location",
                xaxis_title="Location",
                yaxis=dict(
                    title="EBITDA ($)",
                    tickprefix="$"
                ),
                yaxis2=dict(
                    title="EBITDA Margin (%)",
                    overlaying='y',
                    side='right',
                    range=[0, 100]
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Create a table of locations by profitability
            st.markdown("### Location Profitability Rankings")
            
            # Format for display
            display_df = location_profit.copy()
            display_df['EBITDA_Margin'] = display_df['EBITDA_Margin'].apply(lambda x: f"{x:.1f}%")
            display_df['Total_Revenue'] = display_df['Total_Revenue'].apply(lambda x: f"${x:,.0f}")
            display_df['Total_Expenses'] = display_df['Total_Expenses'].apply(lambda x: f"${x:,.0f}")
            display_df['EBITDA'] = display_df['EBITDA'].apply(lambda x: f"${x:,.0f}")
            
            # Rename columns for better readability
            display_df = display_df.rename(columns={
                'Location_Name': 'Location',
                'Total_Revenue': 'Revenue',
                'Total_Expenses': 'Expenses',
                'EBITDA': 'EBITDA',
                'EBITDA_Margin': 'EBITDA Margin'
            })
            
            st.dataframe(display_df, use_container_width=True)
    
    # Tab 3: AR & Collections
    with tab3:
        st.subheader("Accounts Receivable & Collections Analysis")
        
        # AR Aging Analysis
        st.markdown("### AR Aging Analysis")
        
        # Get AR aging columns
        ar_columns = ['AR_Current', 'AR_31_60', 'AR_61_90', 'AR_91_Plus', 'Total_AR']
        
        if all(col in filtered_financial.columns for col in ar_columns):
            # Get the most recent month's data for AR aging
            latest_month = filtered_financial['Month_Year'].max()
            latest_ar = filtered_financial[filtered_financial['Month_Year'] == latest_month]
            
            # Aggregate AR across all selected locations
            ar_aging = latest_ar[ar_columns].sum()
            
            # Create DataFrame for plotting
            ar_df = pd.DataFrame({
                'Age': ['Current', '31-60 Days', '61-90 Days', '90+ Days'],
                'Amount': [ar_aging['AR_Current'], ar_aging['AR_31_60'], ar_aging['AR_61_90'], ar_aging['AR_91_Plus']]
            })
            
            # Calculate percentages
            ar_df['Percentage'] = ar_df['Amount'] / ar_aging['Total_AR'] * 100
            
            # Create a pie chart
            fig = px.pie(
                ar_df,
                values='Percentage',
                names='Age',
                title="AR Aging Distribution",
                color='Age',
                color_discrete_map={
                    'Current': 'green',
                    '31-60 Days': 'yellow',
                    '61-90 Days': 'orange',
                    '90+ Days': 'red'
                },
                hole=0.4
            )
            
            # Add percentage and amount labels
            fig.update_traces(
                texttemplate='%{percent:.1%}<br>$%{value:.2s}',
                textposition='inside'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate AR metrics
            total_ar = ar_aging['Total_AR']
            ar_over_90 = ar_aging['AR_91_Plus']
            ar_over_90_pct = (ar_over_90 / total_ar * 100) if total_ar > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total AR", f"${total_ar:,.0f}")
            
            with col2:
                st.metric("AR > 90 Days", f"${ar_over_90:,.0f}")
            
            with col3:
                st.metric("AR > 90 Days %", f"{ar_over_90_pct:.1f}%")
            
            # AR Trend Analysis
            st.markdown("### AR Trend Analysis")
            
            # Group by month for AR trend
            ar_trend = filtered_financial.groupby('Month_Year')[ar_columns + ['DSO']].sum().reset_index()
            ar_trend = ar_trend.sort_values('Month_Year')
            
            # Create stacked area chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=ar_trend['Month_Year'],
                y=ar_trend['AR_Current'],
                name='Current',
                mode='none',
                stackgroup='one',
                fillcolor='rgba(0, 128, 0, 0.5)'
            ))
            
            fig.add_trace(go.Scatter(
                x=ar_trend['Month_Year'],
                y=ar_trend['AR_31_60'],
                name='31-60 Days',
                mode='none',
                stackgroup='one',
                fillcolor='rgba(255, 255, 0, 0.5)'
            ))
            
            fig.add_trace(go.Scatter(
                x=ar_trend['Month_Year'],
                y=ar_trend['AR_61_90'],
                name='61-90 Days',
                mode='none',
                stackgroup='one',
                fillcolor='rgba(255, 165, 0, 0.5)'
            ))
            
            fig.add_trace(go.Scatter(
                x=ar_trend['Month_Year'],
                y=ar_trend['AR_91_Plus'],
                name='90+ Days',
                mode='none',
                stackgroup='one',
                fillcolor='rgba(255, 0, 0, 0.5)'
            ))
            
            # Add DSO line
            fig.add_trace(go.Scatter(
                x=ar_trend['Month_Year'],
                y=ar_trend['DSO'],
                name='DSO (Days)',
                mode='lines+markers',
                line=dict(color='black', width=2),
                yaxis='y2'
            ))
            
            # Update layout
            fig.update_layout(
                title="AR Aging and DSO Trends",
                xaxis_title="Month",
                yaxis=dict(
                    title="AR Amount ($)",
                    tickprefix="$"
                ),
                yaxis2=dict(
                    title="DSO (Days)",
                    overlaying='y',
                    side='right'
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("AR aging data not available.")
        
        # Collections Analysis
        st.markdown("### Collections Performance")
        
        # Collection-related columns
        collection_cols = ['Collections_Expected', 'Collections_Actual', 'Collection_Rate']
        
        if all(col in filtered_financial.columns for col in collection_cols):
            # Group by month for collection trend
            collection_trend = filtered_financial.groupby('Month_Year')[collection_cols].agg({
                'Collections_Expected': 'sum',
                'Collections_Actual': 'sum',
                'Collection_Rate': 'mean'
            }).reset_index()
            collection_trend = collection_trend.sort_values('Month_Year')
            
            # Create bar chart with collection rate overlay
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=collection_trend['Month_Year'],
                y=collection_trend['Collections_Expected'],
                name='Expected Collections',
                marker_color='rgba(200, 200, 200, 0.7)'
            ))
            
            fig.add_trace(go.Bar(
                x=collection_trend['Month_Year'],
                y=collection_trend['Collections_Actual'],
                name='Actual Collections',
                marker_color='rgba(0, 123, 255, 0.7)'
            ))
            
            fig.add_trace(go.Scatter(
                x=collection_trend['Month_Year'],
                y=collection_trend['Collection_Rate'],
                name='Collection Rate (%)',
                mode='lines+markers',
                line=dict(color='red', width=2),
                yaxis='y2'
            ))
            
            # Update layout
            fig.update_layout(
                title="Collections Performance",
                xaxis_title="Month",
                yaxis=dict(
                    title="Collections Amount ($)",
                    tickprefix="$"
                ),
                yaxis2=dict(
                    title="Collection Rate (%)",
                    overlaying='y',
                    side='right',
                    range=[0, 100]
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                barmode='group'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Collections data not available.")
        
        # Insurance Claims Analysis
        st.markdown("### Insurance Claims Analysis")
        
        # Insurance-related columns
        insurance_cols = ['Total_Claims_Submitted', 'Claims_Outstanding', 'Claims_Denied', 'Avg_Days_To_Payment']
        
        if all(col in filtered_financial.columns for col in insurance_cols):
            # Group by month for insurance claims trend
            claims_trend = filtered_financial.groupby('Month_Year')[insurance_cols].agg({
                'Total_Claims_Submitted': 'sum',
                'Claims_Outstanding': 'sum',
                'Claims_Denied': 'sum',
                'Avg_Days_To_Payment': 'mean'
            }).reset_index()
            claims_trend = claims_trend.sort_values('Month_Year')
            
            # Calculate denial rate
            claims_trend['Denial_Rate'] = (claims_trend['Claims_Denied'] / claims_trend['Total_Claims_Submitted'] * 100).fillna(0)
            
            # Create bar chart with days to payment overlay
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=claims_trend['Month_Year'],
                y=claims_trend['Total_Claims_Submitted'],
                name='Claims Submitted',
                marker_color='rgba(200, 200, 200, 0.7)'
            ))
            
            fig.add_trace(go.Bar(
                x=claims_trend['Month_Year'],
                y=claims_trend['Claims_Outstanding'],
                name='Claims Outstanding',
                marker_color='rgba(255, 165, 0, 0.7)'
            ))
            
            fig.add_trace(go.Bar(
                x=claims_trend['Month_Year'],
                y=claims_trend['Claims_Denied'],
                name='Claims Denied',
                marker_color='rgba(255, 0, 0, 0.7)'
            ))
            
            fig.add_trace(go.Scatter(
                x=claims_trend['Month_Year'],
                y=claims_trend['Avg_Days_To_Payment'],
                name='Avg Days to Payment',
                mode='lines+markers',
                line=dict(color='black', width=2),
                yaxis='y2'
            ))
            
            # Update layout
            fig.update_layout(
                title="Insurance Claims Processing",
                xaxis_title="Month",
                yaxis=dict(
                    title="Number of Claims"
                ),
                yaxis2=dict(
                    title="Avg Days to Payment",
                    overlaying='y',
                    side='right'
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                barmode='group'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display denial rate chart
            fig = px.line(
                claims_trend,
                x='Month_Year',
                y='Denial_Rate',
                title="Insurance Claim Denial Rate Trend",
                labels={
                    'Month_Year': 'Month',
                    'Denial_Rate': 'Denial Rate (%)'
                },
                markers=True
            )
            
            # Add a target line at an acceptable denial rate (e.g., 5%)
            fig.add_shape(
                type="line",
                x0=claims_trend['Month_Year'].min(),
                y0=5,
                x1=claims_trend['Month_Year'].max(),
                y1=5,
                line=dict(color="red", width=2, dash="dash"),
            )
            
            # Update layout
            fig.update_layout(
                xaxis_title="Month",
                yaxis=dict(
                    title="Denial Rate (%)",
                    ticksuffix="%"
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Insurance claims data not available.")
        
        # Payor Mix Analysis if payor columns exist
        payor_cols = [col for col in filtered_financial.columns if col.startswith('Payor_')]
        
        if payor_cols:
            st.markdown("### Payor Mix Analysis")
            
            # Get the most recent month's data for payor mix
            latest_month = filtered_financial['Month_Year'].max()
            latest_payor = filtered_financial[filtered_financial['Month_Year'] == latest_month]
            
            # Aggregate payor data across all selected locations
            payor_mix = latest_payor[payor_cols].sum()
            
            # Create DataFrame for plotting
            payor_df = pd.DataFrame({
                'Payor': [col.replace('Payor_', '').replace('_', ' ') for col in payor_cols],
                'Amount': [payor_mix[col] for col in payor_cols]
            })
            
            # Calculate percentages
            payor_df['Percentage'] = payor_df['Amount'] / payor_df['Amount'].sum() * 100
            
            # Sort by amount
            payor_df = payor_df.sort_values('Amount', ascending=False)
            
            # Create a pie chart
            fig = px.pie(
                payor_df,
                values='Amount',
                names='Payor',
                title="Payor Mix Distribution",
                hole=0.4
            )
            
            # Add percentage and amount labels
            fig.update_traces(
                texttemplate='%{percent:.1%}<br>$%{value:.2s}',
                textposition='inside'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Create a bar chart of collection rate by payor if available
            if 'Collection_Rate' in filtered_financial.columns:
                # Get collection rate by payor
                # This would need a join with patient data or a way to associate payor with collection rate
                st.info("Collection rate by payor analysis would require additional data linkage.")
        else:
            st.info("Payor mix data not available.")
    
    # Tab 4: Financial KPIs
    with tab4:
        st.subheader("Financial Key Performance Indicators")
        
        # KPI Trends
        st.markdown("### KPI Trends")
        
        # Revenue per patient/visit/chair
        revenue_kpi_cols = ['Revenue_Per_Patient', 'Revenue_Per_Chair', 'Revenue_Per_Hour']
        
        if any(col in filtered_financial.columns for col in revenue_kpi_cols):
            available_kpis = [col for col in revenue_kpi_cols if col in filtered_financial.columns]
            
            # Group by month
            kpi_trends = filtered_financial.groupby('Month_Year')[available_kpis].mean().reset_index()
            kpi_trends = kpi_trends.sort_values('Month_Year')
            
            # Create multi-line chart
            fig = go.Figure()
            
            for col in available_kpis:
                fig.add_trace(go.Scatter(
                    x=kpi_trends['Month_Year'],
                    y=kpi_trends[col],
                    mode='lines+markers',
                    name=col.replace('_', ' ')
                ))
            
            # Update layout
            fig.update_layout(
                title="Revenue KPI Trends",
                xaxis_title="Month",
                yaxis=dict(
                    title="Amount ($)",
                    tickprefix="$"
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Revenue KPI data not available.")
        
        # Operational KPIs
        operational_kpi_cols = ['Chair_Utilization', 'Patient_Retention_Rate', 'Case_Acceptance_Rate', 'Treatment_Completion_Rate']
        
        if any(col in filtered_financial.columns for col in operational_kpi_cols):
            available_kpis = [col for col in operational_kpi_cols if col in filtered_financial.columns]
            
            # Group by month
            op_kpi_trends = filtered_financial.groupby('Month_Year')[available_kpis].mean().reset_index()
            op_kpi_trends = op_kpi_trends.sort_values('Month_Year')
            
            # Create multi-line chart
            fig = go.Figure()
            
            for col in available_kpis:
                fig.add_trace(go.Scatter(
                    x=op_kpi_trends['Month_Year'],
                    y=op_kpi_trends[col],
                    mode='lines+markers',
                    name=col.replace('_', ' ')
                ))
            
            # Update layout
            fig.update_layout(
                title="Operational KPI Trends",
                xaxis_title="Month",
                yaxis=dict(
                    title="Percentage (%)",
                    ticksuffix="%"
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Operational KPI data not available.")
        
        # KPI Benchmark Comparisons
        st.markdown("### KPI Benchmarks")
        
        # Define some industry benchmarks (these would typically come from industry research)
        benchmarks = {
            'Labor_Cost_Percentage': 27.0,
            'Supply_Cost_Percentage': 6.0,
            'EBITDA_Margin': 18.0,
            'Collection_Rate': 98.0,
            'DSO': 35.0,
            'Chair_Utilization': 85.0
        }
        
        # Get the most recent month's data for KPIs
        latest_month = filtered_financial['Month_Year'].max()
        latest_kpis = filtered_financial[filtered_financial['Month_Year'] == latest_month]
        
        # Calculate actual KPI values
        actual_kpis = {}
        for kpi in benchmarks.keys():
            if kpi in latest_kpis.columns:
                actual_kpis[kpi] = latest_kpis[kpi].mean()
        
        if actual_kpis:
            # Create DataFrame for plotting
            benchmark_df = pd.DataFrame({
                'KPI': list(actual_kpis.keys()),
                'Actual': list(actual_kpis.values()),
                'Benchmark': [benchmarks[kpi] for kpi in actual_kpis.keys()]
            })
            
            # Calculate percentage of benchmark achieved
            benchmark_df['Percentage'] = (benchmark_df['Actual'] / benchmark_df['Benchmark'] * 100)
            
            # Determine if higher or lower is better
            better_lower = ['Labor_Cost_Percentage', 'Supply_Cost_Percentage', 'DSO']
            benchmark_df['Better'] = benchmark_df['KPI'].apply(lambda x: 'Lower' if x in better_lower else 'Higher')
            
            # Create horizontal bar chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                y=benchmark_df['KPI'],
                x=benchmark_df['Actual'],
                name='Actual',
                orientation='h',
                marker_color=['red' if row['Better'] == 'Lower' and row['Actual'] > row['Benchmark'] or 
                            row['Better'] == 'Higher' and row['Actual'] < row['Benchmark'] else 'green' 
                            for i, row in benchmark_df.iterrows()]
            ))
            
            fig.add_trace(go.Bar(
                y=benchmark_df['KPI'],
                x=benchmark_df['Benchmark'],
                name='Benchmark',
                orientation='h',
                marker_color='rgba(200, 200, 200, 0.7)'
            ))
            
            # Update layout
            fig.update_layout(
                title="KPI Performance vs. Benchmarks",
                xaxis_title="Value",
                yaxis_title="KPI",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                barmode='group'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Create a table of KPI performance
            benchmark_df['Status'] = benchmark_df.apply(
                lambda x: 'Good' if (x['Better'] == 'Lower' and x['Actual'] <= x['Benchmark']) or 
                                   (x['Better'] == 'Higher' and x['Actual'] >= x['Benchmark']) else 'Needs Improvement',
                axis=1
            )
            
            # Format for display
            display_df = benchmark_df.copy()
            display_df['Actual'] = display_df.apply(
                lambda x: f"{x['Actual']:.1f}%" if 'Percentage' in x['KPI'] or x['KPI'] in ['Collection_Rate', 'Chair_Utilization', 'EBITDA_Margin'] 
                                                else f"{x['Actual']:.1f}",
                axis=1
            )
            display_df['Benchmark'] = display_df.apply(
                lambda x: f"{x['Benchmark']:.1f}%" if 'Percentage' in x['KPI'] or x['KPI'] in ['Collection_Rate', 'Chair_Utilization', 'EBITDA_Margin'] 
                                                  else f"{x['Benchmark']:.1f}",
                axis=1
            )
            
            # Create a better display of KPI names
            display_df['KPI'] = display_df['KPI'].apply(lambda x: x.replace('_', ' ').title())
            
            # Reorder columns
            display_df = display_df[['KPI', 'Actual', 'Benchmark', 'Better', 'Status']]
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("KPI benchmark data not available.")
        
        # KPI by Location
        if selected_location == 'All':
            st.markdown("### KPI by Location")
            
            # Select KPIs to display
            kpis_to_display = ['Revenue_Per_Patient', 'Revenue_Per_Chair', 'EBITDA_Margin', 'Collection_Rate', 'Chair_Utilization']
            available_kpis = [kpi for kpi in kpis_to_display if kpi in filtered_financial.columns]
            
            if available_kpis:
                # Group by location
                location_kpis = filtered_financial.groupby('Location_Name')[available_kpis].mean().reset_index()
                
                # Create radar chart for each location
                for i, location in enumerate(location_kpis['Location_Name']):
                    if i % 3 == 0:
                        # Create a new row of columns every three locations
                        cols = st.columns(3)
                    
                    with cols[i % 3]:
                        # Get KPI values for this location
                        location_data = location_kpis[location_kpis['Location_Name'] == location]
                        
                        # Prepare data for radar chart
                        categories = [kpi.replace('_', ' ') for kpi in available_kpis]
                        values = [location_data[kpi].values[0] for kpi in available_kpis]
                        
                        # Normalize values for better radar chart display
                        # Placeholder for actual normalization logic
                        
                        # Create radar chart
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatterpolar(
                            r=values,
                            theta=categories,
                            fill='toself',
                            name=location
                        ))
                        
                        fig.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, max(values) * 1.2]
                                )
                            ),
                            title=location
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("KPI data by location not available.")
    
    # Tab 5: Financial Forecasting
    with tab5:
        st.subheader("Financial Forecasting")
        
        # Revenue Forecasting
        st.markdown("### Revenue Forecast")
        
        # Get monthly revenue data
        if 'Total_Revenue' in filtered_financial.columns:
            # Group by month
            monthly_revenue = filtered_financial.groupby('Month_Year').agg({
                'Total_Revenue': 'sum',
                'Date': 'first'  # Keep a date for proper time series ordering
            }).reset_index()
            
            # Sort by date
            monthly_revenue = monthly_revenue.sort_values('Date')
            
            # Check if we have enough data for forecasting
            if len(monthly_revenue) >= 6:  # Need at least 6 months of data for a meaningful forecast
                # Create time series for forecasting
                revenue_ts = monthly_revenue.set_index('Date')['Total_Revenue']
                
                # Number of periods to forecast
                forecast_periods = 3  # Forecast next 3 months
                
                # Simple forecasting using moving average
                # For a simple moving average forecast
                window = min(3, len(revenue_ts))  # Use up to 3 months for moving average
                ma_forecast = revenue_ts.rolling(window=window).mean().iloc[-1]
                
                # Create a date range for the forecast
                last_date = revenue_ts.index.max()
                forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=forecast_periods, freq='MS')
                
                # Create a DataFrame for the forecast
                forecast_df = pd.DataFrame({
                    'Date': forecast_dates,
                    'Month_Year': [d.strftime('%Y-%m') for d in forecast_dates],
                    'Forecast': [ma_forecast] * forecast_periods,
                    'Type': ['Forecast'] * forecast_periods
                })
                
                # Prepare historical data for plotting
                historical_df = pd.DataFrame({
                    'Date': monthly_revenue['Date'],
                    'Month_Year': monthly_revenue['Month_Year'],
                    'Forecast': monthly_revenue['Total_Revenue'],
                    'Type': ['Historical'] * len(monthly_revenue)
                })
                
                # Combine historical and forecast data
                combined_df = pd.concat([historical_df, forecast_df])
                
                # Create the forecast chart
                fig = px.line(
                    combined_df,
                    x='Month_Year',
                    y='Forecast',
                    color='Type',
                    title="Revenue Forecast",
                    labels={
                        'Month_Year': 'Month',
                        'Forecast': 'Revenue ($)'
                    },
                    markers=True,
                    color_discrete_map={
                        'Historical': 'blue',
                        'Forecast': 'red'
                    }
                )
                
                # Add confidence interval for forecast (simplistic approach)
                for i, row in forecast_df.iterrows():
                    fig.add_shape(
                        type="rect",
                        x0=i,
                        y0=row['Forecast'] * 0.9,  # Lower bound (10% below forecast)
                        x1=i + 1,
                        y1=row['Forecast'] * 1.1,  # Upper bound (10% above forecast)
                        line=dict(width=0),
                        fillcolor="rgba(255, 0, 0, 0.2)"
                    )
                
                # Update layout
                fig.update_layout(
                    xaxis_title="Month",
                    yaxis=dict(
                        title="Revenue ($)",
                        tickprefix="$"
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display forecast metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Next Month Forecast", 
                        f"${forecast_df['Forecast'].iloc[0]:,.0f}",
                        delta=f"{(forecast_df['Forecast'].iloc[0] / historical_df['Forecast'].iloc[-1] - 1) * 100:.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "3-Month Forecast Total", 
                        f"${forecast_df['Forecast'].sum():,.0f}"
                    )
                
                with col3:
                    last_3_months = historical_df['Forecast'].tail(3).sum()
                    st.metric(
                        "vs. Last 3 Months", 
                        f"${last_3_months:,.0f}",
                        delta=f"{(forecast_df['Forecast'].sum() / last_3_months - 1) * 100:.1f}%"
                    )
            else:
                st.info("Insufficient historical data for forecasting. Need at least 6 months of data.")
        else:
            st.info("Revenue data not available for forecasting.")
        
        # Cash Flow Projection
        st.markdown("### Cash Flow Projection")
        
        # Check if we have the necessary data for cash flow projection
        if all(col in filtered_financial.columns for col in ['Total_Revenue', 'Collection_Rate', 'Total_Expenses']):
            # Group by month
            monthly_financials = filtered_financial.groupby('Month_Year').agg({
                'Total_Revenue': 'sum',
                'Collection_Rate': 'mean',
                'Total_Expenses': 'sum',
                'Date': 'first'  # Keep a date for proper time series ordering
            }).reset_index()
            
            # Sort by date
            monthly_financials = monthly_financials.sort_values('Date')
            
            # Calculate historical cash flow
            monthly_financials['Collections'] = monthly_financials['Total_Revenue'] * (monthly_financials['Collection_Rate'] / 100)
            monthly_financials['Cash_Flow'] = monthly_financials['Collections'] - monthly_financials['Total_Expenses']
            
            # Check if we have enough data for forecasting
            if len(monthly_financials) >= 6:  # Need at least 6 months of data for a meaningful forecast
                # Number of periods to forecast
                forecast_periods = 3  # Forecast next 3 months
                
                # Simple forecasting using moving averages
                # For revenue forecast
                window = min(3, len(monthly_financials))  # Use up to 3 months for moving average
                
                revenue_ma = monthly_financials['Total_Revenue'].rolling(window=window).mean().iloc[-1]
                collection_rate_ma = monthly_financials['Collection_Rate'].rolling(window=window).mean().iloc[-1]
                expenses_ma = monthly_financials['Total_Expenses'].rolling(window=window).mean().iloc[-1]
                
                # Create a date range for the forecast
                last_date = monthly_financials['Date'].max()
                forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=forecast_periods, freq='MS')
                
                # Create a DataFrame for the forecast
                forecast_df = pd.DataFrame({
                    'Date': forecast_dates,
                    'Month_Year': [d.strftime('%Y-%m') for d in forecast_dates],
                    'Total_Revenue': [revenue_ma] * forecast_periods,
                    'Collection_Rate': [collection_rate_ma] * forecast_periods,
                    'Total_Expenses': [expenses_ma] * forecast_periods,
                    'Type': ['Forecast'] * forecast_periods
                })
                
                # Calculate forecast cash flow
                forecast_df['Collections'] = forecast_df['Total_Revenue'] * (forecast_df['Collection_Rate'] / 100)
                forecast_df['Cash_Flow'] = forecast_df['Collections'] - forecast_df['Total_Expenses']
                
                # Prepare historical data for plotting
                historical_df = pd.DataFrame({
                    'Date': monthly_financials['Date'],
                    'Month_Year': monthly_financials['Month_Year'],
                    'Collections': monthly_financials['Collections'],
                    'Total_Expenses': monthly_financials['Total_Expenses'],
                    'Cash_Flow': monthly_financials['Cash_Flow'],
                    'Type': ['Historical'] * len(monthly_financials)
                })
                
                # Combine historical and forecast data
                combined_df = pd.concat([historical_df, forecast_df[['Date', 'Month_Year', 'Collections', 'Total_Expenses', 'Cash_Flow', 'Type']]])
                
                # Create the cash flow chart
                fig = go.Figure()
                
                # Add collections
                fig.add_trace(go.Bar(
                    x=historical_df['Month_Year'],
                    y=historical_df['Collections'],
                    name='Historical Collections',
                    marker_color='rgba(0, 123, 255, 0.7)'
                ))
                
                fig.add_trace(go.Bar(
                    x=forecast_df['Month_Year'],
                    y=forecast_df['Collections'],
                    name='Forecast Collections',
                    marker_color='rgba(0, 123, 255, 0.3)'
                ))
                
                # Add expenses
                fig.add_trace(go.Bar(
                    x=historical_df['Month_Year'],
                    y=historical_df['Total_Expenses'],
                    name='Historical Expenses',
                    marker_color='rgba(255, 99, 132, 0.7)'
                ))
                
                fig.add_trace(go.Bar(
                    x=forecast_df['Month_Year'],
                    y=forecast_df['Total_Expenses'],
                    name='Forecast Expenses',
                    marker_color='rgba(255, 99, 132, 0.3)'
                ))
                
                # Add cash flow line
                fig.add_trace(go.Scatter(
                    x=combined_df['Month_Year'],
                    y=combined_df['Cash_Flow'],
                    name='Cash Flow',
                    mode='lines+markers',
                    line=dict(color='black', width=2)
                ))
                
                # Update layout
                fig.update_layout(
                    title="Cash Flow Projection",
                    xaxis_title="Month",
                    yaxis=dict(
                        title="Amount ($)",
                        tickprefix="$"
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    barmode='group'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display cash flow metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Next Month Cash Flow", 
                        f"${forecast_df['Cash_Flow'].iloc[0]:,.0f}",
                        delta=f"{(forecast_df['Cash_Flow'].iloc[0] / historical_df['Cash_Flow'].iloc[-1] - 1) * 100:.1f}%" if historical_df['Cash_Flow'].iloc[-1] != 0 else None
                    )
                
                with col2:
                    st.metric(
                        "3-Month Forecast Cash Flow", 
                        f"${forecast_df['Cash_Flow'].sum():,.0f}"
                    )
                
                with col3:
                    last_3_months = historical_df['Cash_Flow'].tail(3).sum()
                    st.metric(
                        "vs. Last 3 Months", 
                        f"${last_3_months:,.0f}",
                        delta=f"{(forecast_df['Cash_Flow'].sum() / last_3_months - 1) * 100:.1f}%" if last_3_months != 0 else None
                    )
            else:
                st.info("Insufficient historical data for cash flow projection. Need at least 6 months of data.")
        else:
            st.info("Cash flow projection data not available.")
        
        # Financial What-If Scenarios
        st.markdown("### Financial What-If Scenarios")
        
        # Create sliders for scenario modeling
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Revenue Scenarios")
            
            # Get the most recent month's data
            latest_month = filtered_financial['Month_Year'].max()
            latest_data = filtered_financial[filtered_financial['Month_Year'] == latest_month]
            
            # Calculate averages for the baseline
            avg_revenue = latest_data['Total_Revenue'].mean()
            
            # Sliders for revenue scenarios
            revenue_change = st.slider(
                "Revenue Change (%)", 
                min_value=-20.0, 
                max_value=20.0, 
                value=0.0, 
                step=1.0,
                format="%.1f%%"
            )
            
            # If we have service line data, allow adjusting the mix
            service_columns = [col for col in filtered_financial.columns if col.startswith('Revenue_') and col != 'Revenue_MoM_Change' and col != 'Revenue_YoY_Change' and col != 'Revenue_Per_Square_Foot' and col != 'Revenue_Per_Patient']
            
            if service_columns:
                st.subheader("Service Mix Adjustments")
                
                # Calculate service percentages
                service_totals = latest_data[service_columns].sum()
                service_percentages = (service_totals / service_totals.sum() * 100).to_dict()
                
                # Create sliders for each service line
                service_mix_changes = {}
                for col in service_columns:
                    service_name = col.replace('Revenue_', '').replace('_', ' ')
                    default_pct = service_percentages[col]
                    service_mix_changes[col] = st.slider(
                        f"{service_name} Mix (%)", 
                        min_value=max(0.0, default_pct - 10.0), 
                        max_value=min(100.0, default_pct + 10.0), 
                        value=default_pct,
                        step=0.5,
                        format="%.1f%%"
                    )
        
        with col2:
            st.subheader("Cost Scenarios")
            
            # Calculate averages for the baseline
            avg_expenses = latest_data['Total_Expenses'].mean() if 'Total_Expenses' in latest_data.columns else 0
            avg_labor_pct = latest_data['Labor_Cost_Percentage'].mean() if 'Labor_Cost_Percentage' in latest_data.columns else 0
            avg_supply_pct = latest_data['Supply_Cost_Percentage'].mean() if 'Supply_Cost_Percentage' in latest_data.columns else 0
            
            # Sliders for cost scenarios
            if 'Labor_Cost_Percentage' in latest_data.columns:
                labor_change = st.slider(
                    "Labor Cost Change (%)", 
                    min_value=-10.0, 
                    max_value=10.0, 
                    value=0.0, 
                    step=0.5,
                    format="%.1f%%"
                )
            else:
                labor_change = 0.0
            
            if 'Supply_Cost_Percentage' in latest_data.columns:
                supply_change = st.slider(
                    "Supply Cost Change (%)", 
                    min_value=-10.0, 
                    max_value=10.0, 
                    value=0.0, 
                    step=0.5,
                    format="%.1f%%"
                )
            else:
                supply_change = 0.0
            
            if 'Collection_Rate' in latest_data.columns:
                avg_collection_rate = latest_data['Collection_Rate'].mean()
                collection_change = st.slider(
                    "Collection Rate Change (%)", 
                    min_value=-10.0, 
                    max_value=10.0, 
                    value=0.0, 
                    step=0.5,
                    format="%.1f%%"
                )
            else:
                collection_change = 0.0
                avg_collection_rate = 0.0
        
        # Display scenario results
        st.subheader("Scenario Impact")
        
        # Calculate scenario impacts
        new_revenue = avg_revenue * (1 + revenue_change / 100)
        
        # Calculate new expenses based on changes
        if 'Total_Expenses' in latest_data.columns:
            labor_portion = avg_expenses * (avg_labor_pct / 100) if avg_labor_pct > 0 else 0
            supply_portion = avg_expenses * (avg_supply_pct / 100) if avg_supply_pct > 0 else 0
            other_expenses = avg_expenses - labor_portion - supply_portion
            
            new_labor = labor_portion * (1 + labor_change / 100)
            new_supplies = supply_portion * (1 + supply_change / 100)
            new_expenses = new_labor + new_supplies + other_expenses
        else:
            new_expenses = 0
        
        # Calculate new EBITDA
        new_collections = new_revenue * ((avg_collection_rate + collection_change) / 100) if avg_collection_rate > 0 else new_revenue
        new_ebitda = new_collections - new_expenses
        new_ebitda_margin = (new_ebitda / new_revenue * 100) if new_revenue > 0 else 0
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Scenario Revenue", 
                f"${new_revenue:,.0f}",
                delta=f"{revenue_change:.1f}%"
            )
        
        with col2:
            st.metric(
                "Scenario EBITDA", 
                f"${new_ebitda:,.0f}",
                delta=f"{(new_ebitda / avg_revenue - (avg_revenue - avg_expenses) / avg_revenue) * 100:.1f}%" if avg_revenue > 0 else None
            )
        
        with col3:
            st.metric(
                "Scenario EBITDA Margin", 
                f"{new_ebitda_margin:.1f}%",
                delta=f"{new_ebitda_margin - ((avg_revenue - avg_expenses) / avg_revenue * 100):.1f}%" if avg_revenue > 0 else None
            )
        
        # Visual comparison of baseline vs. scenario
        baseline_values = [avg_revenue, avg_revenue - avg_expenses, (avg_revenue - avg_expenses) / avg_revenue * 100 if avg_revenue > 0 else 0]
        scenario_values = [new_revenue, new_ebitda, new_ebitda_margin]
        
        # Create comparison chart
        comparison_df = pd.DataFrame({
            'Metric': ['Revenue', 'EBITDA', 'EBITDA Margin (%)'],
            'Baseline': baseline_values,
            'Scenario': scenario_values
        })
        
        # Create bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=comparison_df['Metric'],
            y=comparison_df['Baseline'],
            name='Baseline',
            marker_color='rgba(0, 123, 255, 0.7)'
        ))
        
        fig.add_trace(go.Bar(
            x=comparison_df['Metric'],
            y=comparison_df['Scenario'],
            name='Scenario',
            marker_color='rgba(40, 167, 69, 0.7)'
        ))
        
        # Update layout
        fig.update_layout(
            title="Baseline vs. Scenario Comparison",
            xaxis_title="Metric",
            yaxis=dict(
                title="Value",
                tickprefix="$" if True else ""
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Footer with download options
    st.subheader("Data Download")
    
    # Create tabs for different data downloads
    tab1, tab2 = st.tabs(["Financial Data", "Key Metrics"])
    
    with tab1:
        st.dataframe(filtered_financial, height=300)
        csv_financial = filtered_financial.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Financial Data as CSV",
            data=csv_financial,
            file_name="filtered_financial_data.csv",
            mime="text/csv"
        )
    
    with tab2:
        # Create a summary metrics table
        metrics_dict = {
            'Month': filtered_financial['Month_Year'].unique().tolist(),
            'Total Revenue': [filtered_financial[filtered_financial['Month_Year'] == m]['Total_Revenue'].sum() for m in filtered_financial['Month_Year'].unique()],
            'EBITDA': [filtered_financial[filtered_financial['Month_Year'] == m]['EBITDA'].sum() for m in filtered_financial['Month_Year'].unique()],
            'EBITDA Margin (%)': [filtered_financial[filtered_financial['Month_Year'] == m]['EBITDA_Margin'].mean() for m in filtered_financial['Month_Year'].unique()],
            'Collection Rate (%)': [filtered_financial[filtered_financial['Month_Year'] == m]['Collection_Rate'].mean() for m in filtered_financial['Month_Year'].unique()],
            'DSO': [filtered_financial[filtered_financial['Month_Year'] == m]['DSO'].mean() for m in filtered_financial['Month_Year'].unique()]
        }
        
        metrics_df = pd.DataFrame(metrics_dict)
        
        st.dataframe(metrics_df, height=300)
        csv_metrics = metrics_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Key Metrics as CSV",
            data=csv_metrics,
            file_name="financial_key_metrics.csv",
            mime="text/csv"
        )

else:
    st.error("Failed to load data. Please check your data files and paths.")
