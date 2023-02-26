# Import the required libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

# Define the get_table_headers function
import pandas as pd
import re

def extract_tables(csv):
    lines = csv_file.getvalue().split('\n')
    tables = {}
    while len(lines) > 0:
        if lines[0] == '':
            lines.pop(0)
            continue
        table_name = None
        for i, line in enumerate(lines):
            if line.strip() != '':
                table_name = line
                break
        if not table_name:
            break
        lines = lines[i+1:]
        last_row_index = None
        for i, line in enumerate(lines):
            if line.strip() == '':
                last_row_index = i
                break
        if not last_row_index:
            last_row_index = len(lines)
        total_row = last_row_index
        headers = []
        for i, line in enumerate(lines[:last_row_index]):
            if line.strip() != '':
                headers.append(line)
        num_cols = len(headers)
        df = pd.DataFrame(columns=headers)
        for i, line in enumerate(lines[last_row_index+1:]):
            if line.strip() == '':
                break
            row_data = line.split(',')
            row = {}
            for j in range(num_cols):
                row[headers[j]] = row_data[j]
            df = df.append(row, ignore_index=True)
        for col in headers:
            if col.startswith('Unnamed'):
                df = df.drop(col, axis=1)
        df = df.apply(pd.to_numeric, errors='ignore')
        tables[table_name] = df
        lines = lines[last_row_index+1+i+1:]
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



