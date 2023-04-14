import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import os
from pyngrok import ngrok
import tempfile
import re
import base64
import random
import datetime
import json
from streamlit_option_menu import option_menu


def display_initial_menu(initial_menu_container):
    menu_options = ["Seleccione una tarea...", "Crear Nuevo Reporte", "Generar automáticamente"]
    user_selection = initial_menu_container.selectbox("", menu_options)
    if user_selection != "Seleccione una tarea...":
        initial_menu_container.empty()
        return user_selection
    return None

def main():
    # ...
    if "initial_menu_container" not in st.session_state:
        st.session_state.initial_menu_container = st.sidebar.empty()

    if st.session_state.user_selection is None:
        initial_menu_result = display


def initialize_and_upload():
    uploaded_file = st.sidebar.file_uploader("Upload file", type=".sav", accept_multiple_files=False)
    if uploaded_file is not None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            df = pd.read_spss(temp_file_path)
            return df
    else:
        return None

def table_chart(df, row_index, col_index_array, title, subtitle, drop_categories=None):
    df_temp = df[col_index_array + [row_index]].copy()
    if drop_categories:
        df_temp = df_temp[~df_temp[row_index].isin(drop_categories)]
    crosstab_data = pd.crosstab(index=df_temp[row_index], columns=[df_temp[col] for col in col_index_array], rownames=[row_index], colnames=col_index_array)
    crosstab_data_percent = crosstab_data.apply(lambda r: r / r.sum() * 100, axis=1).round(2)
    column_sum = crosstab_data.sum()
    crosstab_data_percent.loc['n'] = column_sum.values
    return crosstab_data_percent


def bar_chart(data, row_index, color_sequence, en_text='.2s'):
    return px.bar(data, x=row_index, y='count', color='Variable', color_discrete_sequence=color_sequence, text_auto=en_text)

def horizontal_bar_chart(data, row_index, color_sequence, en_text='.2s'):
    return px.bar(data, x='count', y=row_index, color='Variable', orientation='h', color_discrete_sequence=color_sequence, text_auto=en_text)

def multi_bar_chart(data, row_index, color_sequence,en_text='.2s'):
    chart = px.bar(data, x=row_index, y='count', barmode='group', color='Variable', color_discrete_sequence=color_sequence, text_auto=en_text)
    chart.update_traces(textposition='outside')
    return chart

def horizontal_multi_bar_chart(data, row_index, color_sequence, en_text='.2s'):
    chart = px.bar(data, x='count', y=row_index, color='Variable', orientation='h', barmode='group', color_discrete_sequence=color_sequence, text_auto=en_text)
    chart.update_traces(textposition='outside')
    return chart

def line_chart(data, row_index, color_sequence):
    return px.line(data, x=row_index, y='count', color='Variable', color_discrete_sequence=color_sequence)

def area_chart(data, row_index, color_sequence):
    return px.area(data, x=row_index, y='count', color='Variable', color_discrete_sequence=color_sequence)

def radar_chart(data, row_index, color_sequence):
    chart = px.line_polar(data, r='count', theta=row_index, color='Variable', line_close=True, color_discrete_sequence=color_sequence)
    chart.update_layout(
        showlegend=True,
        legend_title_text='Variable',
        polar_bargap=0,
        polar_radialaxis_ticksuffix='%',
    )
    return chart

def donut_chart(data, row_index, color_sequence):
    return px.pie(data, values='count', names='Variable', hole=0.5, color_discrete_sequence=color_sequence)

def pie_chart(data, row_index, color_sequence):
    return px.pie(data, values='count', names='Variable', color_discrete_sequence=color_sequence)


def live_plot(df, row_index, col_index_array, chart_type, title, subtitle, color_sequence, drop_categories=None, x_label=None, y_label=None):

    combined_col_name = ', '.join(col_index_array)
    df_temp = df[col_index_array + [row_index]].copy()
    df_temp[combined_col_name] = df_temp[col_index_array].apply(lambda row: ', '.join(row.values.astype(str)), axis=1)

    crosstab_data = pd.crosstab(index=df_temp[row_index], columns=df_temp[combined_col_name], rownames=[row_index], colnames=['Variable'])
    data_percentage = crosstab_data.apply(lambda r: r / r.sum() * 100, axis=1).reset_index()
    data = data_percentage.melt(id_vars=row_index, var_name='Variable', value_name='count')
    if drop_categories:
        data = data[~data[row_index].isin(drop_categories)]
    chart_methods = {
        'bar': bar_chart,
        'horizontal bar': horizontal_bar_chart,
        'multi bar': multi_bar_chart,
        'horizontal multi bar': horizontal_multi_bar_chart,
        'line': line_chart,
        'area': area_chart,
        'radar': radar_chart,
        'donut': donut_chart,
        'pie': pie_chart,
    }

    if chart_type in chart_methods:
        chart = chart_methods[chart_type](data, row_index, color_sequence)
        if chart_type in ['bar', 'horizontal bar','horizontal multi bar', 'multi bar', 'line', 'area']:
            chart.update_xaxes(tickangle=30)
    else:
        raise ValueError(f"Unsupported chart_type: {chart_type}")

    chart.update_layout(
        title={'text': f"{title}<br>-{subtitle}-", 'x': 0.5, 'xanchor': 'center'}
    )
    if x_label:
        chart.update_xaxes(title_text=x_label)

    if y_label:
        chart.update_yaxes(title_text=y_label)

    return chart


def customize_plot():

    chart_types = ['bar', 'horizontal bar','multi bar','horizontal multi bar', 'line', 'area', 'radar', 'donut', 'pie', 'table']
    chart_type = st.sidebar.selectbox("Select chart type:", options=chart_types)
    if chart_type == 'table':
        title = st.sidebar.text_input("Enter a title for the table:")
        subtitle = st.sidebar.text_input("Enter a subtitle for the table:")
    else:
        title = st.sidebar.text_input("Enter a title for the plot:")
        subtitle = st.sidebar.text_input("Enter a subtitle for the plot:")

    color_sequence = ["#0068c9", "#83c9ff", "#ff2b2b", "#ffabab", "#29b09d","#7defa1", "#ff8700", "#ffd16a", "#6d3fc0", "#d5dae5"]

    return chart_type, title, subtitle, color_sequence

def append_WIP_to_html(html_report, row_index, col_index_array, plot_html):
    html_report = html_report + f"<h1>{row_index} vs {' '.join(col_index_array)}</h1>"
    
    if isinstance(plot_html, pd.DataFrame):
        table_style = '''
        <style>
            table {
                border-collapse: collapse;
                width: 100%;
                font-family: Arial, sans-serif;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
            }
            th {
                background-color: #f2f2f2;
                font-weight: bold;
                text-align: left;
            }
            td {
                text-align: center;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            tr:hover {
                background-color: #ddd;
            }
        </style>
        '''
        plot_html = table_style + plot_html.to_html(index_names=False, border=0)

    html_report += plot_html
    return html_report


def save_as_template(plot_configs, report_name):
    if report_name:
        json_data = json.dumps(plot_configs)

        with open(f"{report_name}_template.json", "w") as f:
            f.write(json_data)

        st.write("Template saved successfully!")
        return json_data
    else:
        st.write('Please add report name')
        return None

def save_html_report(html_report, report_name):
    if report_name: 
        with open(f"{report_name}.html", "w") as f:
            f.write(html_report)
        report_download_link = get_download_link(report_name, html_report)  # add report_name argument here
        st.markdown(report_download_link, unsafe_allow_html=True)
    else:
        st.write('Please add report name')


def generate_html_report_from_template(df, json_data):
    plot_configs = json.loads(json_data)
    html_report = ""
    for config in plot_configs:
        row_index = config["row_index"]
        col_index_array = config["col_index_array"]
        chart_type = config["chart_type"]
        title = config["title"]
        subtitle = config["subtitle"]
        color_sequence = ["#0068c9", "#83c9ff", "#ff2b2b", "#ffabab", "#29b09d","#7defa1", "#ff8700", "#ffd16a", "#6d3fc0", "#d5dae5"]
        if chart_type == "table":
            plot_html = table_chart(df, row_index, col_index_array, title, subtitle, drop_categories=None)
            table_style = '''
            <style>
                table {
                    border-collapse: collapse;
                    width: 100%;
                    font-family: Arial, sans-serif;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                }
                th {
                    background-color: #f2f2f2;
                    font-weight: bold;
                    text-align: left;
                }
                td {
                    text-align: center;
                }
                tr:nth-child(even) {
                    background-color: #f2f2f2;
                }
                tr:hover {
                    background-color: #ddd;
                }
            </style>
            '''
            plot_html = table_style + plot_html.to_html(index_names=False, border=0)
        else:
            plot = live_plot(df, row_index, col_index_array, chart_type, title, subtitle,color_sequence)
            plot_html = plot.to_html(full_html=False, include_plotlyjs='cdn')
        html_report = append_WIP_to_html(html_report, row_index, col_index_array, plot_html)
    return html_report

def get_download_link(report_name, file_data):
    date_str = datetime.datetime.now().strftime("%d%m%Y")
    file_name = f"{report_name}_{date_str}.html"
    file_encoded = base64.b64encode(file_data.encode()).decode()
    href = f'<a href="data:file/html;base64,{file_encoded}" download="{file_name}" target="_blank">Download report</a>'
    return href

def get_json_download_link(report_name, json_data):
    date_str = datetime.datetime.now().strftime("%d%m%Y")
    file_name = f"{report_name}_{date_str}.json"
    file_encoded = base64.b64encode(json_data.encode()).decode()
    href = f'<a href="data:application/json;base64,{file_encoded}" download="{file_name}" target="_blank">Download template</a>'
    return href

#############################MAIN############################################3
def main():
    st.set_page_config(page_title="Crosstab Plotter CID App", page_icon=":bar_chart:")
    if "html_report" not in st.session_state:
        st.session_state.html_report = ""
        
    if "plot_configs" not in st.session_state:
        st.session_state.plot_configs = []

    if "user_selection" not in st.session_state:
        st.session_state.user_selection = None

    if "initial_menu_container" not in st.session_state:
        st.session_state.initial_menu_container = st.sidebar.empty()

    if st.session_state.user_selection is None:
        initial_menu_result = display_initial_menu(st.session_state.initial_menu_container)
        if initial_menu_result is not None:
            st.session_state.user_selection = initial_menu_result

    if st.session_state.user_selection == "Crear Nuevo Reporte":

        report_name = st.sidebar.text_input("Enter a name for the report:")
        df = initialize_and_upload()

        if df is not None:
            st.sidebar.write("File uploaded successfully!")
            row_index = st.sidebar.selectbox("Select categorical column for row index:",
            options=[col for col in df.columns if col.startswith("P") and col != "POND"])
            col_index_array = []
            first_p_col = next((i for i, col in enumerate(df.columns) if re.match('P\d+', col)), len(df.columns))
            pond_col = df.columns.get_loc('POND')
            possible_elements = int(first_p_col - pond_col - 1)
            num_elements = st.slider("Seleccione Niveles:",
                                     min_value=1,
                                     max_value=possible_elements,
                                     value=1)
            options_list = [col for col in df.columns[pond_col+1:first_p_col]]
            col_to_be_appended = st.multiselect(f"Seleccione Categóricos por Orden de Nivel:",
                                                options=options_list,
                                                max_selections=num_elements)
            col_index_array = col_to_be_appended
            chart_type, title, subtitle, color_sequence = customize_plot()
            drop_categories = st.multiselect("Eliminar algunas categorias:", options=df[row_index].unique())
            if chart_type == 'table':
                try:
                    table = table_chart(df, row_index, col_index_array, title, subtitle, drop_categories=drop_categories)
                    st.write(table, theme='streamlit', use_container_width=True)
                    plot_html = table
                except Exception as e:
                    st.write("Select arguments")
            else:
                x_label = st.sidebar.text_input("Enter x-axis label:")
                y_label = st.sidebar.text_input("Enter y-axis label:")
                try:
                    plot = live_plot(df, row_index, col_index_array, chart_type, title, subtitle, color_sequence, drop_categories=drop_categories, x_label=x_label, y_label=y_label)
                    st.plotly_chart(plot, theme='streamlit')
                    plot_html = plot.to_html(full_html=False, include_plotlyjs='cdn')
                except Exception as e:
                    st.write("Select arguments")

            append_to_html = st.button("Append to Report")

            save_html = st.button("Save Report")

            if append_to_html:
                current_plot_config = {
                    "row_index": row_index,
                    "col_index_array": col_index_array,
                    "chart_type": chart_type,
                    "title": title,
                    "subtitle": subtitle,
                    "color_sequence": color_sequence
                }
                st.session_state.plot_configs.append(current_plot_config)
                st.session_state.html_report = append_WIP_to_html(st.session_state.html_report, row_index, col_index_array, plot_html)
                st.write('Added successfully')

            if save_html:
                save_html_report(st.session_state.html_report, report_name)

            save_as_template_button = st.button("Save as Automation")

            if save_as_template_button:
                json_data = save_as_template(st.session_state.plot_configs, report_name)
                if json_data:
                    json_download_link = get_json_download_link(report_name, json_data)
                    st.markdown(json_download_link, unsafe_allow_html=True)
            pass

    elif st.session_state.user_selection == "Generar automáticamente":

        df = initialize_and_upload()
        report_name = st.sidebar.text_input("Enter a name for the report:")
        uploaded_template = st.file_uploader("Run Automation", type=".json", accept_multiple_files=False)

        if uploaded_template is not None and df is not None:
            template_str = uploaded_template.read().decode("utf-8")
            st.session_state.html_report = generate_html_report_from_template(df, template_str)
            report_download_link = get_download_link(report_name, st.session_state.html_report)
            st.sidebar.markdown(report_download_link, unsafe_allow_html=True)

        pass

if __name__ == "__main__":
    main()
