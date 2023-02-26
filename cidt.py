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
def extract_tables(csv):
    tables = {}
    for row_idx in range(csv.shape[0]):
        if not pd.isna(csv.iloc[row_idx, 0]):
            table_name = csv.iloc[row_idx, 0]
            n_cols = 1
            for col_idx in range(1, csv.shape[1]):
                if pd.isna(csv.iloc[row_idx, col_idx]):
                    n_cols = col_idx
                    break
            n_rows = 0
            for row_idx2 in range(row_idx+2, csv.shape[0]):
                if pd.isna(csv.iloc[row_idx2, 0]):
                    n_rows = row_idx2 - row_idx - 2
                    break
            table_data = csv.iloc[row_idx+2:row_idx+2+n_rows, :n_cols].fillna('')
            tables[table_name] = pd.DataFrame(table_data.values, columns=table_data.iloc[0], index=None).drop([0])
            tables[table_name].fillna(0, inplace=True)

            for col_idx in range(n_cols):
                if col_idx > 0:
                    level = 1
                    parent_cat = ''
                    for row_idx2 in range(row_idx+1, csv.shape[0]):
                        if pd.isna(csv.iloc[row_idx2, col_idx]):
                            break
                        cat_name = csv.iloc[row_idx2, col_idx]
                        tables[table_name][cat_name] = tables[table_name][parent_cat] - tables[table_name][cat_name]
                        parent_cat = cat_name
                        level += 1
    return tables



# Generate plot based on user selections and customizations
def generate_plot(csv_file, table_name, category_path):
    csv = pd.read_csv(csv_file, header=None)
    tables = extract_tables(csv)
    table = tables[table_name]
    category_names = [category.strip() for category in category_path.split('>')]

    # filter the table based on the selected category path
    filtered_table = table.copy()
    for i in range(len(category_names)):
        category_name = category_names[i]
        if category_name:
            level = i + 1
            if level == 1:
                filtered_table = filtered_table.loc[[name.startswith(category_name + ',') for name in filtered_table.index]]
            else:
                parent_category_name = category_names[i-1]
                parent_category_data = filtered_table.loc[parent_category_name]
                filtered_table = filtered_table.loc[[name == category_name or name.startswith(category_name + ',') for name in filtered_table.index]]
                filtered_table = filtered_table.sub(parent_category_data, axis=1)

    # plot the filtered table
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    ax.axis('tight')
    ax.table(cellText=filtered_table.values, colLabels=filtered_table.columns, rowLabels=filtered_table.index, loc='center')
    plt.show()

                      
# Run main program
if __name__ == "__main__":
    main()





