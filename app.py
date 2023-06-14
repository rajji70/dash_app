import io
import base64
# import dash
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output


app = Dash(__name__)
app.config.suppress_callback_exceptions = True

# Global variable to store the Excel data
excel_data = None

# CSS styles
styles = {
    'container': {
        'width': '80%',
        'margin': '0 auto',
        'padding': '20px',
        'fontFamily': 'Arial, sans-serif',
        'border': '2px solid black',  # Outline box
        'backgroundColor': '#f7f7f7',  # Background color
        'color': 'black'  # Text color
    },
    'center': {
        'display': 'flex',
        'justify-content': 'center',
        'align-items': 'center'
    },
    'upload-data': {
        'width': '70%',
        'height': '120px',
        'lineHeight': '120px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin': '10px'
    },
    'dropdown': {
        'width': '200px',
        'marginRight': '10px',
        'backgroundColor': 'white',
        'color': 'black'
    },
    'graph-display': {
        'backgroundColor': 'white',
        'padding': '20px',
        'border': '2px solid #f7f7f7',
        'borderRadius': '5px'
    },
    'graph-title': {
        'fontFamily': 'Arial, sans-serif',
        'color': '#283747',
        'textAlign': 'center',
        'marginBottom': '20px'
    }
}

app.layout = html.Div(style=styles['container'], children=[
    html.H1('Data Visualization Dashboard', style={'textAlign': 'center'}),
    html.H2("Aban offshore", style={'textAlign': 'center'}),
    html.Div(
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style=styles['upload-data']
        ),
        style=styles['center']
    ),
    html.Div(id='output-data-upload', style=styles['center']),     
    html.Label('Graphs', style={'fontSize': '18px', 'marginBottom': '10px'}),
    html.Div([
        dcc.Dropdown(
            options=[
                {'label': 'Line', 'value': 'line'},
                {'label': 'Scatter', 'value': 'scatter'},
                {'label': 'Bar', 'value': 'bar'},
                {'label': 'Area', 'value': 'area'},
                {'label': 'Box', 'value': 'box'},
                {'label': 'Histogram', 'value': 'histogram'}
            ],
            value=['line'],
            multi=True,
            id='graph-options',
            style=styles['dropdown']
        )
    ]),
    html.Div(id='graph-dropdown'),
    html.Label('Indicators', style={'fontSize': '18px', 'marginBottom': '10px'}),
    html.Div(id='indi', children=[
        dcc.Dropdown(
            options=[],
            value=None,
            multi=True,
            id='indicator-dropdown-2',  # Updated ID to resolve conflict
            style=styles['dropdown']
        )
    ]),
    html.Div(id='graphs'),
    html.Div(id='graph-display', style=styles['graph-display'])
])


@app.callback(
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    Input('upload-data', 'filename')
)
def store_excel_data(contents, filename):
    global excel_data

    if contents:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        try:
            # Read the Excel sheet and store it in the global variable
            excel_data = pd.read_excel(io.BytesIO(decoded))
            return f"File {filename} uploaded successfully!"
        except Exception as e:
            return f"Error reading {filename}: {str(e)}"

    return "No file uploaded."


@app.callback(
    Output('graph-dropdown', 'children'),
    Input('graph-options', 'value')
)
def update_graph_dropdown(value):
    return html.Div(value)


@app.callback(
    Output('indicator-dropdown-2', 'options'),  # Updated ID to match the component
    Output('indicator-dropdown-2', 'value'),  # Updated ID to match the component
    Input('output-data-upload', 'children')
)
def update_indicators_dropdown(upload_message):
    if excel_data is None:
        return [], None

    options = []
    keys = excel_data.columns.tolist()

    for index, key in enumerate(keys[1:], start=1):
        options.append({'label': key, 'value': key})

    return options, []  # Return updated options and reset the value


@app.callback(
    Output('graph-display', 'children'),
    Input('graph-options', 'value'),
    Input('output-data-upload', 'children'),
    Input('indicator-dropdown-2', 'value')  # Updated ID to match the component
)
def update_graph(gTypes, upload_message, mTypes):
    if excel_data is None:
        return html.Div("No file uploaded.")

    if not mTypes:
        return html.Div(
            children=[
                html.H3(
                    children='No indicators selected!',
                    style={
                        'fontFamily': 'Helvetica',
                        'color': '#283747',
                        'textAlign': 'center',
                        'marginTop': '50px'
                    }
                )
            ]
        )

    dt = excel_data
    ti = dt.columns[0]

    fig = go.Figure()

    for mType in mTypes:
        for gType in gTypes:
            if gType == 'line':
                fig.add_trace(go.Scatter(x=dt[ti], y=dt[mType], mode='lines', name=f'Line - {mType}'))
            elif gType == 'scatter':
                fig.add_trace(go.Scatter(x=dt[ti], y=dt[mType], mode='markers', name=f'Scatter - {mType}'))
            elif gType == 'bar':
                fig.add_trace(go.Bar(x=dt[ti], y=dt[mType], name=f'Bar - {mType}'))
            elif gType == 'area':
                fig.add_trace(go.Scatter(x=dt[ti], y=dt[mType], fill='tozeroy', name=f'Area - {mType}'))
            elif gType == 'box':
                fig.add_trace(go.Box(x=dt[ti], y=dt[mType], name=f'Box - {mType}'))
            elif gType == 'histogram':
                fig.add_trace(go.Histogram(x=dt[mType], name=f'Histogram - {mType}'))

    fig.update_layout(
        title='Data Visualization',
        xaxis_title=ti,
        yaxis_title='Values',
        template='plotly_dark'
    )

    return dcc.Graph(figure=fig)


if __name__ == '__main__':
    app.run_server(debug=True)
