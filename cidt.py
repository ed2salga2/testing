import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from functools import reduce
 
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
                table_data = table_csv.iloc[data_start_idx:, 3:]
                table_data = table_data.fillna('')
                table_data = table_data.set_index(table_data.columns[0])
                table_data.index.name = None
                table_data.columns.name = None
                table_data = table_data.apply(pd.to_numeric, errors='coerce')
                tables[table_name] = table_data

                # Extract parent/child header information
                headers = {}
                num_levels = table_data.columns.nlevels
                for level in range(num_levels):
                    if level < len(table_data.columns.levels):
                        header_level = [h for h in table_data.columns.levels[level] if h]
                        if header_level:
                            headers[header_level[0]] = list(table_data.columns.get_level_values(level + 1))

                tables[table_name + '_headers'] = headers

                # Move to next table
                table_idx += table_height
            else:
                table_idx += 1

    return tables




def generate_plot(table_data, title):
    fig, ax = plt.subplots()
    table_data.plot(kind='bar', x='Category', y='Value', ax=ax)
    ax.set_title(title)
    ax.set_xlabel(table_data.columns[0])
    ax.set_ylabel(table_data.columns[1])
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
