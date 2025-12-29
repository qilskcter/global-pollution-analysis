import streamlit as st
import os

def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def display_health_card(pm25_val):
    if pm25_val >= 250.5:
        color, title = "#7e0023", "NGUY HẠI"
        impact = "Cảnh báo khẩn cấp. Toàn bộ cộng đồng có nguy cơ bị ảnh hưởng nghiêm trọng."
        action = "Tất cả mọi người nên ở trong nhà, đóng kín cửa. Tuyệt đối tránh vận động ngoài trời."
    elif pm25_val >= 150.5:
        color, title = "#8f3f97", "RẤT XẤU"
        impact = "Nguy cơ ảnh hưởng sức khỏe tăng cao cho tất cả mọi người."
        action = "Hạn chế tối đa ra ngoài. Nhóm nhạy cảm nên ở trong nhà hoàn toàn. Đeo khẩu trang chuyên dụng N95/N99."
    elif pm25_val >= 55.5:
        color, title = "#ff0000", "XẤU"
        impact = "Mọi người bắt đầu cảm thấy các tác động sức khỏe; nhóm nhạy cảm chịu hậu quả nặng hơn."
        action = "Tránh vận động mạnh ngoài trời. Nhóm nhạy cảm nên ở trong nhà. Bắt buộc đeo khẩu trang chống bụi mịn."
    elif pm25_val >= 35.5:
        color, title = "#ff7e00", "KÉM"
        impact = "Nhóm nhạy cảm (trẻ em, người già, người bệnh tim/phổi) có nguy cơ chịu tác động rõ rệt."
        action = "Nhóm nhạy cảm nên giảm vận động mạnh ngoài trời. Người bình thường nên hạn chế thời gian ở ngoài đường."
    elif pm25_val >= 12.1:
        color, title = "#ffff00", "TRUNG BÌNH"
        impact = "Chất lượng không khí chấp nhận được. Tuy nhiên, một số ít người cực kỳ nhạy cảm có thể gặp triệu chứng nhẹ."
        action = "Người cực kỳ nhạy cảm nên cân nhắc hạn chế vận động ngoài trời kéo dài nếu cảm thấy khó chịu."
    else:
        color, title = "#00e400", "TỐT"
        impact = "Chất lượng không khí an toàn. Không có rủi ro sức khỏe."
        action = "Lý tưởng cho các hoạt động thể thao ngoài trời và mở cửa thông gió nhà cửa."

    text_color = "black" if color == "#ffff00" else "white"

    st.markdown(f"""
        <div class="status-card" style="background:{color}; color:{text_color} !important; text-align: left; border-left: 10px solid rgba(0,0,0,0.2);">
            <h3 style="margin:0; color:{text_color};">{title}</h3>
            <p style="margin: 10px 0 5px 0; font-size: 0.9em;"><b>Ảnh hưởng:</b> {impact}</p>
            <p style="margin: 0; font-size: 0.9em;"><b>Khuyến nghị:</b> {action}</p>
        </div>
    """, unsafe_allow_html=True)