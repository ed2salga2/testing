import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def main():
    csv_file = st.file_uploader('Upload CSV', type=['csv'])
    if csv_file is not None:
        csv = pd.read_csv(csv_file,header=None)

        # Split the CSV by blank rows
        tables_csv = [g for _, g in csv.groupby((csv.isnull() | (csv == '')).all(1))]

        # Loop through each table in the CSV
        for table_csv in tables_csv:
            table_name = table_csv.iloc[0, 2]  # extract table name from the second column of the first row

            # Extract the data portion of the table
            data_start_idx = 0
            for idx, row in table_csv.iterrows():
                if row.isna().all():
                    data_start_idx = idx + 1
                    break
            table_data = table_csv.iloc[data_start_idx:, :]

            # Reshape the data into a format suitable for plotting
            table_data = pd.melt(table_data, id_vars=[table_data.columns[0]], value_vars=table_data.columns[1:])

            # Generate the plot
            fig, ax = plt.subplots()
            pd.crosstab(table_data[table_data.columns[1]], table_data[table_data.columns[0]], values=table_data[table_data.columns[2]], aggfunc='sum').plot(kind='bar', ax=ax)
            ax.set_title(table_name)
            ax.set_xlabel(table_data.columns[0])
            ax.set_ylabel(table_data.columns[2])
            st.pyplot(fig)

if __name__ == '__main__':
    main()
