from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objects as go
import networkx as nx
from application.logging_tree import get_graph

from django_plotly_dash import DjangoDash

# יצירת אפליקציית Dash בתוך Django
app = DjangoDash('ProcessingFlowDashboard')  # שם ייחודי לאפליקציה

# פונקציה ליצירת גרף ויזואלי
def create_fig(G):
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    node_x = []
    node_y = []
    text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_info = f"{node}<br>{G.nodes[node]['timestamp']}<br>{G.nodes[node]['level']}"
        text.append(node_info)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=[node for node in G.nodes()],
        textposition="bottom center",
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color='lightblue',
            size=20,
            line_width=2
        )
    )
    
    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='<br>SEC Filings Processing Flow',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=[dict(
                    text="",
                    showarrow=False,
                    xref="paper", yref="paper")],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
    
    return fig

# הגדרת layout של האפליקציה
app.layout = html.Div([ # type: ignore
    html.H1("SEC Filings Processing Dashboard"),
    dcc.Graph(id='processing-flow-graph'),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # עדכון כל 5 שניות
        n_intervals=0
    )
])

# callback לעדכון הגרף
@app.callback(
    Output('processing-flow-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph_live(n):
    G = get_graph()
    fig = create_fig(G)
    return fig