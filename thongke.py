import streamlit as st
import pandas as pd
from supabase import create_client, Client
import plotly.express as px
import pytz
from datetime import datetime

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
    .metric-title { font-size: 14px; color: #004B87; font-weight: bold; text-transform: uppercase; }
    .metric-value { font-size: 38px; color: #C8102E; font-weight: 900; line-height: 1; margin-top: 10px; }
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

    # ==========================================
    # BỘ LỌC THỜI GIAN THÔNG MINH
    # ==========================================
    st.markdown("<h4 style='color:#004B87; margin-bottom: 10px;'>🗓️ CHỌN KỲ THỐNG KÊ</h4>", unsafe_allow_html=True)
    
    current_year = datetime.now(tz_vn).year
    current_month = datetime.now(tz_vn).month

    loai_loc = st.selectbox("Lọc dữ liệu theo:", [
        "Tất cả thời gian", "Tháng này", "Quý I", "Quý II", "Quý III", "Quý IV", 
        "6 Tháng Đầu Năm", "6 Tháng Cuối Năm", "9 Tháng", "Năm nay"
    ], label_visibility="collapsed")

    df_filtered = df_log.copy()
    
    if loai_loc != "Tất cả thời gian":
        df_filtered['month_int'] = df_filtered['Thời gian'].dt.month
        df_filtered['year_int'] = df_filtered['Thời gian'].dt.year
        # Ép khung chỉ lấy dữ liệu của năm hiện tại
        df_filtered = df_filtered[df_filtered['year_int'] == current_year]

        if loai_loc == "Tháng này": df_filtered = df_filtered[df_filtered['month_int'] == current_month]
        elif loai_loc == "Quý I": df_filtered = df_filtered[df_filtered['month_int'].isin([1, 2, 3])]
        elif loai_loc == "Quý II": df_filtered = df_filtered[df_filtered['month_int'].isin([4, 5, 6])]
        elif loai_loc == "Quý III": df_filtered = df_filtered[df_filtered['month_int'].isin([7, 8, 9])]
        elif loai_loc == "Quý IV": df_filtered = df_filtered[df_filtered['month_int'].isin([10, 11, 12])]
        elif loai_loc == "6 Tháng Đầu Năm": df_filtered = df_filtered[df_filtered['month_int'].isin([1, 2, 3, 4, 5, 6])]
        elif loai_loc == "6 Tháng Cuối Năm": df_filtered = df_filtered[df_filtered['month_int'].isin([7, 8, 9, 10, 11, 12])]
        elif loai_loc == "9 Tháng": df_filtered = df_filtered[df_filtered['month_int'].isin([1, 2, 3, 4, 5, 6, 7, 8, 9])]
        # "Năm nay" thì giữ nguyên do đã lọc year_int ở trên

    # ==========================================
    # KHỐI THỐNG KÊ TỔNG QUAN
    # ==========================================
    tong_luot_all = len(df_log)
    luot_ky_nay = len(df_filtered)
    luot_hom_nay = len(df_log[df_log['Ngày'] == datetime.now(tz_vn).strftime('%d/%m/%Y')])
    app_hoat_dong = df_filtered["ten_app"].nunique()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-box"><div class="metric-title">Tổng toàn HT</div><div class="metric-value">{tong_luot_all}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-box" style="border-color: #004B87;"><div class="metric-title">Kỳ đang chọn</div><div class="metric-value" style="color:#004B87;">{luot_ky_nay}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-box" style="border-color: #ff9900;"><div class="metric-title">Hôm nay</div><div class="metric-value" style="color:#ff9900;">{luot_hom_nay}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-box" style="border-color: #28a745;"><div class="metric-title">App Hoạt động</div><div class="metric-value" style="color:#28a745;">{app_hoat_dong}</div></div>', unsafe_allow_html=True)

    st.write("---")

    if df_filtered.empty:
        st.warning(f"📭 Hệ thống không có lượt truy cập nào trong kỳ: **{loai_loc}**")
    else:
        # ==========================================
        # KHỐI BIỂU ĐỒ
        # ==========================================
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown(f"#### 🏆 Tỷ trọng truy cập ({loai_loc})")
            df_app = df_filtered['ten_app'].value_counts().reset_index()
            df_app.columns = ['Ứng dụng', 'Số lượt']
            fig_pie = px.pie(df_app, values='Số lượt', names='Ứng dụng', hole=0.4)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_chart2:
            st.markdown(f"#### 📈 Tăng trưởng theo Ngày ({loai_loc})")
            df_day = df_filtered.groupby('Ngày').size().reset_index(name='Lượt truy cập')
            df_day['Ngày_sort'] = pd.to_datetime(df_day['Ngày'], format='%d/%m/%Y')
            df_day = df_day.sort_values('Ngày_sort')
            
            fig_line = px.line(df_day, x='Ngày', y='Lượt truy cập', markers=True, line_shape='spline', color_discrete_sequence=['#C8102E'])
            fig_line.update_traces(line=dict(width=3), marker=dict(size=8))
            st.plotly_chart(fig_line, use_container_width=True)

        # ==========================================
        # BẢNG DỮ LIỆU CHI TIẾT
        # ==========================================
        with st.expander(f"📜 XEM NHẬT KÝ CHI TIẾT ({loai_loc})"):
            df_show = df_filtered[['Thời gian', 'ten_app']].sort_values(by='Thời gian', ascending=False)
            df_show['Thời gian'] = df_show['Thời gian'].dt.strftime('%H:%M:%S - %d/%m/%Y')
            df_show.columns = ['Thời gian truy cập', 'Tên Ứng dụng']
            df_show.index = range(1, len(df_show) + 1)
            st.dataframe(df_show, use_container_width=True)
