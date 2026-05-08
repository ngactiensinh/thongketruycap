import streamlit as st
import pandas as pd
from supabase import create_client, Client
import plotly.express as px
import plotly.graph_objects as go
import pytz
from datetime import datetime, timedelta

# =============================================
# CẤU HÌNH TRANG
# =============================================
st.set_page_config(
    page_title="Hệ Sinh Thái | Analytics",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================
# CSS NÂNG CAO - GIAO DIỆN DARK COMMAND CENTER (TỐI)
# =============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Be Vietnam Pro', sans-serif;
    }

    /* Đổi toàn bộ nền thành màu Xanh đen sâu thẳm (Dark Blue/Black) */
    .stApp {
        background-color: #060b14 !important;
        background-image: radial-gradient(circle at 50% 0%, #112240 0%, #060b14 70%);
        color: #e2e8f0;
    }

    #MainMenu, footer, header { visibility: hidden; }

    .dashboard-header {
        text-align: center;
        padding: 40px 20px 20px;
        position: relative;
    }
    .dashboard-header::after {
        content: '';
        display: block;
        width: 120px;
        height: 4px;
        background: linear-gradient(90deg, #00f2fe, #4facfe);
        margin: 16px auto 0;
        border-radius: 2px;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.5);
    }
    .dashboard-title {
        font-size: 2.2rem;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: 1px;
        margin: 0;
        text-transform: uppercase;
        text-shadow: 0 0 15px rgba(79, 172, 254, 0.4);
    }
    .dashboard-subtitle {
        font-size: 0.9rem;
        color: #38bdf8;
        font-weight: 600;
        margin-top: 8px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Style cho các khối thẻ (Cards) với viền phát sáng (Glow) */
    .metric-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 24px 20px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.5), inset 0 0 0 1px rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.6), inset 0 0 0 1px rgba(255,255,255,0.1);
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        border-radius: 16px 16px 0 0;
    }
    
    /* Màu sắc Neon cho viền trên của thẻ */
    .metric-card.red::before    { background: #ef4444; box-shadow: 0 0 10px #ef4444; }
    .metric-card.blue::before   { background: #0ea5e9; box-shadow: 0 0 10px #0ea5e9; }
    .metric-card.orange::before { background: #f59e0b; box-shadow: 0 0 10px #f59e0b; }
    .metric-card.green::before  { background: #10b981; box-shadow: 0 0 10px #10b981; }

    .metric-icon  { font-size: 1.8rem; margin-bottom: 12px; display: block; opacity: 0.8;}
    .metric-label { font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 6px; }
    .metric-value { font-size: 2.8rem; font-weight: 900; line-height: 1; letter-spacing: -1px; text-shadow: 0 0 20px rgba(255,255,255,0.2); }

    /* Màu sắc Neon cho Chữ số liệu */
    .metric-card.red    .metric-value { color: #fca5a5; text-shadow: 0 0 15px rgba(239, 68, 68, 0.4);}
    .metric-card.blue   .metric-value { color: #7dd3fc; text-shadow: 0 0 15px rgba(14, 165, 233, 0.4);}
    .metric-card.orange .metric-value { color: #fcd34d; text-shadow: 0 0 15px rgba(245, 158, 11, 0.4);}
    .metric-card.green  .metric-value { color: #6ee7b7; text-shadow: 0 0 15px rgba(16, 185, 129, 0.4);}

    .metric-delta { font-size: 0.78rem; margin-top: 10px; padding: 4px 10px; border-radius: 20px; display: inline-block; font-weight: 600; }
    .delta-up  { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3);}
    .delta-down{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(248, 113, 113, 0.3);}
    .delta-neu { background: rgba(148, 163, 184, 0.1); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.3);}

    .section-title {
        font-size: 1rem; font-weight: 800; color: #38bdf8;
        text-transform: uppercase; letter-spacing: 1.5px;
        margin: 32px 0 16px;
        display: flex; align-items: center; gap: 8px;
    }
    .section-title::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, #1e293b, transparent); }

    .insight-card { background: rgba(15, 23, 42, 0.5); border: 1px solid #1e293b; border-left: 3px solid #38bdf8; border-radius: 8px; padding: 20px; margin-bottom: 12px; }
    .insight-title { font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .insight-value { font-size: 1.4rem; font-weight: 800; color: #f8fafc; }
    .insight-sub   { font-size: 0.8rem; color: #64748b; margin-top: 4px; }

    .status-live { display: inline-flex; align-items: center; gap: 6px; font-size: 0.8rem; color: #10b981; font-weight: 700; text-shadow: 0 0 5px #10b981;}
    .dot-live { width: 8px; height: 8px; border-radius: 50%; background: #10b981; animation: pulse 2s infinite; box-shadow: 0 0 8px #10b981;}
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%       { opacity: 0.5; transform: scale(1.5); }
    }

    /* Style lại Form bộ lọc cho hợp nền tối */
    .stSelectbox > div > div {
        background: #0f172a !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
        color: #f8fafc !important;
        font-weight: 500;
    }
    .stSelectbox > div > div > div > svg { fill: #38bdf8 !important; }
    
    .stButton > button {
        background: rgba(14, 165, 233, 0.1) !important;
        color: #38bdf8 !important; 
        border: 1px solid #0ea5e9 !important;
        border-radius: 8px !important;
        font-family: 'Be Vietnam Pro', sans-serif !important;
        font-weight: 700 !important; letter-spacing: 0.5px !important;
        padding: 10px 24px !important; transition: all 0.3s !important;
    }
    .stButton > button:hover { background: #0ea5e9 !important; color: white !important; box-shadow: 0 0 15px rgba(14, 165, 233, 0.5); }

    div[data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
    }
    .js-plotly-plot .plotly { background: transparent !important; }
    
    /* Làm nền bảng dữ liệu tối màu */
    [data-testid="stDataFrame"] { background-color: transparent !important; }
</style>
""", unsafe_allow_html=True)

# =============================================
# SUPABASE CONFIG
# =============================================
SUPABASE_URL = "https://qqzsdxhqrdfvxnlurnyb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxenNkeGhxcmRmdnhubHVybnliIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU2MjY0NjAsImV4cCI6MjA5MTIwMjQ2MH0.H62F5zYEZ5l47fS4IdAE2JdRdI7inXQqWG0nvXhn2P8"

supabase_ok = False
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    supabase_ok = True
except Exception:
    pass

tz_vn  = pytz.timezone('Asia/Ho_Chi_Minh')
now_vn = datetime.now(tz_vn)

# =============================================
# HEADER
# =============================================
st.markdown("""
<div class="dashboard-header">
    <p class="dashboard-subtitle">🌐 TGDV Ecosystem Platform</p>
    <h1 class="dashboard-title">HỆ THỐNG TRUNG TÂM ĐIỀU HÀNH TỔNG HỢP</h1>
</div>
""", unsafe_allow_html=True)

col_time, col_btn = st.columns([3, 1])
with col_time:
    time_str = now_vn.strftime('%H:%M:%S — %d/%m/%Y')
    st.markdown(f"""
        <div style="padding:8px 0;">
            <span class="status-live"><span class="dot-live"></span> Đang kết nối trực tuyến</span>
            <span style="color:#64748b;font-size:0.8rem;margin-left:16px; font-weight: 500;">Dữ liệu đồng bộ lúc: {time_str}</span>
        </div>
    """, unsafe_allow_html=True)
with col_btn:
    if st.button("🔄 Đồng bộ dữ liệu", use_container_width=True):
        st.session_state.pop("df_log_cache", None)
        st.session_state.pop("df_log_ts", None)
        st.rerun()

# =============================================
# LẤY DỮ LIỆU
# =============================================
def get_log_data():
    if not supabase_ok:
        return pd.DataFrame()
    try:
        res = supabase.table("thong_ke_truy_cap").select("*").order("created_at", desc=True).limit(50000).execute()
        return pd.DataFrame(res.data)
    except Exception:
        return pd.DataFrame()

_now_ts = datetime.now(tz_vn).timestamp()
if ("df_log_cache" not in st.session_state
        or _now_ts - st.session_state.get("df_log_ts", 0) > 60):
    st.session_state["df_log_cache"] = get_log_data()
    st.session_state["df_log_ts"] = _now_ts

df_log = st.session_state["df_log_cache"]

if df_log.empty:
    st.info("Chưa có dữ liệu truy cập nào được ghi nhận.")
    st.stop()

# =============================================
# XỬ LÝ THỜI GIAN + CHUẨN HÓA TÊN APP
# =============================================
df_log['Thời gian'] = pd.to_datetime(df_log['created_at']).dt.tz_convert(tz_vn)

# Loại bỏ các biến thể của Đăng ký số văn bản
df_log = df_log[~df_log['ten_app'].str.contains('Số văn bản|Số VB|So van ban|So VB', case=False, na=False)]

# Chuẩn hóa tên app
app_rename = {
    'Diem Tin Bao Chi':      'Điểm tin Báo chí',
    'diem tin bao chi':      'Điểm tin Báo chí',
    'DiemTinBaoChi':         'Điểm tin Báo chí',
    'Dang ky tin bai':       'Đăng ký Tin bài',
    'DangKyTinBai':          'Đăng ký Tin bài',
    'Theo doi nang luong':   'Theo dõi Nâng lương',
    'TheoDoiNangLuong':      'Theo dõi Nâng lương',
}
df_log['ten_app'] = df_log['ten_app'].replace(app_rename)

if df_log.empty:
    st.warning("Hiện tại không có dữ liệu cho các ứng dụng trong hệ thống.")
    st.stop()

df_log['Ngày']      = df_log['Thời gian'].dt.strftime('%d/%m/%Y')
df_log['Tháng']     = df_log['Thời gian'].dt.strftime('%m/%Y')
df_log['Giờ']       = df_log['Thời gian'].dt.hour
df_log['Thứ']       = df_log['Thời gian'].dt.day_name()
df_log['month_int'] = df_log['Thời gian'].dt.month
df_log['year_int']  = df_log['Thời gian'].dt.year

# =============================================
# BỘ LỌC
# =============================================
st.write("") 
col_filter, col_app_filter = st.columns(2)

with col_filter:
    st.markdown("<span style='font-size:0.8rem;font-weight:700;color:#38bdf8;text-transform:uppercase;letter-spacing:1px;'>📅 Chu kỳ phân tích</span>", unsafe_allow_html=True)
    loai_loc = st.selectbox("Kỳ", [
        "Tất cả thời gian", "Hôm nay", "7 Ngày Gần Nhất", "Tháng này",
        "Quý I", "Quý II", "Quý III", "Quý IV",
        "6 Tháng Đầu Năm", "6 Tháng Cuối Năm", "9 Tháng", "Năm nay"
    ], label_visibility="collapsed")

with col_app_filter:
    st.markdown("<span style='font-size:0.8rem;font-weight:700;color:#38bdf8;text-transform:uppercase;letter-spacing:1px;'>📱 Phân hệ ứng dụng</span>", unsafe_allow_html=True)
    app_list = ["Tất cả ứng dụng"] + sorted(df_log["ten_app"].dropna().unique().tolist())
    selected_app = st.selectbox("App", app_list, label_visibility="collapsed")

st.write("---") 

# Áp dụng bộ lọc
df_filtered    = df_log.copy()
current_year   = now_vn.year
current_month  = now_vn.month

if loai_loc != "Tất cả thời gian":
    if loai_loc == "Hôm nay":
        df_filtered = df_filtered[df_filtered['Ngày'] == now_vn.strftime('%d/%m/%Y')]
    elif loai_loc == "7 Ngày Gần Nhất":
        cutoff = now_vn - timedelta(days=7)
        df_filtered = df_filtered[df_filtered['Thời gian'] >= cutoff]
    else:
        df_filtered = df_filtered[df_filtered['year_int'] == current_year]
        if   loai_loc == "Tháng này":        df_filtered = df_filtered[df_filtered['month_int'] == current_month]
        elif loai_loc == "Quý I":            df_filtered = df_filtered[df_filtered['month_int'].isin([1,2,3])]
        elif loai_loc == "Quý II":           df_filtered = df_filtered[df_filtered['month_int'].isin([4,5,6])]
        elif loai_loc == "Quý III":          df_filtered = df_filtered[df_filtered['month_int'].isin([7,8,9])]
        elif loai_loc == "Quý IV":           df_filtered = df_filtered[df_filtered['month_int'].isin([10,11,12])]
        elif loai_loc == "6 Tháng Đầu Năm":  df_filtered = df_filtered[df_filtered['month_int'].isin([1,2,3,4,5,6])]
        elif loai_loc == "6 Tháng Cuối Năm": df_filtered = df_filtered[df_filtered['month_int'].isin([7,8,9,10,11,12])]
        elif loai_loc == "9 Tháng":          df_filtered = df_filtered[df_filtered['month_int'].isin([1,2,3,4,5,6,7,8,9])]

if selected_app != "Tất cả ứng dụng":
    df_filtered = df_filtered[df_filtered['ten_app'] == selected_app]

# =============================================
# TÍNH TOÁN METRICS
# =============================================
tong_all     = len(df_log)
luot_loc     = len(df_filtered)
luot_hom_nay = len(df_log[df_log['Ngày'] == now_vn.strftime('%d/%m/%Y')])
app_count    = df_filtered["ten_app"].nunique()

hom_qua_str  = (now_vn - timedelta(days=1)).strftime('%d/%m/%Y')
luot_hom_qua = len(df_log[df_log['Ngày'] == hom_qua_str])
if luot_hom_qua > 0:
    delta_pct   = ((luot_hom_nay - luot_hom_qua) / luot_hom_qua) * 100
    arrow       = "▲" if delta_pct >= 0 else "▼"
    delta_str   = f"{arrow} {abs(delta_pct):.1f}% so với hôm qua"
    delta_class = "delta-up" if delta_pct >= 0 else "delta-down"
else:
    delta_str   = "Chưa có dữ liệu hôm qua"
    delta_class = "delta-neu"

# =============================================
# METRIC CARDS (THẺ SỐ LIỆU PHÁT SÁNG)
# =============================================
c1, c2, c3, c4 = st.columns(4)

card_data = [
    (c1, "red",    "🌐", "TỔNG TOÀN HỆ THỐNG", f"{tong_all:,}",        "Tất cả thời gian", "delta-neu"),
    (c2, "blue",   "📊", "KỲ ĐANG PHÂN TÍCH",  f"{luot_loc:,}",        loai_loc,           "delta-neu"),
    (c3, "orange", "⚡", "TRUY CẬP HÔM NAY",    f"{luot_hom_nay:,}",    delta_str,          delta_class),
    (c4, "green",  "📱", "PHÂN HỆ HOẠT ĐỘNG",  f"{app_count:,}",       "Trong kỳ chọn",    "delta-neu"),
]

for col, color, icon, label, value, sub, dclass in card_data:
    with col:
        st.markdown(f"""
            <div class="metric-card {color}">
                <span class="metric-icon">{icon}</span>
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <span class="metric-delta {dclass}">{sub}</span>
            </div>
        """, unsafe_allow_html=True)

if df_filtered.empty:
    st.warning("Không có dữ liệu trong kỳ đã chọn.")
    st.stop()

# =============================================
# PLOTLY THEME (DARK MODE LỘT XÁC HOÀN TOÀN)
# =============================================
CHART_LAYOUT = dict(
    template='plotly_dark', # Sử dụng template tối mặc định của Plotly
    paper_bgcolor='rgba(0,0,0,0)', # Nền trong suốt
    plot_bgcolor='rgba(0,0,0,0)',  # Nền biểu đồ trong suốt
    font=dict(family='Be Vietnam Pro', color='#cbd5e1', size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(
        bgcolor='rgba(15,23,42,0.8)',
        bordercolor='#334155',
        borderwidth=1,
        font=dict(size=11, color='#f8fafc')
    )
)

# =============================================
# BIỂU ĐỒ 1: Pie + Line
# =============================================
st.markdown('<div class="section-title">📊 PHÂN TÍCH LƯU LƯỢNG TỔNG QUAN</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 2])

with col1:
    df_app = df_filtered['ten_app'].value_counts().reset_index()
    df_app.columns = ['App', 'Lượt']
    # Bảng màu Neon cực gắt
    COLORS = ['#0ea5e9', '#f43f5e', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#ec4899']
    
    fig_pie = go.Figure(go.Pie(
        labels=df_app['App'], values=df_app['Lượt'],
        hole=0.65, # Làm vòng donut mỏng lại cho giống radar
        marker=dict(colors=COLORS[:len(df_app)], line=dict(color='#0f172a', width=2)),
        textinfo='percent',
        textfont=dict(size=11, family='Be Vietnam Pro', color='#ffffff'),
        hovertemplate="<b>%{label}</b><br>%{value} lượt<br>%{percent}<extra></extra>"
    ))
    fig_pie.add_annotation(
        text=f"<b>{luot_loc:,}</b><br><span style='font-size:10px; color:#94a3b8;'>TỔNG LƯỢT</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=20, color='#38bdf8', family='Be Vietnam Pro')
    )
    fig_pie.update_layout(
        title=dict(text="Tỷ trọng Phân hệ (Ecosystem Distribution)", font=dict(size=14, color='#e2e8f0', weight='bold')),
        showlegend=True, **CHART_LAYOUT
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    df_day = df_filtered.groupby('Ngày').size().reset_index(name='Lượt')
    df_day['sort_key'] = pd.to_datetime(df_day['Ngày'], format='%d/%m/%Y')
    df_day = df_day.sort_values('sort_key')
    df_day['MA7'] = df_day['Lượt'].rolling(7, min_periods=1).mean()

    fig_line = go.Figure()
    # Đường chính màu xanh biển Neon (Cyan)
    fig_line.add_trace(go.Scatter(
        x=df_day['Ngày'], y=df_day['Lượt'],
        name='Lượt truy cập',
        fill='tozeroy', fillcolor='rgba(14, 165, 233, 0.15)', # Gradient mờ ảo
        line=dict(color='#0ea5e9', width=3, shape='spline'), # Đường cong mượt (spline)
        marker=dict(size=6, color='#0ea5e9', line=dict(width=2, color='white')),
        hovertemplate="<b>%{x}</b><br>%{y} lượt<extra></extra>"
    ))
    if len(df_day) >= 3:
        # Đường MA7 nét đứt màu cam phát sáng
        fig_line.add_trace(go.Scatter(
            x=df_day['Ngày'], y=df_day['MA7'].round(1),
            name='Trung bình 7 ngày',
            line=dict(color='#f59e0b', width=2, dash='dot'),
            hovertemplate="<b>%{x}</b><br>TB: %{y}<extra></extra>"
        ))
    fig_line.update_layout(
        title=dict(text="Lưu lượng theo Ngày (Daily Traffic Trend)", font=dict(size=14, color='#e2e8f0', weight='bold')),
        xaxis=dict(gridcolor='#1e293b', tickangle=-30, showgrid=False), # Tắt lưới dọc cho đỡ rối
        yaxis=dict(gridcolor='#1e293b'),
        hovermode='x unified', **CHART_LAYOUT
    )
    st.plotly_chart(fig_line, use_container_width=True)

# =============================================
# BIỂU ĐỒ 2: Giờ + App ranking
# =============================================
st.markdown('<div class="section-title">⏱️ BIỂU ĐỒ HÀNH VI VÀ XẾP HẠNG</div>', unsafe_allow_html=True)
col3, col4 = st.columns(2)

with col3:
    df_hour = df_filtered.groupby('Giờ').size().reset_index(name='Lượt')
    all_hours = pd.DataFrame({'Giờ': range(24)})
    df_hour = all_hours.merge(df_hour, on='Giờ', how='left').fillna(0)

    # Đổ gradient cho cột dọc (Đỏ đô đến Đỏ Neon)
    fig_bar_hour = go.Figure(go.Bar(
        x=df_hour['Giờ'], y=df_hour['Lượt'],
        marker=dict(
            color=df_hour['Lượt'],
            colorscale=[[0,'#4c0519'],[1,'#f43f5e']], 
            line=dict(width=1, color='#be123c')
        ),
        hovertemplate="<b>%{x}:00</b><br>%{y} lượt<extra></extra>"
    ))
    tick_vals = list(range(0, 24, 2))
    fig_bar_hour.update_layout(
        title=dict(text="Phân bổ theo Khung giờ (Heatmap theo Giờ)", font=dict(size=14, color='#e2e8f0', weight='bold')),
        xaxis=dict(tickmode='array', tickvals=tick_vals,
                   ticktext=[f"{h}h" for h in tick_vals],
                   gridcolor='#1e293b'),
        yaxis=dict(gridcolor='#1e293b'),
        bargap=0.15, **CHART_LAYOUT
    )
    st.plotly_chart(fig_bar_hour, use_container_width=True)

with col4:
    df_app_bar = df_filtered['ten_app'].value_counts().reset_index()
    df_app_bar.columns = ['App', 'Lượt']
    df_app_bar = df_app_bar.sort_values('Lượt')

    # Gradient cột ngang (Xanh đậm đến Cyan)
    fig_bar_app = go.Figure(go.Bar(
        x=df_app_bar['Lượt'], y=df_app_bar['App'],
        orientation='h',
        marker=dict(
            color=df_app_bar['Lượt'],
            colorscale=[[0,'#0f172a'],[1,'#0ea5e9']],
            line=dict(width=1, color='#38bdf8')
        ),
        hovertemplate="<b>%{y}</b><br>%{x} lượt<extra></extra>"
    ))
    fig_bar_app.update_layout(
        title=dict(text="Xếp hạng truy cập (Top Applications)", font=dict(size=14, color='#e2e8f0', weight='bold')),
        xaxis=dict(gridcolor='#1e293b'),
        yaxis=dict(gridcolor='rgba(0,0,0,0)'),
        **CHART_LAYOUT
    )
    st.plotly_chart(fig_bar_app, use_container_width=True)

# =============================================
# INSIGHT TỰ ĐỘNG
# =============================================
st.markdown('<div class="section-title">💡 BÁO CÁO PHÂN TÍCH NHANH (AI INSIGHTS)</div>', unsafe_allow_html=True)

peak_hour = int(df_filtered.groupby('Giờ').size().idxmax()) if not df_filtered.empty else 0
top_app   = df_filtered['ten_app'].value_counts().idxmax() if not df_filtered.empty else "—"
top_day   = df_filtered.groupby('Ngày').size().idxmax() if not df_filtered.empty else "—"
avg_day   = df_filtered.groupby('Ngày').size().mean() if not df_filtered.empty else 0

ins1, ins2, ins3, ins4 = st.columns(4)
insights = [
    (ins1, "Đỉnh lưu lượng (Giờ)",  f"{peak_hour}:00 – {peak_hour+1}:00", "Khung giờ nghẽn mạng nhất"),
    (ins2, "Phân hệ dẫn đầu",   top_app,                              "Nhiều lượt truy xuất dữ liệu nhất"),
    (ins3, "Ngày cao điểm", top_day,                              "Ngày có lượng thao tác đỉnh"),
    (ins4, "Trung bình tần suất",   f"{avg_day:.1f} request/ngày",        f"Theo phân tích kỳ: {loai_loc}"),
]
for col, title, val, sub in insights:
    with col:
        st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">{title}</div>
                <div class="insight-value">{val}</div>
                <div class="insight-sub">{sub}</div>
            </div>
        """, unsafe_allow_html=True)

# =============================================
# BẢNG CHI TIẾT
# =============================================
st.markdown('<div class="section-title">📂 TRUY VẾT NHẬT KÝ (LOGS)</div>', unsafe_allow_html=True)
with st.expander(f"Mở khóa toàn bộ {len(df_filtered):,} bản ghi trong kỳ '{loai_loc}'"):
    df_show = df_filtered[['Thời gian', 'ten_app']].sort_values('Thời gian', ascending=False).copy()
    df_show['Thời gian'] = df_show['Thời gian'].dt.strftime('%H:%M:%S — %d/%m/%Y')
    df_show.columns = ['Thời gian ghi nhận (Timestamp)', 'Mã Phân hệ (Module)']
    df_show.index = range(1, len(df_show) + 1)
    
    # Ép style bảng dữ liệu cho hợp màu tối
    st.markdown("""
        <style>
            [data-testid="stDataFrame"] { background-color: rgba(15, 23, 42, 0.5) !important; border-radius: 8px;}
        </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(df_show, use_container_width=True, height=400)

# Footer
st.markdown("""
<div style="text-align:center;padding:40px 0 20px;color:#475569;font-size:0.8rem; font-weight: 500; letter-spacing: 1px;">
    TGDV INTELLIGENT OPERATIONS CENTER • SYSTEM ONLINE
</div>
""", unsafe_allow_html=True)
