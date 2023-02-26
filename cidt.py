# Import the required libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

# Define the get_table_headers function
def get_table_headers(tables):
    # Initialize an empty dictionary to store the table headers
    table_headers = {}

    # Loop through the keys and values of the tables dictionary
    for table_name, table_df in tables.items():
        
        # Get the crosstab headers by selecting the first row and first column of the dataframe
        headers = table_df.iloc[0, 1:].tolist() + table_df.iloc[1:, 0].tolist()

        # Remove any NaN values from the headers list
        headers = [header for header in headers if not pd.isna(header)]

        # Initialize an empty list to store the header hierarchy
        header_hierarchy = []

        # Loop through the headers list and create a list of tuples representing the hierarchy
        for header in headers:
            if len(header_hierarchy) == 0:
                header_hierarchy.append((header,))
            else:
                current_level = header_hierarchy[-1]
                if header in table_df.columns:
                    header_hierarchy[-1] = current_level + (header,)
                else:
                    header_hierarchy.append((header,))

        # Store the header hierarchy in the table_headers dictionary with the table name as the key
        table_headers[table_name] = header_hierarchy

    return table_headers

# Define the extract_tables function
def extract_tables(csv):
    # Read the CSV string into a pandas dataframe
    df = pd.read_csv(StringIO(csv), header=None)

    # Initialize an empty dictionary to store the tables
    tables = {}

    # Loop through the dataframe rows
    for i in range(len(df)):
        row = df.iloc[i]

        # Check if the row contains the start of a new table
        if not pd.isnull(row[1]) and pd.isnull(row[2]):

            # Extract the table name from the first non-blank cell in the row
            table_name = row[row.notnull()].iloc[0]

            # Remove any non-alphanumeric characters from the table name and convert to lowercase
            table_name = ''.join(e for e in table_name if e.isalnum()).lower()

            # Create a new dataframe for the table, starting from the next row
            table_df = pd.DataFrame(columns=row[1:])

            # Loop through the next rows until the end of the table
            j = i + 1
            while j < len(df) and not pd.isnull(df.iloc[j][1]):
                row = df.iloc[j]
                table_df.loc[len(table_df)] = row[1:]
                j += 1

            # Store the table in the dictionary with the cleaned table name as the key
            tables[table_name] = table_df

    return tables

# Define the plot_table function
def plot_table(table, plot_type, filter_columns, plot_options):
    # Filter the table based on the filter columns
    for column, value in filter_columns.items():
        if value != 'All':
            table = table[table[column] == value]

    # Get the table headers
    table_headers = get_table_headers({table.name: table})

    # Create a list of tuples representing the columns to plot
    plot_columns = []
    for header in plot_options['Headers']:
        for col in table.columns:
            if header in col:
                plot_columns.append(col)

    # Initialize the figure and axis objects
    fig, ax = plt.subplots()

    # Check the plot type and plot accordingly
    if plot_type == 'Bar':
        table.plot(x=plot_columns[0], y=plot_columns[1:], kind='bar', ax=ax, color=plot_options['Color'])
    elif plot_type == 'Line':
        table.plot(x=plot_columns[0], y=plot_columns[1:], kind='line', ax=ax, color=plot_options['Color'])
    elif plot_type == 'Scatter':
        table.plot(x=plot_columns[0], y=plot_columns[1], kind='scatter', ax=ax, color=plot_options['Color'])
    elif plot_type == 'Boxplot':
        table.plot(x=plot_columns[0], y=plot_columns[1:], kind='box', ax=ax, color=plot_options['Color'])

    # Set the plot title and axis labels
    ax.set_title(plot_options['Title'])
    ax.set_xlabel(plot_options['X Axis Label'])
    ax.set_ylabel(plot_options['Y Axis Label'])

    # Show the plot
    st.pyplot(fig)

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

        # Create a dropdown menu to select the table to plot
        table_name = st.selectbox('Select a table to plot', options=list(tables.keys()))

        # If the selected table is not empty
        if not tables[table_name].empty:
            # Create a list of the column headers in the table
            column_headers = ['All'] + list(tables[table_name].columns)

            # Create a dictionary to store the filter options
            filter_options = {}

            # Loop through the header hierarchy and add each level to the filter options
            for level in get_table_headers({table_name: tables[table_name]})[table_name]:
                header = ' '.join(level)
                filter_options[header] = st.selectbox(header, options=column_headers)

            # Create a dropdown menu to select the plot type
            plot_type = st.selectbox('Select a plot type', options=['Bar', 'Line', 'Scatter', 'Boxplot'])

            # Create a list of the column headers in the table
            headers = []
            for level in get_table_headers({table_name: tables[table_name]})[table_name]:
                header = ' '.join(level)
                headers.append(header)

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
                filtered_table = tables[table_name].copy().reset_index(drop=True)
                for column, value in filter_columns.items():
                    filtered_table = filtered_table[filtered_table[column] == value]

                # If the filtered table is not empty
                if not filtered_table.empty:
                    # Plot the table based on the selected plot type and plot options
                    plot_table(filtered_table, plot_type, filter_columns, plot_options)
                else:
                    # Display a message if the filtered table is empty
                    st.write('No data')

    # Set the app footer
    st.text('Created by CAN with love for coding')

# Call the main function
if __name__ == '__main__':
    main()
