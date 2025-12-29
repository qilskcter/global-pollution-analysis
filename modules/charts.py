import plotly.express as px
import plotly.graph_objects as go

def apply_adaptive_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50, b=50, l=20, r=20)
    )
    return fig

def create_gauge(pm25_val, avg_csv):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta", value = pm25_val,
        delta = {'reference': avg_csv},
        title = {'text': "PM2.5 Thực tế vs TB Lịch sử"},
        gauge = {'axis': {'range': [0, 150]}, 'bar': {'color': "gray"},
                 'steps' : [{'range': [0, 15], 'color': "#27ae60"}, 
                            {'range': [15, 50], 'color': "#f1c40f"}, 
                            {'range': [50, 150], 'color': "#e74c3c"}]}))
    return apply_adaptive_theme(fig)

def create_main_map(df, scope, colorscale):
    fig = px.scatter_geo(
        df, locations="Country", locationmode='country names', 
        color="AQI Value", size="AQI Value", hover_name="City",
        custom_data=["City", "Country", "AQI Value", "CO AQI Value", "Ozone AQI Value", "NO2 AQI Value", "PM2.5 AQI Value"],
        range_color=[0, 500], color_continuous_scale=colorscale, 
        projection="natural earth", template="plotly_white"
    )
    fig.update_traces(mode='markers', marker=dict(opacity=0.7, line=dict(width=0.5, color='white')))
    fig.update_geos(scope=scope, showcountries=True, countrycolor="#636e72", showland=True, landcolor="#f8f9fa")
    fig.update_layout(margin={"r":0,"t":10,"l":0,"b":0}, height=600, coloraxis_showscale=False, clickmode='event+select')
    return fig