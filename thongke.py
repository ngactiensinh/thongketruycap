import streamlit as st
import pandas as pd
from supabase import create_client, Client
import plotly.express as px
import pytz
from datetime import datetime  # <--- DÒNG NÀY LÀ THUỐC CHỮA BỆNH ĐÂY Ạ

st.set_page_config(page_title="Thống kê Hệ sinh thái", page_icon="📊", layout="wide")

# --- CẤU HÌNH SUPABASE ---
SUPABASE_URL = "https://qqzsdxhqrdfvxnlurnyb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxenNkeGhxcmRmdnhubHVybnliIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU2MjY0NjAsImV4cCI6MjA5MTIwMjQ2MH0.H62F5zYEZ5l47fS4IdAE2JdRdI7inXQqWG0nvXhn2P8"
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    pass

st.markdown("""
<style>
    .metric-box { background-color: #ffffff; padding: 20px; border-radius: 10px; border-top: 5px solid #C8102E; box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center; margin-bottom: 20px; }
    .metric-title { font-size: 16px; color: #004B87; font-weight: bold; text-transform: uppercase; }
    .metric-value { font-size: 40px; color: #C8102E; font-weight: 900; line-height: 1; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #004B87; font-weight: 900; margin-bottom: 30px;'>📊 TRUNG TÂM PHÂN TÍCH LƯỢT TRUY CẬP HỆ SINH THÁI</h2>", unsafe_allow_html=True)

if st.button("🔄 Cập nhật số liệu mới nhất", use_container_width=True):
    st.cache_data.clear()

@st.cache_data(ttl=60)
def get_log_data():
    try:
        res = supabase.table("thong_ke_truy_cap").select("*").execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

df_log = get_log_data()

if df_log.empty:
    st.info("📭 Hệ thống chưa ghi nhận lượt truy cập nào.")
else:
    # Xử lý thời gian từ UTC về giờ Việt Nam
    tz_vn = pytz.timezone('Asia/Ho_Chi_Minh')
    df_log['Thời gian'] = pd.to_datetime(df_log['created_at']).dt.tz_convert(tz_vn)
    df_log['Ngày'] = df_log['Thời gian'].dt.strftime('%d/%m/%Y')
    df_log['Tháng'] = df_log['Thời gian'].dt.strftime('%m/%Y')

    # --- KHỐI THỐNG KÊ TỔNG QUAN ---
    tong_luot = len(df_log)
    luot_hom_nay = len(df_log[df_log['Ngày'] == datetime.now(tz_vn).strftime('%d/%m/%Y')])
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="metric-box"><div class="metric-title">Tổng truy cập toàn hệ thống</div><div class="metric-value">{tong_luot}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-box" style="border-color: #004B87;"><div class="metric-title">Truy cập trong hôm nay</div><div class="metric-value" style="color:#004B87;">{luot_hom_nay}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-box" style="border-color: #28a745;"><div class="metric-title">Số ứng dụng đang hoạt động</div><div class="metric-value" style="color:#28a745;">{df_log["ten_app"].nunique()}</div></div>', unsafe_allow_html=True)

    st.write("---")

    # --- KHỐI BIỂU ĐỒ ---
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("#### 🏆 Tỷ trọng truy cập theo Ứng dụng")
        df_app = df_log['ten_app'].value_counts().reset_index()
        df_app.columns = ['Ứng dụng', 'Số lượt']
        fig_pie = px.pie(df_app, values='Số lượt', names='Ứng dụng', hole=0.4)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        st.markdown("#### 📈 Biểu đồ tăng trưởng theo Ngày")
        df_day = df_log.groupby('Ngày').size().reset_index(name='Lượt truy cập')
        df_day['Ngày_sort'] = pd.to_datetime(df_day['Ngày'], format='%d/%m/%Y')
        df_day = df_day.sort_values('Ngày_sort')
        
        fig_line = px.line(df_day, x='Ngày', y='Lượt truy cập', markers=True, line_shape='spline', color_discrete_sequence=['#C8102E'])
        fig_line.update_traces(line=dict(width=3), marker=dict(size=8))
        st.plotly_chart(fig_line, use_container_width=True)

    # --- BẢNG DỮ LIỆU CHI TIẾT ---
    with st.expander("📜 XEM NHẬT KÝ TRUY CẬP CHI TIẾT"):
        df_show = df_log[['Thời gian', 'ten_app']].sort_values(by='Thời gian', ascending=False)
        df_show['Thời gian'] = df_show['Thời gian'].dt.strftime('%H:%M:%S - %d/%m/%Y')
        df_show.columns = ['Thời gian truy cập', 'Tên Ứng dụng']
        df_show.index = range(1, len(df_show) + 1)
        st.dataframe(df_show, use_container_width=True)
