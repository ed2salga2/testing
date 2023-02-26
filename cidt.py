import pandas as pd
import matplotlib.pyplot as plt
import io
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Drive authentication
creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
drive_service = build("drive", "v3", credentials=creds)

# Main program
def main():
    # Page setup
    st.set_page_config(page_title="Contingency Plotter", page_icon=":bar_chart:", layout="wide")

    # Sidebar setup
    st.sidebar.title("Contingency Plotter")

    # Load CSV file
    st.sidebar.subheader("Load a CSV file from your Google Drive:")
    file = st.sidebar.file_uploader("Select CSV file", type="csv")
    if file is not None:
        csv = pd.read_csv(file)
        st.sidebar.success(f"File '{file.name}' loaded successfully.")

        # Extract tables
        tables = extract_tables(csv)
        selected_table = st.sidebar.selectbox("Table", list(tables.keys()))
        if selected_table:
            table = tables[selected_table]
            st.sidebar.success(f"Table '{selected_table}' loaded successfully.")

            # Filter setup
            st.sidebar.subheader("Select rows and columns to plot:")
            row_filter = st.sidebar.multiselect("Rows", table[table.columns[0]].unique(), default=[table[table.columns[0]].unique()[0]])
            col_filter = st.sidebar.multiselect("Columns", table.columns[1:], default=[table.columns[1]])

            # Create filtered table
            filtered_table = table.loc[table[table.columns[0]].isin(row_filter), col_filter]

            # Show filtered table
            st.write("Filtered table:")
            st.write(filtered_table)

            # Plot setup
            st.sidebar.subheader("Customize your plot:")
            plot_type = st.sidebar.selectbox("Plot type", ["line", "bar", "scatter", "histogram"])
            x_col = st.sidebar.selectbox("X-axis", filtered_table.columns)
            y_col = st.sidebar.selectbox("Y-axis", filtered_table.columns)
            color = st.sidebar.color_picker("Color")
            title = st.sidebar.text_input("Title", "My Custom Plot")
            xlabel = st.sidebar.text_input("X-axis label", x_col)
            ylabel = st.sidebar.text_input("Y-axis label", y_col)
            direction = st.sidebar.selectbox("Direction", ["vertical", "horizontal"])

            # Plot
            fig, ax = plt.subplots()

            if plot_type == "line":
                ax.plot(filtered_table[x_col], filtered_table[y_col], color=color)
            elif plot_type == "bar":
                ax.bar(filtered_table[x_col], filtered_table[y_col], color=color)
            elif plot_type == "scatter":
                ax.scatter(filtered_table[x_col], filtered_table[y_col], color=color)
            elif plot_type == "histogram":
                ax.hist(filtered_table[y_col], color=color)

            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)

            if direction == "horizontal":
                ax.invert_yaxis()

            # Show plot
            st.pyplot(fig)

            # Save plot
            st.sidebar.subheader("Save plot as:")
            save_location = st.sidebar.radio("Location", ("Local", "Google Drive"))
            filename = st.sidebar.text_input("File name", "plot.png")
            
            if st.sidebar.button("Save"):
                if save_location == "Local":
                    fig.savefig(filename, format="png")
                    st.sidebar.success("Plot saved successfully as '{}'.".format(filename))
                else:
                    try:
                        file_metadata = {"name": filename, "parents": [st.secrets["gdrive_folder_id"]]}
                        buffer = io.BytesIO()
                        fig.savefig(buffer, format="png")
                        media = {"mimeType": "image/png", "body": buffer.getvalue()}
                        file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
                        st.sidebar.success("Plot saved successfully to Google Drive with ID: {}".format(file.get("id")))
                    except HttpError as error:
                        st.sidebar.error("Unable to save plot to Google Drive: {}".format(error))

    # Parse CSV to extract contingency tables
import pandas as pd

import pandas as pd

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
            while num_cols < len(csv.columns) and not pd.isna(csv.iloc[table_idx + 1, num_cols]):
                num_cols += 1
            num_rows = 0
            while data_start_idx + num_rows < len(csv.index) and not pd.isna(csv.iloc[data_start_idx + num_rows, 0]):
                num_rows += 1
            
            # Extract table data
            table_data = csv.iloc[data_start_idx:data_start_idx + num_rows, :num_cols]
            table_data = table_data.set_index(table_data.columns[0])
            table_data.index.name = None
            table_data.columns.name = None
            table_data = table_data.apply(pd.to_numeric, errors='ignore')
            tables[table_name] = table_data

            # Extract parent/child header information
            headers = {}
            parent_headers = list(table_data.columns)
            child_headers = list(reduce(lambda x, y: x + y, pd.crosstab(index=table_data.index, columns=[table_data[c] for c in parent_headers]).columns))
            for parent in parent_headers:
                child_start_idx = parent_headers.index(parent) * len(table_data.index)
                child_end_idx = child_start_idx + len(table_data.index)
                headers[parent] = child_headers[child_start_idx:child_end_idx]

            tables[table_name + '_headers'] = headers

            # Move to next table
            table_idx = data_start_idx + num_rows
        else:
            table_idx += 1
            
    return tables


# Generate plot based on user selections and customizations
def generate_plot(table, x_col, y_col):
    fig, ax = plt.subplots()
    table.plot(kind='bar', x=x_col, y=y_col, ax=ax)
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    st.pyplot(fig)

# Load CSV file
csv_file = st.file_uploader("Upload CSV file", type=['csv'])
if csv_file is not None:
    csv = pd.read_csv(csv_file)
    tables = extract_tables(csv)

    # Prompt user to select table
    table_name = st.selectbox("Select table", list(tables.keys()))

    # Prompt user to select parent and child headers
    parent_header = st.selectbox("Select parent header", list(tables[table_name + '_headers'].keys()))
    child_header = st.selectbox("Select child header", tables[table_name + '_headers'][parent_header])

    # Filter data
    data = tables[table_name].loc[:, [parent_header, child_header]]
    data = data.groupby([parent_header, child_header]).size().reset_index(name='count')

    # Generate plot
    generate_plot(data, parent_header, 'count')

                      
# Run main program
if __name__ == "__main__":
    main()





