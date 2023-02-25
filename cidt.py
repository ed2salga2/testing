!pip install pandas
!pip install matplotlib
!pip install io
!pip install streamlit
!pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

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

# Read CSV file from Google Drive
def read_csv_file(file_id):
    file = drive_service.files().get(fileId=file_id).execute()
    filename = file.get("name")
    content = drive_service.files().get_media(fileId=file_id).execute()
    csv = pd.read_csv(io.BytesIO(content))
    return csv, filename

# Parse CSV to extract contingency tables
def extract_tables(csv):
    tables = {}
    for col in csv.columns:
        if csv[col].iloc[0] == 'Class: Question':
            question = csv[col].iloc[1]
            tables[question] = csv.iloc[:, csv.columns.get_loc(col):].dropna(how='all')
            tables[question].columns = tables[question].iloc[0]
            tables[question] = tables[question].iloc[1:]
    return tables

# Generate plot based on user selections and customizations
def generate_plot(table, x_col, y_cols, plot_type, colors, title, subtitle, direction, x_label, y_label, x_tick_labels, y_tick_labels, grid, legend, style):
    fig, ax = plt.subplots()
    if plot_type == "bar":
        table.plot(x=x_col, y=y_cols, kind=plot_type, color=colors, ax=ax)
    else:
        table.plot(x=x_col, y=y_cols, kind=plot_type, color=colors, ax=ax, legend=False)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xticklabels(x_tick_labels)
    ax.set_yticklabels(y_tick_labels)
    if subtitle:
        ax.text(0.5, 1.08, subtitle, horizontalalignment='center', transform=ax.transAxes, fontsize=12)
    if grid:
        ax.grid(True)
    if legend:
        ax.legend(legend)
    if style:
        plt.style.use(style)
    if direction == "horizontal":
        ax.invert_yaxis()
    return fig

# Main program
def main():
    # Page setup
    st.set_page_config(page_title="Contingency Plotter", page_icon=":bar_chart:", layout="wide")

    # Sidebar setup
    st.sidebar.title("Contingency Plotter")
    st.sidebar.subheader("Select a CSV file from your Google Drive:")
    file_id = st.sidebar.text_input("File ID")
    if file_id:
        try:
            csv, filename = read_csv_file(file_id)
            st.sidebar.success(f"File '{filename}' loaded successfully.")
        except HttpError:
            st.sidebar.error("Invalid file ID. Please try again.")
    st.sidebar.subheader("Select a contingency table to plot:")
    if file_id:
        tables = extract_tables(csv)
        selected_table = st.sidebar.selectbox("Table", list(tables.keys()))
        if selected_table:
            table = tables[selected_table]
            st.sidebar.success(f"Table '{selected_table}' loaded successfully.")

            # Filter setup
            st.sidebar.subheader("Select rows and columns to plot:")
            row_filter = st.sidebar.multiselect("Rows", table.columns[0], default=[table.columns[0]])
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
            
def save_plot(fig):
    st.sidebar.subheader("Save plot as:")
    save_location = st.sidebar.radio("Location", ("Local", "Google Drive"))
    filename = st.sidebar.text_input("File name", "plot.png")

    if save_location == "Local":
        fig.savefig(filename, format='png')
        st.write("File saved locally as:", filename)
    else:
        try:
            # Save plot as PNG to Google Drive
            file_metadata = {"name": filename, "parents": [st.secrets["gdrive_folder_id"]]}
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png')
            media = {"mimeType": "image/png", "body": buffer.getvalue()}
            file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            st.write("File saved to Google Drive with ID:", file.get("id"))
        except:
            st.write("Unable to save file to Google Drive. Check your credentials or try again later.")


