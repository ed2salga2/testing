import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from functools import reduce
 
def extract_tables(csv):
    tables = {}
    table_idx = 0
    
    while table_idx < len(csv.index):
        # Look for table name in first column
        if not pd.isna(csv.loc[table_idx, csv.columns[0]]):
            table_name = csv.loc[table_idx, csv.columns[0]]
            data_start_idx = table_idx + 2
            
            # Determine table dimensions
            num_cols = 0
            for i in range(3):
                if pd.isna(csv.loc[table_idx, csv.columns[i]]):
                    break
                num_cols += 1
                
            num_rows = 1
            while pd.isna(csv.loc[table_idx + num_rows, csv.columns[0]]):
                num_rows += 1
            
            # Extract table data
            table_data = csv.iloc[data_start_idx:data_start_idx + num_rows - 1, :num_cols]
            table_data = table_data.fillna('')
            table_data = table_data.set_index(table_data.columns[0])
            table_data.index.name = None
            table_data.columns.name = None
            table_data = table_data.apply(pd.to_numeric, errors='coerce')
            tables[table_name] = table_data
            
            # Extract parent/child header information
            headers = {}
            for i in range(1, num_cols):
                header_level = [h for h in table_data.columns.levels[i] if h]
                headers[header_level[0]] = header_level[1:]
            
            tables[table_name + '_headers'] = headers
            
            # Move to next table
            table_idx += num_rows
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
