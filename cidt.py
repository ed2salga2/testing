import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from functools import reduce

def extract_tables(csv):
    tables = {}
    table_idx = 0
    while table_idx < len(csv.index):
        # Look for table name in first column
        if not pd.isna(csv.iloc[table_idx, 0]):
            table_name = csv.iloc[table_idx, 0]
            data_start_idx = table_idx + 2
            
            # Determine table dimensions
            num_cols = 0
            while num_cols < csv.shape[1] and not pd.isna(csv.iloc[table_idx + 1, num_cols]):
                num_cols += 1
            num_rows = 0
            while data_start_idx + num_rows < len(csv.index) and not pd.isna(csv.iloc[data_start_idx + num_rows, 0]):
                num_rows += 1
            
            # Extract table data
            table_data = csv.iloc[data_start_idx:data_start_idx + num_rows, :num_cols]
            if table_data.empty:
                table_idx = data_start_idx + num_rows
                continue
            table_data = table_data.fillna('')
            table_data = table_data.set_index(table_data.columns[0])

            # Extract parent/child header information
            headers = {}
            parent_headers = list(table_data.columns)
            child_headers = list(reduce(lambda x, y: x + y, pd.crosstab(index=table_data.index, columns=[table_data[c] for c in parent_headers]).columns))
            for parent in parent_headers:
                child_start_idx = parent_headers.index(parent) * len(table_data.index)
                child_end_idx = child_start_idx + len(table_data.index)
                headers[parent] = child_headers[child_start_idx:child_end_idx]

            tables[table_name] = table_data
            tables[table_name + '_headers'] = headers

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
        csv = pd.read_csv(csv_file)
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
