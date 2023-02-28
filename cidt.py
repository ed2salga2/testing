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
    df = pd.read_spss(csv)

    # find empty cells in dataframe
    empty_cells = df.isna()

    tables = {}
    current_table = None

    for i, row in df.iterrows():
        # Check if row is empty
        if row.isnull().all():
            continue

        # Check if row is the start of a new table
        if empty_cells.loc[i, 0]:
            table_name = row[0]
            tables[table_name] = {}
            current_table = table_name
            tables[table_name]['header_rows'] = []

            # find end of table row
            for j, value in row.iteritems():
                if pd.notna(value):
                    end_row = j
                    break

            # find row indexes
            tables[table_name]['row_indexes'] = [x for x in range(i+1, df.shape[0]-1) if not empty_cells.loc[x, 0]]

            # find header rows
            header_rows = []
            for k in range(i+1, df.shape[0]-1):
                if empty_cells.loc[k, 3]:
                    header_rows.append(k)
            tables[table_name]['header_rows'] = header_rows

            # initialize table data as empty dataframe
            table_data = pd.DataFrame(columns=df.loc[i:end_row-1, 3:end_row].iloc[0])

            # fill table data with values
            for k in range(i+2, end_row):
                table_data.loc[k-1] = df.loc[k, 3:end_row]

            # set row indexes
            table_data.index = tables[table_name]['row_indexes']

            # set table data in tables dictionary
            tables[table_name]['data'] = table_data

            # set header levels
            header_levels = {}
            parent_stack = []
            for header_row in header_rows:
                row = df.loc[header_row, 3:end_row]
                row_levels = []
                for cell in row:
                    if pd.notna(cell):
                        level = len(parent_stack)
                        if level not in header_levels:
                            header_levels[level] = []
                        if level == 0:
                            parent_stack = [cell]
                        else:
                            if level-1 < len(parent_stack):
                                parent_stack = parent_stack[:level-1]
                            parent_stack.append(cell)
                        row_levels.append(level)
                    else:
                        row_levels.append(np.nan)
                header_levels[len(parent_stack)] = list(set(row_levels))
            tables[table_name]['header_levels'] = header_levels

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



