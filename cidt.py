import streamlit as st
import pandas as pd
import altair as alt
import json
import argparse


def initialize_and_upload():
    uploaded_file = st.file_uploader("Upload file", type=".sav")
    if uploaded_file is not None:
        df = pd.read_spss(uploaded_file)
        job = {"name": "", "tables": []}
        return df, job
    else:
        return None, None


def save_job(job):
    name = st.text_input("Enter job name:")
    if name != "":
        with open(os.path.join("jobs", "jobs.json"), "a") as f:
            job["name"] = name
            json.dump(job, f)
            f.write('\n')
        st.write("Job saved successfully!")
        return True
    else:
        return False


def generate_plot(df, job, col_name, num_elements, col_order, altair_args):
    col_values = df[col_name].value_counts().index.tolist()
    if len(col_values) <= num_elements:
        col_array = col_values
    else:
        col_array = col_values[:num_elements]

    table_name = f"#{col_name}={col_array}"
    job["tables"].append({"name": table_name, "filter_params": [col_name, num_elements, col_order, altair_args]})
    crosstab_df = pd.crosstab(df[col_name], df[col_order])[col_array].T
    chart = alt.Chart(crosstab_df).mark_bar().encode(x=alt.X(col_order, sort=None), y=alt.Y(title=col_name, axis=alt.Axis(labelOverlap=True)))
    chart = chart.configure_title(fontSize=20).configure_axis(labelFontSize=16, titleFontSize=18)
    chart = chart.configure_legend(labelFontSize=16, titleFontSize=18)
    chart = eval(altair_args, {"alt": alt, "chart": chart})
    st.altair_chart(chart, use_container_width=True)
    st.write(table_name)
    st.write(crosstab_df)
    return job


def main():
        st.set_page_config(page_title="Crosstab Plotter App", page_icon=":bar_chart:")

        if "jobs" not in os.listdir():
            os.mkdir("jobs")
            with open(os.path.join("jobs", "jobs.json"), "a") as f:
                f.write("[]\n")

        df, job = initialize_and_upload()

        if df is not None:
            st.write("File uploaded successfully!")
            st.write("Sample data:")
            st.write(df.head())

            if st.button("Run job"):
                for table in job["tables"]:
                    generate_plot(df, job, *table["filter_params"])

            else:
                col_name = st.selectbox("Select categorical column for row index:", options=df.columns)
                num_elements = st.slider("Select number of elements for column array:", 1, len(df.columns) - df.columns.get_loc(col_name) - 1, 2)
                col_order = st.selectbox("Select categorical column for column index:", options=df.columns[df.columns.get_loc(col_name) + 1:])
                altair_args = st.text_input("Enter Altair chart configuration arguments:", value='').strip()

                job = generate_plot(df, job, col_name, num_elements, col_order, altair_args)

                if st.button("Generate"):
                    save_job(job)

                if st.button("Finish job"):
                    if save_job(job):
                        st.write("Job finished successfully!")
                        st.write("Generating report...")

                        html = "<h1>Job Report</h1>"
                        for table in job["tables"]:
                            col_name = table["filter_params"][0]
                            col_array = table["name"].split("=")[1][1:-1].split(", ")
                            col_order = table["filter_params"][2]
                            altair_args = table["filter_params"][3]

                            col_values = df[col_name].value_counts().index.tolist()
                            if len(col_values) <= len(col_array):
                                col_array = col_values

                            crosstab_df = pd.crosstab(df[col_name], df[col_order])[col_array].T
                            chart = alt.Chart(crosstab_df).mark_bar().encode(x=alt.X(col_order, sort=None), y=alt.Y(title=col_name, axis=alt.Axis(labelOverlap=True)))
                            chart = chart.configure_title(fontSize=20).configure_axis(labelFontSize=16, titleFontSize=18)
                            chart = chart.configure_legend(labelFontSize=16, titleFontSize=18)
                            chart = eval(altair_args, {"alt": alt, "chart": chart})
                            chart_html = chart.to_html(full_html=False, include_plotlyjs="cdn")
                            table_html = crosstab_df.to_html()
                            html += f"<h2>{table['name']}</h2>"
                            html += f"{chart_html}"
                            html += f"{table_html}"

                        report_path = os.path.join("jobs", f"{job['name']}.html")
                        with open(report_path, "w") as f:
                            f.write(html)

                        st.write("Report generated successfully!")
                        st.stop()
if __name__ == "__main__":
    main()