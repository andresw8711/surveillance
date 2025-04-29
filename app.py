import dash
from dash import dcc, html, Input, Output
import dash_cytoscape as cyto

# Inicializar app
app = dash.Dash(__name__)
app.title = "Surveillance Petrolero"

# Queries clave
queries = {
    "ETL_SQL": """
-- Opción 1: Agrupación en SQL (ETL)
SELECT 
    campo, patron, estructura, pozo,
    AVG(presion) AS avg_presion,
    SUM(produccion) AS prod_total
FROM 
    tabla_pozos
GROUP BY 
    campo, patron, estructura, pozo;
""",
    "ELT_CDF": """
-- Opción 2: Transformación en CDF (ELT)
-- Paso 1: Cargar datos crudos a CDF
-- Paso 2: Usar Cognite Functions para:
SELECT 
    asset.externalId AS pozo_id,
    ts.avg(presion) AS avg_presion
FROM 
    timeseries ts
JOIN 
    assets asset ON ts.asset_id = asset.id
WHERE 
    asset.parent = 'Estructura_X';
"""
}

# Elementos del diagrama de flujo
flow_elements = [
    # Opción 1
    {"data": {"id": "etl", "label": "SierraCol (DB - SQL)"}, "position": {"x": 50, "y": 100}},
    {"data": {"id": "grp", "label": "Datos Agrupados (YAML)"}, "position": {"x": 250, "y": 100}},
    {"data": {"id": "cdf", "label": "CDF: Assets TF"}, "position": {"x": 450, "y": 100}},
    {"data": {"id": "app", "label": "Aplicativo (SDK, GraphQL)"}, "position": {"x": 650, "y": 100}},

    # Opción 2
    {"data": {"id": "cd", "label": "CDF: Raw (Datos Maestros)"}, "position": {"x": 50, "y": 250}},
    {"data": {"id": "ass", "label": "CDF: Relaciones (MJ)"}, "position": {"x": 250, "y": 250}},
    {"data": {"id": "rel", "label": "CDF: Assets TF"}, "position": {"x": 450, "y": 250}},
    {"data": {"id": "gql", "label": "Aplicativo (SDK, GraphQL)  "}, "position": {"x": 650, "y": 250}},

    # Flechas opción 1
    {"data": {"source": "etl", "target": "grp"}},
    {"data": {"source": "grp", "target": "cdf"}},
    {"data": {"source": "cdf", "target": "app"}},

    # Flechas opción 2
    {"data": {"source": "cd", "target": "ass"}},
    {"data": {"source": "ass", "target": "rel"}},
    {"data": {"source": "rel", "target": "gql"}},
]   

cyto_stylesheet = [
    {"selector": "node", "style": {
        "label": "data(label)",
        "text-valign": "center",
        "color": "white",
        "background-color": "#0074D9",
        "width": "180px",
        "height": "60px",
        "font-size": "14px",
        "border-width": "2px",
        "border-color": "#333",
        "shape": "roundrectangle"
    }},
    {"selector": "edge", "style": {
        "curve-style": "bezier",
        "target-arrow-shape": "triangle",
        "target-arrow-color": "#555",
        "line-color": "#aaa",
        "width": 2
    }}
]

# Layout
app.layout = html.Div([
    html.H1("Flujo de Datos: Surveillance Petrolero", style={"textAlign": "center"}),

    # Diagrama de flujo
    cyto.Cytoscape(
        id="flujo-datos",
        layout={"name": "preset"},
        style={"width": "100%", "height": "300px"},
        elements=flow_elements,
        stylesheet=cyto_stylesheet
    ),

    # Selector de opción
    html.Div([
        dcc.RadioItems(
            id="opcion-selector",
            options=[
                {"label": "Opción 1: ETL (Procesar en SQL)", "value": "ETL_SQL"},
                {"label": "Opción 2: ELT (Procesar en CDF)", "value": "ELT_CDF"}
            ],
            value="ETL_SQL",
            style={"margin": "20px"}
        )
    ], style={"textAlign": "center"}),

    # Consulta mostrada
    html.Div([
        html.H3("Query Clave", style={"color": "#34495e"}),
        dcc.Markdown(
            id="query-output",
            style={
                "backgroundColor": "#272822",
                "padding": "15px",
                "borderRadius": "5px",
                "overflow": "auto",
                "color": "white",
                "fontFamily": "monospace"
            }
        )
    ], style={"width": "80%", "margin": "0 auto"})
])

# Callback para mostrar la query
@app.callback(
    Output("query-output", "children"),
    Input("opcion-selector", "value")
)
def update_query(opcion):
    return f"```sql\n{queries[opcion]}\n```"

# Ejecutar
if __name__ == "__main__":
    app.run(debug=True, port=8050)