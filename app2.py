# Import necessary libraries
import streamlit as st
import pandas as pd
import plotly.express as px

# Function to load data from Excel file
def load_data(file_path):
    return pd.read_excel(file_path, engine='openpyxl')

# File path to your Excel file
file_path = "C:/Users/AMOL/Desktop/project/Dataa.xlsx"  # Replace this with the actual path to your Excel file

# Load data
df = load_data(file_path)

# Streamlit setup
st.set_page_config(page_title='Dashboard 1')
st.title('Sales Dashboard')

# Information about the data
st.write("""
### About the Data
This dataset contains information about sales transactions, including details such as ship mode, segment, category, sub-category, sales, profit, and order date.

#### Additional Information:
- **Number of Categories:** {}
- **Number of Sub-Categories:** {}
- **Total Regions:** {}
""".format(
    df['Category'].nunique(),
    df['Sub-Category'].nunique(),
    df['Region'].nunique()
))

st.sidebar.subheader('Filters for Bar & Donut Chart')

# Display DataFrame
st.dataframe(df)

# Group by selection
groupby_column = st.sidebar.selectbox(
    'What would you like to analyse?',
    ('Ship Mode', 'Segment', 'Category', 'Sub-Category', 'State', 'City', 'Region')
)

# Filter by category (if applicable)
if groupby_column != 'Category':
    df_filtered = df
else:
    df_filtered = df

if groupby_column:
    output_columns = ['Sales', 'Profit']
    if groupby_column in ['State', 'City']:
        df_grouped = df_filtered.groupby(by=[groupby_column], as_index=False)[output_columns].sum()
    else:
        df_grouped = df_filtered.groupby(by=[groupby_column], as_index=False)[output_columns].sum()
    st.dataframe(df_grouped)

    # Bar Chart
    st.write("## Bar Chart")
    st.write(f"This bar chart shows the total sales and profit for each {groupby_column}.")
    fig_bar = px.bar(
        df_grouped,
        x=groupby_column,
        y='Sales',
        color='Profit',
        color_continuous_scale=['red', 'yellow', 'green'],
        template='plotly_white'
    )
    st.plotly_chart(fig_bar)

    # Pie Charts
    st.write("## Donut Charts")
    st.write("These pie charts display the distribution of sales and profit.")
    
    # Calculate total sales and profit
    total_sales = df_grouped['Sales'].sum()
    total_profit = df_grouped['Profit'].sum()
    
    # Pie chart for sales
    fig_pie_sales = px.pie(
        names=df_grouped[groupby_column],
        values=df_grouped['Sales'],
        title=f'Distribution of Sales by {groupby_column}',
        template='plotly_white',
        hole=0.3,
        labels={groupby_column: f'{groupby_column}', 'value': 'Sales'},
        height=300,  # Adjust height
        width=300,   # Adjust width
    )
    
    # Pie chart for profit
    fig_pie_profit = px.pie(
        names=df_grouped[groupby_column],
        values=df_grouped['Profit'],
        title=f'Distribution of Profit by {groupby_column}',
        template='plotly_white',
        hole=0.3,
        labels={groupby_column: f'{groupby_column}', 'value': 'Profit'},
        height=300,  # Adjust height
        width=300,   # Adjust width
    )
    
    # Display pie charts side by side using columns layout
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_pie_sales)
    with col2:
        st.plotly_chart(fig_pie_profit)
    
# Assuming 'df' is your DataFrame containing sales, profit, and region data

if 'Order Date' in df.columns:
    st.write("## Line Chart for Sales and Profit Over Time")
    
    # Filters section for line chart
    st.sidebar.subheader('Filters for Line Chart')

    # Option button to select metric
    selected_metric = st.sidebar.radio("Select metric to display:", ('Sales', 'Profit'))
    
    # Option button to select region
    selected_region = st.sidebar.radio("Select region to display:", df['Region'].unique())
    
    # Option button to select category for bar chart
    
    st.write(f"This line chart shows the total {selected_metric.lower()} for region {selected_region} over time.")
    
    # Filter data by selected region
    df_filtered_time = df[df['Region'] == selected_region]
    
    # Group by Order Date and sum
    df_time_combined = df_filtered_time.groupby(pd.Grouper(key='Order Date', freq='M')).sum().reset_index()
    
    # Create line chart
    fig_time_combined = px.line(
        df_time_combined,
        x='Order Date',
        y=selected_metric,
        title=f"Total {selected_metric} for Region {selected_region} Over Time",
        template='plotly_white',
        labels={'value': 'Amount', 'variable': 'Metric'}
    )
    st.plotly_chart(fig_time_combined)
else:
    st.write("## Line Chart for Sales and Profit Over Time")
    st.write("No 'Order Date' column found. Unable to create chart.")

# Sidebar
st.sidebar.subheader('Filters for Geo-Heatmap')

# Option button for selecting metric (sales or profit) in the sidebar
selected_metric = st.sidebar.radio("Select metric to visualize:", ("Sales", "Profit"))

# Group by latitude and longitude and sum of selected metric
if selected_metric == "Sales":
    metric_column = 'Sales'
else:
    metric_column = 'Profit'

df_grouped_location = df.groupby(['Latitude', 'Longitude']).agg({
    metric_column: 'sum',
    'Discount': 'sum',
    'Quantity': 'sum',
    'Region': lambda x: x.mode()[0],  # Most frequent region
    'Postal Code': lambda x: x.mode()[0],  # Most frequent postal code
    'State': lambda x: x.mode()[0],  # Most frequent state
    'City': lambda x: x.mode()[0]  # Most frequent city
}).reset_index()

# Plot map with heatmap
st.write("## Geographic Patterns with Heatmap")
st.write(f"This heatmap visualizes the sum of {selected_metric.lower()} by location across the United States.")

fig = px.density_mapbox(
    df_grouped_location,
    lat='Latitude',
    lon='Longitude',
    z=metric_column,
    radius=25,
    center=dict(lat=37.0902, lon=-95.7129),
    zoom=3,
    mapbox_style="carto-positron",
    title=f"Sum of {selected_metric} by Location",
    labels={metric_column: f'Sum of {selected_metric} ($)', 'Latitude': 'Latitude', 'Longitude': 'Longitude'},
    color_continuous_scale="Viridis",  # You can choose other color scales as well
    custom_data=['Discount', 'Quantity', 'Region', 'Postal Code', 'State', 'City'],  # Additional data for hovering
)

# Update hover template
fig.update_traces(hovertemplate="<b>Latitude</b>: %{lat}<br><b>Longitude</b>: %{lon}<br>"
                                  "<b>Sum of Sales</b>: %{z:.2f}<br>"
                                  "<b>Total Discount</b>: %{customdata[0]:.2f}<br>"
                                  "<b>Total Quantity</b>: %{customdata[1]}<br>"
                                  "<b>Region</b>: %{customdata[2]}<br>"
                                  "<b>State</b>: %{customdata[4]}<br>"
                                  "<b>City</b>: %{customdata[5]}<br>"
                                  "<b>Postal Code</b>: %{customdata[3]}")

# Show the map
st.plotly_chart(fig)
