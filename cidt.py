# Import the required libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

# Define the get_table_headers function
import pandas as pd
import re

def extract_tables(csv):
    """
    Parse CSV string and return a dictionary of tables.

    Each table is a pandas DataFrame and is keyed by its table name.
    """

    # Split CSV string into a list of lines
    lines = csv.split('\n')

    # Initialize variables
    tables = {}
    current_table_name = None
    current_table_data = []
    current_table_hierarchy = None
    current_row_index = 0

    # Loop through each line in the CSV
    while current_row_index < len(lines):
        line = lines[current_row_index].strip()

        # Check if this line is a new table
        if re.match(r'^[,\s]*$', line):
            current_table_name = None
            current_table_hierarchy = None
            current_table_data = []

        # Check if this line contains a table name
        elif not current_table_name:
            current_table_name = line
            current_table_data = []
            current_table_hierarchy = []
            # Find end of table and calculate column totals
            for i in range(current_row_index, len(lines)):
                if re.match(r'^[^\s,]', lines[i]):
                    # This is the end of the table
                    break
                if not re.match(r'^[,\s]*$', lines[i]):
                    # This line is not empty, so calculate column totals
                    row_totals = lines[i].split(',')
                    row_totals = [float(x) if x != '' else 0.0 for x in row_totals]
                    current_table_data.append(row_totals)
                current_row_index += 1

        # Check if this line contains hierarchy information for the table
        elif not current_table_hierarchy:
            current_table_hierarchy.append(line)
            # Calculate the number of hierarchy levels from the number of empty rows
            num_levels = 0
            while re.match(r'^[,\s]*$', lines[current_row_index + num_levels]):
                num_levels += 1
            # Loop through the hierarchy rows and create a list of parent indices for each level
            current_table_hierarchy.append([])
            current_parent_indices = [0]
            current_level = 1
            for i in range(current_row_index + 1, current_row_index + num_levels):
                line = lines[i].strip()
                if line:
                    # This line is a parent cell
                    parent_index = len(current_table_hierarchy[current_level-1]) - 1
                    current_table_hierarchy[current_level].append(parent_index)
                    current_table_hierarchy[current_level-1].append(len(current_table_hierarchy[current_level]) - 1)
                    current_parent_indices.append(parent_index)
                    current_level += 1
                else:
                    # This line is an empty row, so decrement the current level
                    current_parent_indices.pop()
                    current_level -= 1
            current_row_index += num_levels - 1

        # This line contains table data
        else:
            row = [x.strip() for x in line.split(',')]
            # Check if this row contains a header
            if row[0]:
                header_row = [x for x in row[3:] if x]
                header_levels = [[] for _ in range(len(header_row))]
                for i, header in enumerate(header_row):
                    parent_index = current_table_hierarchy[len(header) // 2][i]
                    header_levels[len(header) - 1].append((parent_index, header))
                current_table_data.append([''] * 3 + header_row)
            else:
                # This row contains data
                current_row = row[3:]
               

    

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



