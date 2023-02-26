import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def extract_tables(csv):
    # Split the CSV by blank rows
    tables_csv = [g for _, g in csv.groupby((csv.isnull() | (csv == '')).all(1))]

    tables = {}
    for table_csv in tables_csv:
        table_idx = 0
        while table_idx < len(table_csv.index):
            # Look for table name in first column
            if not pd.isna(table_csv.loc[table_idx, table_csv.columns[0]]):
                table_name = table_csv.loc[table_idx, table_csv.columns[0]]

                # Find table dimensions
                table_height = 1
                while (table_idx + table_height) < len(table_csv.index) and all(pd.isna(table_csv.loc[table_idx + table_height, table_csv.columns[0]:3])):
                    table_height += 1
                data_start_idx = table_idx + table_height

                # Extract table data
                table_data = table_csv.iloc[data_start_idx:, :3]
                table_data = table_data.dropna()
                tables[table_name] = table_data

                # Move to next table
                table_idx += table_height
            else:
                table_idx += 1

    return tables

def get_crosstab_data(table_data):
    # pivot data to be in wide format
    table_data = table_data.pivot(index=table_data.columns[0], columns=table_data.columns[1], values=table_data.columns[2])

    # calculate totals for rows and columns
    table_data.loc[:, 'Total'] = table_data.sum(axis=1)
    table_data.loc['Total', :] = table_data.sum(axis=0)

    return table_data

def generate_plot(table_data, title):
    # Calculate the crosstab data
    crosstab_data = get_crosstab_data(table_data)
    
    # Get the index and columns levels to generate the plot labels
    index_levels = crosstab_data.index.levels
    column_levels = crosstab_data.columns.levels
    
    # Set the index and columns labels
    crosstab_data.index = crosstab_data.index.set_names([index_levels[0][0], index_levels[1][0]])
    crosstab_data.columns = crosstab_data.columns.set_names([column_levels[0][0], column_levels[1][0]])
    
    # Plot the data
    fig, ax = plt.subplots()
    crosstab_data.plot(kind='bar', ax=ax, rot=0)
    ax.set_title(title)
    ax.set_xlabel(table_data.columns[0])
    ax.set_ylabel(table_data.columns[2])
    st.pyplot(fig)

def main():
    csv_file = st.file_uploader('Upload CSV', type=['csv'])
    if csv_file is not None:
        csv = pd.read_csv(csv_file, header=None)
        tables = extract_tables(csv)
        table_names = list(tables.keys())
        if len(table_names) == 0:
            st.write('No tables found in CSV file.')
        else:
            table_name = st.selectbox('Select table', table_names)
            st.write(tables[table_name])
            generate_plot(tables[table_name], table_name)

if __name__ == '__main__':
    main()
