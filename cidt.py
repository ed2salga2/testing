# Import the required libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

# Define the get_table_headers function
import pandas as pd
import re

from io import BytesIO
from savReaderWriter import SavReader

def extract_tables(csv):
    tables = {}
    with BytesIO(csv) as f:
        with SavReader(f) as reader:
            # Extract each table from the SPSS file
            while True:
                try:
                    # Find the start of the next table
                    while True:
                        # Read the next line from the SPSS file
                        row = reader.next()
                        if row[0] != b'':
                            break
                    # The first non-empty cell in this row is the table name
                    table_name = row[0].decode('utf-8')
                    tables[table_name] = {}
                    # Find the end of the table (the "Total" row)
                    while True:
                        row = reader.next()
                        if row[0] == b'Total':
                            break
                    # Get the column headers from the row above the data
                    headers = [col.decode('utf-8') for col in row]
                    # Find the start of the data
                    while True:
                        row = reader.next()
                        if row[0] != b'Total':
                            break
                    # Get the row indexes from the first column
                    index_cols = [row[0].decode('utf-8') for row in reader]
                    # Get the data from the remaining columns
                    data_cols = [list(row)[1:] for row in reader]
                    # Store the data in a pandas dataframe
                    df = pd.DataFrame(data_cols, index=index_cols, columns=headers[1:])
                    tables[table_name]['data'] = df
                    # Get the header hierarchy from the fourth column
                    header_hierarchy = []
                    for row in reader:
                        if row[3] != b'':
                            header_hierarchy.append(row[3].decode('utf-8'))
                    tables[table_name]['header_hierarchy'] = header_hierarchy
                except StopIteration:
                    break
    return tables


               

    

# Define the plot_table function
def plot_table_data(tables, table_name):
    # Check if the selected table is in the tables dictionary
    if table_name not in tables:
        st.write('Table not found')
        return

    # Get the headers for the selected table
    headers = [header[0] for header in get_table_headers({table_name: tables[table_name]})[table_name]]

    # Create a dictionary to store the filter options
    filter_options = {}

    # Loop through the headers and create a filter dropdown for each column
    for header in headers:
        unique_values = sorted(list(set(tables[table_name][header].tolist())))
        filter_options[header] = st.selectbox(f'Select {header}', ['All'] + unique_values)

    # Create a list of available plot types
    plot_types = ['line', 'bar', 'scatter', 'hist']

    # Create a dropdown to select the plot type
    plot_type = st.selectbox('Select plot type', plot_types)

    # Create a list of tuples representing the columns to plot
    plot_columns = []
    for header in plot_options['Headers']:
        if header in tables[table_name].columns:
            plot_columns.append((header, 'column'))
        elif header in tables[table_name].index:
            plot_columns.append((header, 'index'))

    # Check if there are any columns to plot
    if len(plot_columns) == 0:
        st.write('No columns selected for plotting')
        return

    # Create a dictionary to store the plot options
    plot_options = {
        'Headers': st.multiselect('Select columns to plot', options=headers),
        'Title': st.text_input('Enter the plot title', value=table_name),
        'X Axis Label': st.text_input('Enter the X axis label', value=headers[0]),
        'Y Axis Label': st.text_input('Enter the Y axis label', value='Count'),
        'Color': st.color_picker('Select a plot color', value='#1f77b4')
    }

    # Create a button to plot the selected options
    plot_button = st.button('Plot')

    # If the plot button is clicked
    if plot_button:
        # Filter the table based on the selected filter options
        filter_columns = {}
        for key, value in filter_options.items():
            if value != 'All':
                filter_columns[key] = value
        filtered_table = tables.get(table_name, pd.DataFrame()).copy().reset_index(drop=True)
        for column, value in filter_columns.items():
            filtered_table = filtered_table[filtered_table[column] == value]

        # If the filtered table is not empty
        if not filtered_table.empty:
            # Plot the table based on the selected plot type and plot options
            plot_table(filtered_table, plot_type, filter_columns, plot_options)
        else:
            # Display a message if the filtered table is empty
            st.write('No data')

# Define the main function
def main():
    # Set the app title and page icon
    st.set_page_config(page_title='Crosstab Plotter', page_icon=':chart_with_upwards_trend:')

    # Set the app header and subheader
    st.header('Crosstab Plotter')
    st.subheader('Upload a CSV file to get started!')

    # Create a file uploader widget and prompt the user to upload a CSV file
    csv_file = st.file_uploader('Upload a CSV file', type='csv')

    # If the user has uploaded a file
    if csv_file is not None:
        # Extract the tables from the CSV file
        tables = extract_tables(csv_file.getvalue())

        # If there are no tables in the CSV file
        if not tables:
            st.write('No tables found in the CSV file')
            return

        # Create a dropdown menu to select the table to plot
        table_name = st.selectbox('Select a table to plot', options=list(tables.keys()))

        # Call the plot_table_data function to plot the table
        plot_table_data(tables, table_name)

    # Set the app footer
    st.text('Created by Zompopa Solutions with love for coding')

if __name__ == '__main__':
    main()



