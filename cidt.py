import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def extract_tables(csv):
    tables = {}
    table_names = set(csv.iloc[:, 0].values)
    for table_name in table_names:
        if not pd.isna(table_name):
            table_data = pd.crosstab(index=csv.iloc[:, 0], columns=csv.iloc[:, 1:], dropna=False)
            table_data = table_data.loc[table_name].reset_index().melt(id_vars=[table_name])
            table_data.columns = ['Category', 'Value']
            tables[table_name] = table_data
            parent_headers = list(table_data['Category'].unique())
            child_headers = list(table_data['Value'].unique())
            headers = {parent: [child for child in child_headers if child.startswith(parent)] for parent in parent_headers}
            tables[table_name + '_headers'] = headers
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
