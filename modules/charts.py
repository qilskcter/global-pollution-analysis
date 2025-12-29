import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def apply_adaptive_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50, b=50, l=20, r=20)
    )
    return fig

GAUGE_CFG = {
    "AQI": {
        "col": "AQI Value",
        "max": 500,
        "steps": [
            {'range': [0, 50], 'color': "#00e400"},
            {'range': [50, 100], 'color': "#ffff00"},
            {'range': [100, 150], 'color': "#ff7e00"},
            {'range': [150, 200], 'color': "#ff0000"},
            {'range': [200, 300], 'color': "#8f3f97"},
            {'range': [300, 500], 'color': "#7e0023"}
        ]
    },
    "CO": {
        "col": "CO AQI Value",
        "max": 200,
        "steps": [
            {'range': [0, 40], 'color': "#27ae60"},
            {'range': [40, 100], 'color': "#f1c40f"},
            {'range': [100, 200], 'color': "#e74c3c"}
        ]
    },
    "NO2": {
        "col": "NO2 AQI Value",
        "max": 50,
        "steps": [
            {'range': [0, 9], 'color': "#27ae60"},
            {'range': [9, 30], 'color': "#f1c40f"},
            {'range': [30, 50], 'color': "#e74c3c"}
        ]
    },
    "Ozone": {
        "col": "Ozone AQI Value",
        "max": 200,
        "steps": [
            {'range': [0, 60], 'color': "#27ae60"},
            {'range': [60, 120], 'color': "#f1c40f"},
            {'range': [120, 200], 'color': "#e74c3c"}
        ]
    },
    "PM2.5": {
        "col": "PM2.5 AQI Value",
        "max": 150,
        "steps": [
            {'range': [0, 15], 'color': "#27ae60"},
            {'range': [15, 50], 'color': "#f1c40f"},
            {'range': [50, 150], 'color': "#e74c3c"}
        ]
    }
}

def create_gauge(title, value, avg, max_val, steps):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        delta={'reference': avg},
        title={'text': title},
        gauge={
            'axis': {'range': [0, max_val]},
            'bar': {'color': "gray"},
            'steps': steps
        }
    ))

    fig.update_layout(height=260)  
    return apply_adaptive_theme(fig)

def create_main_map(df, scope, colorscale):
    fig = px.scatter_geo(
        df, locations="Country", locationmode='country names', 
        color="AQI Value", size="AQI Value", hover_name="City",
        custom_data=["City", "Country", "AQI Value", "CO AQI Value", "Ozone AQI Value", "NO2 AQI Value", "PM2.5 AQI Value"],
        range_color=[0, 500], color_continuous_scale=colorscale, 
        projection="natural earth", template="plotly_white"
    )

    df_labels = df.drop_duplicates(subset=['Country']).copy()

    if scope == 'world':
        df_labels = df_labels.nlargest(30, 'AQI Value')
    else:
        df_labels = df_labels.nlargest(50, 'AQI Value')

    fig.add_trace(
        go.Scattergeo(
            locations=df_labels["Country"],
            locationmode='country names',
            text=df_labels["Country"],
            mode='text',
            textfont=dict(
                size=9, 
                color="#2c3e50",
                family="Arial"
            ),
            textposition="top center",
            hoverinfo='skip'
        )
    )

    fig.update_geos(
        scope=scope, 
        showcountries=True, 
        countrycolor="#d1d8e0", 
        showland=True, 
        landcolor="#f8f9fa"
    )

    fig.update_layout(
        margin={"r":0,"t":10,"l":0,"b":0}, 
        height=600, 
        coloraxis_showscale=False, 
        clickmode='event+select',
        uniformtext_minsize=8,
        uniformtext_mode='hide' 
    )
    

    return fig
