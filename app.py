import streamlit as st
import pandas as pd
import plotly.express as px
import os
from streamlit_searchbox import st_searchbox
from modules.data_handler import process_air_data, find_all_csv
from modules.api_service import get_realtime_data
from modules.charts import *
from modules.ui_utils import load_css, display_health_card

st.set_page_config(
    page_title="Pollution Analysis", 
    layout="wide", 
    page_icon="Assets/air-quality.png"
)

load_css("Assets/style.css")

default_file = 'Data_Analysis/global_air_pollution_clean_data_set.csv'
df_hist = None

if os.path.exists(default_file):
    df_hist = process_air_data(default_file)
    if "data_loaded_notification" not in st.session_state:
        st.toast(f"Đã tự động nạp dữ liệu: {default_file}")
        st.session_state.data_loaded_notification = True
else:
    csv_files = find_all_csv()
    if csv_files:
        selected_f = st.selectbox("Chọn file dữ liệu:", csv_files)
        df_hist = process_air_data(selected_f)
    else:
        uploaded_file = st.file_uploader("Tải tệp dữ liệu CSV:", type=["csv"])
        if uploaded_file: df_hist = process_air_data(uploaded_file)

if df_hist is not None:
    st.markdown('<div class="title-wrapper"><h1 class="main-title">POLLUTION ANALYSIS</h1></div>', unsafe_allow_html=True)

    with st.container():
        menu = st.radio(
            "", 
            ["Giám sát Real-time & Đối sánh", "Phân tích Lịch sử & Diễn biến"], 
            horizontal=True, 
            label_visibility="collapsed",
            key="navigation_menu" 
        )

    if menu == "Giám sát Real-time & Đối sánh":
        st.subheader("Giám sát Real-time & Đối sánh")
        c_in, _ = st.columns([1.5, 2.5])
        with c_in:
            available_cities = sorted(df_hist['City'].unique().tolist()) if 'City' in df_hist.columns else []
            def search_cities(t): return [c for c in available_cities if t.lower() in c.lower()][:20]
            
            city_input = st_searchbox(search_cities, label="Nhập tên thành phố:", key="city_search")
            btn_scan = st.button("Tìm kiếm")

        if btn_scan and city_input:
            result, error = get_realtime_data(city_input)
            if not error:
                st.session_state.realtime_result = result
                st.session_state.selected_city = city_input
            else:
                st.error(error)

        if "realtime_result" in st.session_state:
            result = st.session_state.realtime_result
            city_input = st.session_state.selected_city

            st.success(f"Kết nối thành công! {result['name']}, {result['country']}")
            comp = result['components']

            city_hist = df_hist[df_hist['City'].str.lower() == city_input.lower()]

            if city_hist.empty:
                row = df_hist.mean(numeric_only=True)
                st.warning("Không tìm thấy dữ liệu lịch sử của thành phố này, dùng giá trị trung bình.")
            else:
                row = city_hist.iloc[0]

            st.subheader("Cảnh báo y tế")
            display_health_card(comp['pm2_5'])

            st.markdown("### Chọn chỉ số cần xem")

            selected = st.selectbox(
                "Chỉ số môi trường:",
                ["AQI", "CO", "NO2", "Ozone", "PM2.5"],
                key="gauge_select"
            )

            value_map = {
                "AQI": row["AQI Value"],
                "CO": row["CO AQI Value"],
                "NO2": row["NO2 AQI Value"],
                "Ozone": row["Ozone AQI Value"],
                "PM2.5": row["PM2.5 AQI Value"]
            }

            cfg = GAUGE_CFG[selected]

            st.markdown('<div style="margin-top: 50px;"></div>', unsafe_allow_html=True)

            st.plotly_chart(
                create_gauge(
                    selected,
                    value_map[selected],
                    df_hist[cfg["col"]].mean(),
                    cfg["max"],
                    cfg["steps"],
                    cfg["unit"]
                ),
                width='stretch'
            )

    else:
        tab_line, tab_map, tab_pie = st.tabs(["Diễn biến ô nhiễm", "Bản đồ điểm nóng", "Cơ cấu chất khí"])
        
        with tab_map:
            st.subheader("Bản đồ điểm nóng toàn cầu")
            continent_map = {"Toàn cầu": "world", "Châu Á": "asia", "Châu Âu": "europe", "Châu Phi": "africa", "Bắc Mỹ": "north america", "Nam Mỹ": "south america"}
            col_sel1, col_sel2 = st.columns([1, 2])
            with col_sel1: sel_cont = st.selectbox("Khu vực:", list(continent_map.keys()))
            with col_sel2: aqi_range = st.select_slider('AQI:', options=list(range(501)), value=(0, 500))
            st.markdown(f"", unsafe_allow_html=True)

            aqi_colors = [(0, "#00e400"), (50, "#ffff00"), (100, "#ff7e00"), (150, "#ff0000"), (200, "#8f3f97"), (500, "#7e0023")]
            colorscale = [[v/500, c] for v, c in aqi_colors]
            
            m_df = df_hist[(df_hist['AQI Value'] >= aqi_range[0]) & (df_hist['AQI Value'] <= aqi_range[1])]
            
            if len(m_df) > 500:
                m_df = m_df.sample(n=500, random_state=42)

            col_m, col_s = st.columns([3, 1])
            with col_m:
                fig_map = create_main_map(m_df, continent_map[sel_cont], colorscale)
                event = st.plotly_chart(fig_map, width='stretch', on_select="rerun", key="geo_map")
            
            with col_s:
                st.markdown(f"**Top 5 ({sel_cont})**")
                for _, row in m_df.nlargest(5, 'AQI Value').iterrows():
                    c_code = next((c for v, c in reversed(aqi_colors) if row['AQI Value'] >= v), "#00e400")
                    st.markdown(f"""
                        <div style="
                            border-left: 5px solid {c_code}; 
                            padding: 10px; 
                            background: rgba(128, 128, 128, 0.1); 
                            border-radius: 8px;
                            margin-bottom: 8px;
                            line-height: 1.4;
                        ">
                            <div style="
                                font-size: 0.85rem; 
                                opacity: 0.8;
                                font-weight: 500;
                            ">
                                {row["City"]}
                            </div>
                            <div style="
                                font-size: 1.1rem; 
                                font-weight: 700;
                            ">
                                AQI: <span style="color: {c_code};">{row["AQI Value"]}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

            if event and "selection" in event and len(event["selection"]["points"]) > 0:
                st.session_state.clicked_data = event["selection"]["points"][0]["customdata"]
            
            if st.session_state.get("clicked_data"):
                p = st.session_state.clicked_data
                city, country, aqi_val, co, o3, no2, pm25 = p
                
                active_color = next((c for v, c in reversed(aqi_colors) if aqi_val >= v), "#00e400")
                
                st.markdown(f"""
                    <div class="detail-container" style="
                        padding: 20px; 
                        border-left: 10px solid {active_color}; 
                        background: rgba(128, 128, 128, 0.1); 
                        border-radius: 15px; 
                        margin-top: 20px;
                        border-top: 1px solid rgba(128, 128, 128, 0.05);
                    ">
                        <h2 style="margin:0; font-weight: 700;">{city}, {country}</h2>
                        <p style="margin:10px 0 0 0; font-size: 1.1rem; opacity: 0.9;">
                            Chỉ số AQI tổng hợp: 
                            <b style="color:{active_color}; font-size: 1.5rem; margin-left: 5px;">{aqi_val}</b>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                st.write("#### Thông tin chi tiết từ Dataset")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("PM2.5 AQI", pm25)
                c2.metric("NO2 AQI", no2)
                c3.metric("Ozone AQI", o3)
                c4.metric("CO AQI", co)

                fig_detail = px.bar(x=["AQI", "CO", "O3", "NO2", "PM2.5"], y=[aqi_val, co, o3, no2, pm25],
                                    color=[aqi_val, co, o3, no2, pm25], color_continuous_scale=colorscale, 
                                    range_color=[0, 500], text_auto=True)
                fig_detail.update_layout(height=400, coloraxis_showscale=False, transition_duration=500)
                st.plotly_chart(fig_detail, width='stretch')

            else:
                st.info("**Hướng dẫn:** Nhấn vào một chấm tròn trên bản đồ để xem hồ sơ dữ liệu chi tiết của khu vực đó.")

        with tab_line:
            st.subheader("Diễn biến ô nhiễm theo khu vực")
            
            if 'Continent' not in df_hist.columns:
                from modules.data_handler import get_continent_from_country
                df_hist['Continent'] = df_hist['Country'].apply(get_continent_from_country)

            col_l1, col_l2 = st.columns(2)
            
            with col_l1:
                line_continents = ["Toàn cầu"] + sorted(df_hist['Continent'].unique().tolist())
                sel_line_cont = st.selectbox("Chọn Châu lục:", line_continents, key="line_cont_sel")
            
            with col_l2:
                if sel_line_cont == "Toàn cầu":
                    line_countries = sorted(df_hist['Country'].unique().tolist())
                else:
                    line_countries = sorted(df_hist[df_hist['Continent'] == sel_line_cont]['Country'].unique().tolist())
                
                sel_line_country = st.selectbox(f"Chọn quốc gia ({sel_line_cont}):", line_countries, key="line_country_sel")

            df_line = df_hist[df_hist['Country'] == sel_line_country].sort_values('AQI Value')

            if not df_line.empty:
                fig_l = px.area(
                    df_line, 
                    x='City', 
                    y=['AQI Value', 'PM2.5 AQI Value'],
                    title=f"Chỉ số AQI tại các thành phố của {sel_line_country}",
                    labels={"value": "Chỉ số", "variable": "Loại chỉ số"}
                )
                st.plotly_chart(apply_adaptive_theme(fig_l), width='stretch')
            else:
                st.info("Không có dữ liệu cho quốc gia này.")

        with tab_pie:
            st.subheader("Cơ cấu chất khí theo khu vực")
            if 'Continent' not in df_hist.columns:
                from modules.data_handler import get_continent_from_country
                df_hist['Continent'] = df_hist['Country'].apply(get_continent_from_country)

            col_sel1, col_sel2 = st.columns(2)
            
            with col_sel1:
                available_continents = ["Toàn cầu"] + sorted(df_hist['Continent'].unique().tolist())
                sel_continent = st.selectbox("Chọn Châu lục:", available_continents)
            
            with col_sel2:
                if sel_continent == "Toàn cầu":
                    countries_filtered = sorted(df_hist['Country'].unique().tolist())
                else:
                    countries_filtered = sorted(df_hist[df_hist['Continent'] == sel_continent]['Country'].unique().tolist())
                
                sel_country = st.selectbox(f"Chọn quốc gia ({sel_continent}):", ["Tất cả"] + countries_filtered)

            if sel_continent == "Toàn cầu":
                if sel_country == "Tất cả":
                    df_pie = df_hist
                else:
                    df_pie = df_hist[df_hist['Country'] == sel_country]
            else:
                if sel_country == "Tất cả":
                    df_pie = df_hist[df_hist['Continent'] == sel_continent]
                else:
                    df_pie = df_hist[df_hist['Country'] == sel_country]

            if not df_pie.empty:
                gas_cols = ['CO AQI Value', 'Ozone AQI Value', 'NO2 AQI Value', 'PM2.5 AQI Value']
                p_sums = df_pie[gas_cols].mean()
                clean_names = [n.replace(' AQI Value', '') for n in gas_cols]
                
                fig_pie = px.pie(
                    values=p_sums, 
                    names=clean_names, 
                    hole=0.5,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                
                fig_pie.update_traces(
                    textinfo='percent+label',
                    marker=dict(line=dict(color='#FFFFFF', width=2))
                )
                
                title_text = f"Cơ cấu khí thải tại: {sel_country if sel_country != 'Tất cả' else sel_continent}"
                fig_pie.update_layout(title=title_text, showlegend=True)
                
                st.plotly_chart(apply_adaptive_theme(fig_pie), width='stretch')
            else:
                st.info("Không có dữ liệu cho lựa chọn này.")
else:

    st.info("Vui lòng nạp dữ liệu CSV.")