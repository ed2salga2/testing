import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from functools import reduce

import pandas as pd

def extract_tables(csv):
    tables = {}
    table_idx = 0
    while table_idx < len(csv.index):
        # Look for table name in first column
        if not pd.isna(csv.loc[table_idx, csv.columns[0]]):
            table_name = csv.loc[table_idx, csv.columns[0]]
            data_start_idx = table_idx + 2

            # Determine table dimensions
            col_start_idx = 1
            while pd.isna(csv.loc[table_idx + 1, csv.columns[col_start_idx]]):
                col_start_idx += 1
            col_end_idx = col_start_idx
            while col_end_idx < csv.shape[1] and not pd.isna(csv.loc[table_idx + 1, csv.columns[col_end_idx]]):
                col_end_idx += 1
            num_cols = col_end_idx - col_start_idx

            num_rows = 0
            while data_start_idx + num_rows < len(csv.index) and not pd.isna(csv.loc[data_start_idx + num_rows, csv.columns[0]]):
                num_rows += 1

            # Extract table data
            table_data = csv.iloc[data_start_idx:data_start_idx + num_rows, col_start_idx:col_end_idx]
            table_data = table_data.fillna('')
            table_data = table_data.set_index(table_data.columns[0])
            table_data.index.name = None
            table_data.columns.name = None
            table_data = table_data.apply(pd.to_numeric, errors='coerce')
            tables[table_name] = {'data': table_data}

            # Extract parent/child header information
            headers = {}
            parent_headers = list(table_data.columns)
            child_headers = [item for sublist in pd.crosstab(index=table_data.index, columns=[table_data[c] for c in parent_headers]).columns for item in sublist]
            for parent, child in zip(parent_headers, child_headers):
                if parent not in headers:
                    headers[parent] = []
                headers[parent].append(child)

            tables[table_name]['headers'] = headers

            # Extract hierarchy levels
            header_rows = table_data.columns.nlevels
            hierarchy_levels = []
            for i in range(header_rows):
                level = []
                for j in range(len(table_data.columns.levels[i])):
                    level.append(table_data.columns.levels[i][j])
                hierarchy_levels.append(level)
            tables[table_name]['hierarchy_levels'] = hierarchy_levels

            # Move to next table
            table_idx = data_start_idx + num_rows
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
        csv = pd.read_csv(csv_file,header=None)
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
