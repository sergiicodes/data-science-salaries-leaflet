import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from geopy.geocoders import Nominatim
import dash_leaflet as dl

location = r"C:\Users\shacosta\Desktop\ds_salaries.csv"
df = pd.read_csv(location)
df.drop(['salary', 'salary_currency'], axis=1, inplace=True)

experience_level_mapping = {
    "EN": "Entry Level",
    "MI": "Mid Level",
    "SE": "Senior",
    "EX": "Executive Level"
}

df['experience_level'] = df['experience_level'].replace(experience_level_mapping)
print(df)

geolocator = Nominatim(user_agent="ds_salaries_app")

def create_map_markers(df):
    markers = []
    for _, row in df.iterrows():
        country_name, salary = row[['employee_residence', 'salary_in_usd']]
        try:
            location = geolocator.geocode(country_name, timeout=10)
            if location:
                marker = dl.Marker(position=(location.latitude, location.longitude), children=[
                    dl.Tooltip(f"{country_name}<br>Average Salary: ${salary}")
                ])
                markers.append(marker)
        except Exception as e:
            print(f"Error: {e}")
    return markers

map_style = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Data Science Salaries Dashboard"),
    dcc.Loading([
        dl.Map(id='leaflet_map', style={'width': '100%', 'height': '600px'}, center=(40, 0), zoom=2),
    ]),
    dcc.Dropdown(
        id='experience_level_dropdown',
        options=[{'label': i, 'value': i} for i in df['experience_level'].unique()],
        multi=True,
        placeholder="Select Experience Levels"
    ),
    html.Div(id='filtered_data_container')
])

import traceback

@app.callback(
    Output('leaflet_map', 'children'),
    [Input('experience_level_dropdown', 'value')]
)
def update_map(selected_experience_levels):
    try:
        if selected_experience_levels:
            filtered_df = df[df['experience_level'].isin(selected_experience_levels)]
        else:
            filtered_df = df

        markers = create_map_markers(filtered_df)
        return [
            dl.TileLayer(url=map_style, attribution="Map data © <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"),
            *markers
        ]
    except Exception as e:
        traceback.print_exc()

if __name__ == '__main__':
    app.run_server(debug=True)
