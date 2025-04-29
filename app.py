from dash import Dash, dcc, html, Input, Output
import dash_cytoscape as cyto

app = Dash(__name__)
app.title = "Surveillance Petrolero"

# Queries
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

# Elementos por opción
def get_flow_elements(option):
    if option == "ETL_SQL":
        return [
            {"data": {
                "id": "etl",
                "label": "SierraCol (DB - SQL)",
                "title": "Base de datos SQL (Oracle, SQL Server) donde se almacenan los datos crudos de los pozos."
            }, "position": {"x": 50, "y": 150}},
            
            {"data": {
                "id": "grp",
                "label": "Datos Agrupados (YAML)",
                "title": "Querys en YAML que agrupan y preprocesan los datos antes de enviarlos a CDF."
            }, "position": {"x": 300, "y": 150}},
            
            {"data": {
                "id": "cdf",
                "label": "CDF: Raw (Assets, Timeseries...)",
                "title": "Datos preprocesados almacenados directamente en CDF como Timeseries y Assets."
            }, "position": {"x": 550, "y": 150}},

           {"data": {
                "id": "rel",
                "label": "CDF: (Transformacion)",
                "title": "Transformaciones aplicadas directamente dentro de CDF sobre los datos preprocesados."
            }, "position": {"x": 800, "y": 150}},

            {"data": {
                "id": "app",
                "label": "Aplicativo (SDK, GraphQL)",
                "title": "Aplicación que accede a los datos procesados mediante SDK o GraphQL API."
            }, "position": {"x": 1050, "y": 150}},
            
            {"data": {
                "id": "title",
                "label": "🔷 Flujo ETL - SQL"
            }, "position": {"x": 475, "y": 50}, "classes": "title"},

            {"data": {"source": "etl", "target": "grp"}},
            {"data": {"source": "grp", "target": "cdf"}},
            {"data": {"source": "cdf", "target": "rel"}},            
            {"data": {"source": "cdf", "target": "app"}}
        ]
    else:
        return [
            {"data": {
                "id": "cd",
                "label": "CDF: Raw (Assets, Timeseries...)",
                "title": "Datos crudos de los pozos almacenados directamente en CDF como Timeseries y Assets."
            }, "position": {"x": 100, "y": 350}},
            
            {"data": {
                "id": "ass",
                "label": "CDF: Relaciones",
                "title": "Relaciones jerárquicas entre los Assets, gestionadas en el diccionario de CDF."
            }, "position": {"x": 350, "y": 350}},
            
            {"data": {
                "id": "rel",
                "label": "CDF: (Transformacion)",
                "title": "Transformaciones aplicadas directamente dentro de CDF sobre los datos relacionados."
            }, "position": {"x": 600, "y": 350}},
            
            {"data": {
                "id": "gql",
                "label": "Aplicativo (SDK, GraphQL)",
                "title": "Aplicación que consulta los datos procesados desde CDF usando el SDK o GraphQL."
            }, "position": {"x": 850, "y": 350}},
            
            {"data": {
                "id": "title",
                "label": "🟢 Flujo ELT - CDF"
            }, "position": {"x": 475, "y": 270}, "classes": "title"},

            {"data": {"source": "cd", "target": "ass"}},
            {"data": {"source": "ass", "target": "rel"}},
            {"data": {"source": "rel", "target": "gql"}}
        ]


cyto_stylesheet = [
    {"selector": "node", "style": {
        "label": "data(label)",
        "text-valign": "center",
        "text-halign": "center",
        "color": "white",
        "background-color": "#0074D9",
        "width": "220px",  # Aumentado
        "height": "80px",  # Aumentado
        "font-size": "14px",
        "border-width": "2px",
        "border-color": "#333",
        "shape": "roundrectangle",
        "text-wrap": "wrap",  # Habilita el salto de línea
        "text-max-width": "200px"  # Máximo ancho antes de hacer wrap
    }},
        {"selector": ".title", "style": {
        "background-color": "#f0f0f0",
        "color": "#2c3e50",
        "font-weight": "bold",
        "border-color": "#ccc",
        "font-size": "16px",
        "width": "240px",
        "height": "40px",
        "text-valign": "center",
        "text-halign": "center",
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

# Layout general
app.layout = html.Div([
    html.H1("Flujo de Datos: Surveillance Petrolero", style={"textAlign": "center"}),

    html.Div([
        dcc.RadioItems(
            id="opcion-selector",
            options=[
                {"label": "Opción 1: ETL (Procesar en SQL)", "value": "ETL_SQL"},
                {"label": "Opción 2: ELT (Procesar en CDF)", "value": "ELT_CDF"}
            ],
            value="ETL_SQL",
            labelStyle={'display': 'inline-block', 'marginRight': '20px'},
            style={"textAlign": "center", "margin": "20px"}
        )
    ]),

    # Contenedor para el tooltip
    html.Div(id="tooltip-container", style={"position": "absolute", "background-color": "rgba(0, 0, 0, 0.75)", "color": "white", "padding": "5px", "border-radius": "5px", "display": "none"}),

    cyto.Cytoscape(
        id="flujo-datos",
        layout={"name": "preset"},
        style={"width": "100%", "height": "200px"},
        elements=get_flow_elements("ETL_SQL"),
        stylesheet=cyto_stylesheet
    ),

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

# Callbacks
@app.callback(
    [Output("query-output", "children"),
     Output("flujo-datos", "elements"),
     Output("tooltip-container", "style"),
     Output("tooltip-container", "children")],
    [Input("opcion-selector", "value"),
     Input("flujo-datos", "mouseoverNodeData"),
     Input("flujo-datos", "mouseoutNodeData")]
)   
def update_content(opcion, mouseover_node, mouseout_node):
    query = f"```sql\n{queries[opcion]}\n```"
    elements = get_flow_elements(opcion)

    # Mostrar tooltip
    tooltip_style = {"display": "none"}
    tooltip_text = ""
    if mouseover_node:
        tooltip_text = mouseover_node.get("title", "")
        tooltip_style = {"position": "absolute", "background-color": "rgba(0, 0, 0, 0.75)", "color": "white", "padding": "5px", "border-radius": "5px", "top": "100px", "left": "50px"}

    return query, elements, tooltip_style, tooltip_text

# Run app
if __name__ == "__main__":
    app.run(debug=True, port=8050)
