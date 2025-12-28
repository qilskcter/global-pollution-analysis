import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import os
import glob
from streamlit_searchbox import st_searchbox

st.set_page_config(page_title="AirGuard Hybrid", layout="wide", page_icon="🌬️")

def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    load_css("style.css")
except:
    st.info("Hãy tạo file style.css để kích hoạt giao diện Topbar & Adaptive UI.")

API_KEY = "a8c35a6b54ef7bbf688768bb545ee920" 

def process_air_data(file_source):
    df = pd.read_csv(file_source)
    df = df.interpolate(method='linear').ffill().bfill()
    if 'AQI Value' in df.columns:
        Q1 = df['AQI Value'].quantile(0.25)
        Q3 = df['AQI Value'].quantile(0.75)
        IQR = Q3 - Q1
        df = df[(df['AQI Value'] >= (Q1 - 1.5 * IQR)) & (df['AQI Value'] <= (Q3 + 1.5 * IQR))]
    return df

st.markdown('<h1 style="text-align: center; margin-top: -30px;">AIRGUARD HYBRID</h1>', unsafe_allow_html=True)

default_file = 'Data_Analysis/global_air_pollution_clean_data_set.csv'
csv_files = glob.glob("*.csv") + glob.glob("**/*.csv", recursive=True)
df_hist = None

if os.path.exists(default_file):
    df_hist = process_air_data(default_file)
    st.toast(f"Đã tự động nạp dữ liệu: {default_file}")
elif csv_files:
    selected_f = st.selectbox("Không tìm thấy file mặc định. Vui lòng chọn file dữ liệu từ thư mục:", csv_files)
    df_hist = process_air_data(selected_f)
else:
    st.error("Không tìm thấy tệp dữ liệu CSV nào trong thư mục!")
    uploaded_file = st.file_uploader("Vui lòng tải lên tệp dữ liệu (.csv) để bắt đầu:", type=["csv"])
    if uploaded_file:
        df_hist = process_air_data(uploaded_file)

def apply_adaptive_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=None,
        margin=dict(t=50, b=50, l=20, r=20)
    )
    return fig

if df_hist is not None:
    menu = st.radio("", ["Giám sát Real-time & Đối sánh", "Phân tích Lịch sử & Diễn biến"], horizontal=True, label_visibility="collapsed")
    st.markdown("---")

    if menu == "Giám sát Real-time & Đối sánh":
        c_in, _ = st.columns([1.5, 2.5])
        with c_in:
            available_cities = sorted(df_hist['City'].unique().tolist()) if 'City' in df_hist.columns else []

            def search_cities(searchterm: str):
                if not searchterm:
                    return available_cities[:20]
                matches = [city for city in available_cities if searchterm.lower() in city.lower()]
                return matches[:20]

            city_input = st_searchbox(
                search_cities,
                label="Nhập tên thành phố (vd: Ha noi, Tokyo...):",
                placeholder="Gõ để tìm kiếm...",
                key="city_search",
                clear_on_submit=False
            )
            btn_scan = st.button("Tìm kiếm")

        if btn_scan:
            if not city_input:
                st.warning("Vui lòng nhập tên thành phố.")
            else:
                try:
                    geo = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city_input}&limit=1&appid={API_KEY}").json()
                    if not geo:
                        st.error("Không tìm thấy thành phố này. Hãy kiểm tra lại.")
                    else:
                        lat, lon = geo[0]['lat'], geo[0]['lon']
                        res = requests.get(f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}").json()
                        data = res['list'][0]
                        comp = data['components']
                        pm25_val = comp['pm2_5']
                        
                        st.success(f"Kết nối thành công! {geo[0]['name']}, {geo[0]['country']}")
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("PM2.5", f"{pm25_val} µg/m³")
                        m2.metric("NO2", f"{comp['no2']} µg/m³")
                        m3.metric("CO", f"{round(comp['co']/1000, 2)} mg/m³")
                        m4.metric("Ozone", f"{comp['o3']} µg/m³")
                        
                        st.divider()
                        cg, cr = st.columns([1.5, 1])
                        with cg:
                            avg_csv = df_hist['AQI Value'].mean()
                            fig_g = go.Figure(go.Indicator(
                                mode = "gauge+number+delta", value = pm25_val,
                                delta = {'reference': avg_csv},
                                title = {'text': "PM2.5 Thực tế vs TB Lịch sử"},
                                gauge = {'axis': {'range': [0, 150]}, 'bar': {'color': "gray"},
                                         'steps' : [{'range': [0, 15], 'color': "#27ae60"}, 
                                                    {'range': [15, 50], 'color': "#f1c40f"}, 
                                                    {'range': [50, 150], 'color': "#e74c3c"}]}))
                            st.plotly_chart(apply_adaptive_theme(fig_g), use_container_width=True)
                        with cr:
                            st.subheader("Cảnh báo y tế")
                            # 
                            if pm25_val >= 55.5:
                                color, title, impact = "#c0392b", "XẤU", "Tránh vận động ngoài trời. Đeo khẩu trang N95."
                            elif pm25_val >= 12.1:
                                color, title, impact = "#f39c12", "TRUNG BÌNH", "Nhóm nhạy cảm nên hạn chế ra ngoài."
                            else:
                                color, title, impact = "#27ae60", "AN TOÀN", "Tự do hoạt động ngoài trời."
                            
                            st.markdown(f'<div class="status-card" style="background:{color};">{title}<br><small>{impact}</small></div>', unsafe_allow_html=True)
                except:
                    st.error("Lỗi API.")

    else:
        st.subheader("Hồ sơ diễn biến & Phân tích Historical Data")
        tab_line, tab_map, tab_pie = st.tabs(["Diễn biến ô nhiễm", "Bản đồ điểm nóng", "Cơ cấu chất khí"])
        
        with tab_line:
            country_list = sorted(df_hist['Country'].unique())
            sel_c = st.selectbox("Chọn quốc gia:", country_list, index=0)
            c_df = df_hist[df_hist['Country'] == sel_c].sort_values('AQI Value')
            fig_l = px.area(c_df, x='City', y=['AQI Value', 'PM2.5 AQI Value'], title=f"Biến thiên tại {sel_c}")
            st.plotly_chart(apply_adaptive_theme(fig_l), use_container_width=True)

        with tab_map:
            st.subheader("Bản đồ điểm nóng AQI (Click để xem chi tiết)")
            
            # 1. Định nghĩa bảng màu AQI chuẩn
            aqi_colors = [(0, "#00e400"), (50, "#ffff00"), (100, "#ff7e00"), (150, "#ff0000"), (200, "#8f3f97"), (500, "#7e0023")]
            
            # 2. Slider lọc giá trị (CSS nằm trong style.css đã load ở trên)
            aqi_range = st.select_slider('Lọc giá trị AQI:', options=list(range(0, 501)), value=(0, 500), key="aqi_slider_map")
            
            # 3. Xử lý dữ liệu
            m_df = df_hist[(df_hist['AQI Value'] >= aqi_range[0]) & (df_hist['AQI Value'] <= aqi_range[1])]
            map_display = m_df.sample(min(2000, len(m_df)))
            
            # 4. Cấu hình màu cho Plotly
            plotly_colorscale = [[v/500, c] for v, c in aqi_colors]
            
            fig_map = px.scatter_geo(
                map_display, locations="Country", locationmode='country names', color="AQI Value", 
                size="AQI Value", hover_name="City",
                custom_data=["City", "Country", "AQI Value", "CO AQI Value", "Ozone AQI Value", "NO2 AQI Value", "PM2.5 AQI Value"],
                range_color=[0, 500], color_continuous_scale=plotly_colorscale, projection="natural earth", template="plotly_white"
            )
            fig_map.update_geos(showcountries=True, countrycolor="#ecf0f1", showland=True, landcolor="#f9f9f9", showocean=True, oceancolor="#ffffff")
            fig_map.update_layout(margin={"r":0,"t":10,"l":0,"b":0}, height=600, coloraxis_showscale=False, clickmode='event+select')
            
            event_data = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun", key="geo_map")
            
            if event_data and "selection" in event_data and len(event_data["selection"]["points"]) > 0:
                c_data = event_data["selection"]["points"][0]["customdata"]
                city, country, aqi_val, co, o3, no2, pm25 = c_data
                
                active_color = "#00e400"
                for v, c in aqi_colors:
                    if aqi_val >= v: active_color = c
                
                st.markdown(f"""
                <div style="padding:15px; border-left: 8px solid {active_color}; background-color: #f1f3f6; border-radius: 5px; margin-top: 20px;">
                    <h2 style="margin:0; color:#2c3e50;">📍 {city}, {country}</h2>
                    <p style="margin:0; font-size:18px;">Chỉ số AQI: <b style="color:{active_color};">{aqi_val}</b></p>
                </div>
                """, unsafe_allow_html=True)

                detail_df = pd.DataFrame({
                    "Chỉ số": ["Tổng quan (AQI)", "CO", "Ozone", "NO2", "PM2.5"],
                    "Giá trị": [aqi_val, co, o3, no2, pm25]
                })
                fig_detail = px.bar(detail_df, x="Chỉ số", y="Giá trị", color="Giá trị", 
                                    color_continuous_scale=plotly_colorscale, range_color=[0, 500], 
                                    text_auto=True, template="plotly_white")
                fig_detail.update_layout(height=400, coloraxis_showscale=False)
                st.plotly_chart(fig_detail, use_container_width=True)
            else:
                st.info("💡 **Hướng dẫn:** Hãy click chuột vào một chấm tròn trên bản đồ để xem biểu đồ phân tích chi tiết.")

        with tab_pie:
            st.subheader("Phân bổ cơ cấu chất khí")
            p_sums = df_hist[['CO AQI Value', 'Ozone AQI Value', 'NO2 AQI Value', 'PM2.5 AQI Value']].mean()
            fig_pie = px.pie(values=p_sums, names=["CO", "O3", "NO2", "PM2.5"], hole=0.5)
            st.plotly_chart(apply_adaptive_theme(fig_pie), use_container_width=True)
else:
    st.info("Vui lòng nạp dữ liệu CSV.")