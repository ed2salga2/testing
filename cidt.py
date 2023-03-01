import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# Function to read .sav file with pd.read_spss()
def read_sav_file(file_path):
    df = pd.read_spss(file_path)
    return df

# Function to create crosstab and plot it
def create_crosstab(df, col_name, row_name, chart_type, chart_args):
    crosstab_df = pd.crosstab(df[row_name], df[col_name])
    if chart_type == 'bar':
        fig = px.bar(crosstab_df)
    elif chart_type == 'line':
        fig = px.line(crosstab_df)
    elif chart_type == 'scatter':
        fig = px.scatter(crosstab_df)
    else:
        fig = go.Figure()
    fig.update_layout(**chart_args)
    st.plotly_chart(fig)

# Function to save plot as png and update job JSON
def save_plot_and_update_job(job, df, col_name, row_name, chart_type, chart_args):
    plot_name = f"{col_name}.png"
    plot_path = os.path.join(os.path.dirname(df), plot_name)
    create_crosstab(df, col_name, row_name, chart_type, chart_args)
    fig = go.Figure()
    fig.write_image(plot_path)
    plot_params = {
        "name": f"#{col_name}",
        "filter_params": {
            "col_name": col_name,
            "row_name": row_name,
            "chart_type": chart_type,
            "chart_args": chart_args
        }
    }
    job['tables'].append(plot_params)
    return job

# Function to create job JSON and save it
def create_job(job_name, job):
    job_path = os.path.join(os.getcwd(), "jobs", f"{job_name}.json")
    with open(job_path, "w") as outfile:
        json.dump(job, outfile)
    st.success("Job created successfully!")

# Function to generate the report HTML and close the current job
def finish_job(job_name, job):
    job_path = os.path.join(os.getcwd(), "jobs", f"{job_name}.json")
    with open(job_path, "w") as outfile:
        json.dump(job, outfile)
    report_path = os.path.join(os.path.dirname(job_path), f"{job_name}.html")
    report_content = "<html><head></head><body>"
    for table in job['tables']:
        col_name = table['filter_params']['col_name']
        plot_name = f"{col_name}.png"
        plot_path = os.path.join(os.path.dirname(job_path), plot_name)
        report_content += f"<h3>{table['name']}</h3>"
        report_content += f"<img src='{plot_path}'><br>"
    report_content += "</body></html>"
    with open(report_path, "w") as outfile:
        outfile.write(report_content)
    st.success("Job finished and report generated!")
    return {"name": "", "tables": []}

# App code
def main():
    # Initialize app
    st.set_page_config(page_title="Crosstab Plotter", page_icon="📊")
    st.title("Crosstab Plotter")
    job = {"name": "", "tables": []}

    # Upload file and read sav file with pd.read_spss()
    file_uploaded = st.file_uploader("Upload a .sav file", type="sav")
    if file_uploaded is not None:
        df = read_sav_file(file_uploaded)

        # Run job
        if st.button("Run Job"):
            # TODO: Implement code to run all plots based on uploaded file and previously saved JOB JSON files
            pass

        # Display LIVE VISUALIZATION PREVIEW based on the crosstab arguments inputted by user
        st.subheader("Live Visualization Preview")

        # Select categorical column for row indexes
        cat_cols = [col for col in df.columns if col.startswith("P")]
        selected_col = st.selectbox("Select a categorical column for row indexes", cat_cols)

        # Input amount of elements for column array
        amount_elements = len(df.columns) - df.columns.get_loc(selected_col) - 1
        input_elements = st.number_input(f"Input the amount of elements (up to {amount_elements}) for the column array", min_value=1, max_value=amount_elements, value=1)

        # Define order of categorical columns for input column array
        input_cols = []
        for i in range(input_elements):
            input_col = st.selectbox(f"Select column {i+1} for the input column array", cat_cols)
            input_cols.append(input_col)

        # Customize live preview with plotly arguments
        chart_type = st.selectbox("Select chart type", ["bar", "line", "scatter"])
        chart_args = {}
        chart_args['title'] = st.text_input("Title", value=f"{selected_col}")
        chart_args['xaxis_title'] = st.text_input("X-axis Title", value=f"{input_cols}")
        chart_args['yaxis_title'] = st.text_input("Y-axis Title", value="Count")
        chart_args['legend_title'] = st.text_input("Legend Title", value=f"{selected_col}")
        chart_args['color_discrete_sequence'] = px.colors.qualitative.Dark24
        chart_args['template'] = "simple_white"
        chart_args['showlegend'] = True
        chart_args['barmode'] = 'stack'

        # Generate plot and save it as png
        if st.button("Generate"):
            job_append = st.checkbox("Append parameters to JOB?")
            if job_append:
                job = save_plot_and_update_job(job, df, selected_col, input_cols, chart_type, chart_args)
            else:
                job = {"name": "", "tables": []}
                job = save_plot_and_update_job(job, df, selected_col, input_cols, chart_type, chart_args)
            st.success(f"Plot {selected_col} generated and saved successfully!")
            plot_path = os.path.join(os.path.dirname(file_uploaded.name), f"{selected_col}.png")
            st.image(plot_path)

        # Finish job and generate report
        if st.button("Finish Job"):
            job_name = st.text_input("Enter job name")
            job = finish_job(job_name, job)

    # Create job
    if st.button("Create Job"):
        job_name = st.text_input("Enter job name")
        create_job(job_name, job)

if __name__ == "__main__":
    main()

