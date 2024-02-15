import streamlit as st 
import pandas as pd
import plotly.express as px
import plotly
import cufflinks


# Function to load data from Excel file
def load_data(file_path):
    return pd.read_excel(file_path,engine='openpyxl')

# File path to your Excel file
file_path = "Data.xlsx"  # Replace this with the actual path to your Excel file

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

st.sidebar.subheader('Data Selection')

# Display DataFrame
st.dataframe(df)

# Group by selection
groupby_column = st.sidebar.selectbox(
    'What would you like to analyse?',
    ('Ship Mode','Segment','Category','Sub-Category')
)

if groupby_column:
    output_columns = ['Sales', 'Profit']
    df_grouped = df.groupby(by=[groupby_column], as_index=False)[output_columns].sum()
    st.dataframe(df_grouped)

    # Bar Chart
    st.write("## Bar Chart")
    st.write("This bar chart shows the total sales and profit for each category.")
    fig_bar = px.bar(
        df_grouped,
        x=groupby_column,
        y='Sales',
        color='Profit',
        color_continuous_scale=['red', 'yellow', 'green'],
        template='plotly_white'
    )
    st.plotly_chart(fig_bar)

    # Pie Chart
    st.write("## Pie Chart")
    st.write(f"This pie chart displays the distribution of sales by {groupby_column}.")
    fig_pie = px.pie(
        df_grouped,
        values='Sales',
        names=groupby_column,
        title=f'Distribution of Sales by {groupby_column}',
        template='plotly_white'
    )
    st.plotly_chart(fig_pie)

    # Line Chart for Sales Over Time
    if 'Order Date' in df.columns:
        st.write("## Line Chart for Sales Over Time")
        st.write("This line chart shows the total sales over time.")
        df_time = df.groupby(pd.Grouper(key='Order Date', freq='M')).sum().reset_index()
        fig_time = px.line(
            df_time,
            x='Order Date',
            y='Sales',
            title='Total Sales Over Time',
            template='plotly_white'
        )
        st.plotly_chart(fig_time)
    else:
        st.write("## Line Chart for Sales Over Time")
        st.write("No 'Order Date' column found. Unable to create chart.")
        
