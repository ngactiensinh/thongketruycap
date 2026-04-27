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
# CSS NÂNG CAO - GIAO DIỆN LIGHT PREMIUM (SÁNG)
# =============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Be Vietnam Pro', sans-serif;
    }

    .stApp {
        background-color: #f4f6f9;
        color: #1e293b;
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
        width: 80px;
        height: 4px;
        background: linear-gradient(90deg, #C8102E, #004B87);
        margin: 16px auto 0;
        border-radius: 2px;
    }
    .dashboard-title {
        font-size: 2.2rem;
        font-weight: 900;
        color: #004B87;
        letter-spacing: -0.5px;
        margin: 0;
        text-transform: uppercase;
    }
    .dashboard-subtitle {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
        margin-top: 8px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px 20px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        border-radius: 16px 16px 0 0;
    }
    .metric-card.red::before    { background: #C8102E; }
    .metric-card.blue::before   { background: #004B87; }
    .metric-card.orange::before { background: #f59e0b; }
    .metric-card.green::before  { background: #10b981; }

    .metric-icon  { font-size: 1.8rem; margin-bottom: 12px; display: block; }
    .metric-label { font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 6px; }
    .metric-value { font-size: 2.5rem; font-weight: 900; line-height: 1; letter-spacing: -1px; }

    .metric-card.red    .metric-value { color: #C8102E; }
    .metric-card.blue   .metric-value { color: #004B87; }
    .metric-card.orange .metric-value { color: #d97706; }
    .metric-card.green  .metric-value { color: #059669; }

    .metric-delta { font-size: 0.78rem; margin-top: 8px; padding: 4px 10px; border-radius: 20px; display: inline-block; font-weight: 600; }
    .delta-up  { background: #d1fae5; color: #059669; }
    .delta-down{ background: #fee2e2; color: #dc2626; }
    .delta-neu { background: #f1f5f9; color: #64748b; }

    .section-title {
        font-size: 0.9rem; font-weight: 800; color: #004B87;
        text-transform: uppercase; letter-spacing: 1.5px;
        margin: 32px 0 16px;
        display: flex; align-items: center; gap: 8px;
    }
    .section-title::after { content: ''; flex: 1; height: 2px; background: #e2e8f0; }

    .insight-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .insight-title { font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .insight-value { font-size: 1.4rem; font-weight: 800; color: #0f172a; }
    .insight-sub   { font-size: 0.8rem; color: #64748b; margin-top: 4px; }

    .status-live { display: inline-flex; align-items: center; gap: 6px; font-size: 0.8rem; color: #059669; font-weight: 700; }
    .dot-live { width: 8px; height: 8px; border-radius: 50%; background: #10b981; animation: pulse 2s infinite; }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%       { opacity: 0.5; transform: scale(1.3); }
    }

    .stSelectbox > div > div {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        color: #1e293b !important;
        font-weight: 500;
    }
    .stButton > button {
        background: #004B87 !important;
        color: white !important; border: none !important;
        border-radius: 8px !important;
        font-family: 'Be Vietnam Pro', sans-serif !important;
        font-weight: 700 !important; letter-spacing: 0.5px !important;
        padding: 10px 24px !important; transition: all 0.3s !important;
        box-shadow: 0 4px 6px -1px rgba(0, 75, 135, 0.2);
    }
    .stButton > button:hover { background: #C8102E !important; transform: translateY(-2px); box-shadow: 0 6px 8px -1px rgba(200, 16, 46, 0.3); }

    div[data-testid="stExpander"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .js-plotly-plot .plotly { background: transparent !important; }
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
    <p class="dashboard-subtitle">🌐 Hệ Sinh Thái Ứng Dụng</p>
    <h1 class="dashboard-title">Trung Tâm Phân Tích Truy Cập</h1>
</div>
""", unsafe_allow_html=True)

col_time, col_btn = st.columns([3, 1])
with col_time:
    time_str = now_vn.strftime('%H:%M:%S — %d/%m/%Y')
    st.markdown(f"""
        <div style="padding:8px 0;">
            <span class="status-live"><span class="dot-live"></span> Dữ liệu thời gian thực</span>
            <span style="color:#64748b;font-size:0.8rem;margin-left:16px; font-weight: 500;">Cập nhật lúc: {time_str}</span>
        </div>
    """, unsafe_allow_html=True)
with col_btn:
    if st.button("Làm mới dữ liệu", use_container_width=True):
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

# Chuẩn hóa tên app
app_rename = {
    'Diem Tin Bao Chi':      'Điểm tin Báo chí',
    'diem tin bao chi':      'Điểm tin Báo chí',
    'DiemTinBaoChi':         'Điểm tin Báo chí',
}
df_log['ten_app'] = df_log['ten_app'].replace(app_rename)

df_log['Ngày']      = df_log['Thời gian'].dt.strftime('%d/%m/%Y')
df_log['Tháng']     = df_log['Thời gian'].dt.strftime('%m/%Y')
df_log['Giờ']       = df_log['Thời gian'].dt.hour
df_log['Thứ']       = df_log['Thời gian'].dt.day_name()
df_log['month_int'] = df_log['Thời gian'].dt.month
df_log['year_int']  = df_log['Thời gian'].dt.year

# =============================================
# BỘ LỌC
# =============================================
st.markdown('<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px 20px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
col_filter, col_app_filter = st.columns(2)

with col_filter:
    st.markdown("<span style='font-size:0.8rem;font-weight:700;color:#004B87;text-transform:uppercase;letter-spacing:1px;'>📅 Kỳ thống kê</span>", unsafe_allow_html=True)
    loai_loc = st.selectbox("Kỳ", [
        "Tất cả thời gian", "Hôm nay", "7 Ngày Gần Nhất", "Tháng này",
        "Quý I", "Quý II", "Quý III", "Quý IV",
        "6 Tháng Đầu Năm", "6 Tháng Cuối Năm", "9 Tháng", "Năm nay"
    ], label_visibility="collapsed")

with col_app_filter:
    st.markdown("<span style='font-size:0.8rem;font-weight:700;color:#004B87;text-transform:uppercase;letter-spacing:1px;'>📱 Ứng dụng</span>", unsafe_allow_html=True)
    app_list = ["Tất cả ứng dụng"] + sorted(df_log["ten_app"].dropna().unique().tolist())
    selected_app = st.selectbox("App", app_list, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

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
# METRIC CARDS
# =============================================
c1, c2, c3, c4 = st.columns(4)

card_data = [
    (c1, "red",    "🌐", "Tổng Toàn Hệ Thống", f"{tong_all:,}",        "Tất cả thời gian", "delta-neu"),
    (c2, "blue",   "📊", "Kỳ Đang Xem",         f"{luot_loc:,}",        loai_loc,           "delta-neu"),
    (c3, "orange", "⚡", "Hôm Nay",             f"{luot_hom_nay:,}",    delta_str,          delta_class),
    (c4, "green",  "📱", "App Hoạt Động",        f"{app_count:,}",       "Trong kỳ chọn",    "delta-neu"),
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
# PLOTLY THEME (LIGHT MODE)
# =============================================
CHART_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Be Vietnam Pro', color='#475569', size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor='#e2e8f0',
        borderwidth=1,
        font=dict(size=11, color='#1e293b')
    )
)

# =============================================
# BIỂU ĐỒ 1: Pie + Line
# =============================================
st.markdown('<div class="section-title">Phân tích tổng quan</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 2])

with col1:
    df_app = df_filtered['ten_app'].value_counts().reset_index()
    df_app.columns = ['App', 'Lượt']
    COLORS = ['#C8102E','#004B87','#f59e0b','#10b981','#8b5cf6','#f43f5e','#0ea5e9']
    fig_pie = go.Figure(go.Pie(
        labels=df_app['App'], values=df_app['Lượt'],
        hole=0.55,
        marker=dict(colors=COLORS[:len(df_app)], line=dict(color='#ffffff', width=2)),
        textinfo='percent',
        textfont=dict(size=11, family='Be Vietnam Pro', color='#ffffff'),
        hovertemplate="<b>%{label}</b><br>%{value} lượt<br>%{percent}<extra></extra>"
    ))
    fig_pie.add_annotation(
        text=f"<b>{luot_loc:,}</b><br><span style='font-size:10px;'>tổng lượt</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color='#1e293b', family='Be Vietnam Pro')
    )
    fig_pie.update_layout(
        title=dict(text="Tỷ trọng theo App", font=dict(size=14, color='#004B87', weight='bold')),
        showlegend=True, **CHART_LAYOUT
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    df_day = df_filtered.groupby('Ngày').size().reset_index(name='Lượt')
    df_day['sort_key'] = pd.to_datetime(df_day['Ngày'], format='%d/%m/%Y')
    df_day = df_day.sort_values('sort_key')
    df_day['MA7'] = df_day['Lượt'].rolling(7, min_periods=1).mean()

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=df_day['Ngày'], y=df_day['Lượt'],
        name='Lượt truy cập',
        fill='tozeroy', fillcolor='rgba(200,16,46,0.1)',
        line=dict(color='#C8102E', width=3),
        marker=dict(size=6, color='#C8102E'),
        hovertemplate="<b>%{x}</b><br>%{y} lượt<extra></extra>"
    ))
    if len(df_day) >= 3:
        fig_line.add_trace(go.Scatter(
            x=df_day['Ngày'], y=df_day['MA7'].round(1),
            name='Trung bình 7 ngày',
            line=dict(color='#004B87', width=2, dash='dot'),
            hovertemplate="<b>%{x}</b><br>TB: %{y}<extra></extra>"
        ))
    fig_line.update_layout(
        title=dict(text="Tăng trưởng theo Ngày", font=dict(size=14, color='#004B87', weight='bold')),
        xaxis=dict(gridcolor='#f1f5f9', tickangle=-30),
        yaxis=dict(gridcolor='#f1f5f9'),
        hovermode='x unified', **CHART_LAYOUT
    )
    st.plotly_chart(fig_line, use_container_width=True)

# =============================================
# BIỂU ĐỒ 2: Giờ + App ranking
# =============================================
st.markdown('<div class="section-title">Phân tích hành vi</div>', unsafe_allow_html=True)
col3, col4 = st.columns(2)

with col3:
    df_hour = df_filtered.groupby('Giờ').size().reset_index(name='Lượt')
    all_hours = pd.DataFrame({'Giờ': range(24)})
    df_hour = all_hours.merge(df_hour, on='Giờ', how='left').fillna(0)

    fig_bar_hour = go.Figure(go.Bar(
        x=df_hour['Giờ'], y=df_hour['Lượt'],
        marker=dict(
            color=df_hour['Lượt'],
            colorscale=[[0,'#fca5a5'],[1,'#C8102E']],
            line=dict(width=0)
        ),
        hovertemplate="<b>%{x}:00</b><br>%{y} lượt<extra></extra>"
    ))
    tick_vals = list(range(0, 24, 2))
    fig_bar_hour.update_layout(
        title=dict(text="Phân bổ theo Giờ trong Ngày", font=dict(size=14, color='#004B87', weight='bold')),
        xaxis=dict(tickmode='array', tickvals=tick_vals,
                   ticktext=[f"{h}h" for h in tick_vals],
                   gridcolor='#f1f5f9'),
        yaxis=dict(gridcolor='#f1f5f9'),
        bargap=0.2, **CHART_LAYOUT
    )
    st.plotly_chart(fig_bar_hour, use_container_width=True)

with col4:
    df_app_bar = df_filtered['ten_app'].value_counts().reset_index()
    df_app_bar.columns = ['App', 'Lượt']
    df_app_bar = df_app_bar.sort_values('Lượt')

    fig_bar_app = go.Figure(go.Bar(
        x=df_app_bar['Lượt'], y=df_app_bar['App'],
        orientation='h',
        marker=dict(
            color=df_app_bar['Lượt'],
            colorscale=[[0,'#bae6fd'],[1,'#004B87']],
            line=dict(width=0)
        ),
        hovertemplate="<b>%{y}</b><br>%{x} lượt<extra></extra>"
    ))
    fig_bar_app.update_layout(
        title=dict(text="Xếp hạng Ứng dụng", font=dict(size=14, color='#004B87', weight='bold')),
        xaxis=dict(gridcolor='#f1f5f9'),
        yaxis=dict(gridcolor='rgba(0,0,0,0)'),
        **CHART_LAYOUT
    )
    st.plotly_chart(fig_bar_app, use_container_width=True)

# =============================================
# INSIGHT TỰ ĐỘNG
# =============================================
st.markdown('<div class="section-title">Nhận xét tự động</div>', unsafe_allow_html=True)

peak_hour = int(df_filtered.groupby('Giờ').size().idxmax()) if not df_filtered.empty else 0
top_app   = df_filtered['ten_app'].value_counts().idxmax() if not df_filtered.empty else "—"
top_day   = df_filtered.groupby('Ngày').size().idxmax() if not df_filtered.empty else "—"
avg_day   = df_filtered.groupby('Ngày').size().mean() if not df_filtered.empty else 0

ins1, ins2, ins3, ins4 = st.columns(4)
insights = [
    (ins1, "Giờ cao điểm",  f"{peak_hour}:00 – {peak_hour+1}:00", "Lượt truy cập đạt đỉnh"),
    (ins2, "App dẫn đầu",   top_app,                              "Nhiều lượt nhất kỳ này"),
    (ins3, "Ngày bận nhất", top_day,                              "Đỉnh truy cập trong kỳ"),
    (ins4, "TB mỗi ngày",   f"{avg_day:.1f} lượt",                f"Trong kỳ: {loai_loc}"),
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
st.markdown('<div class="section-title">Nhật ký chi tiết</div>', unsafe_allow_html=True)
with st.expander(f"Xem tất cả {len(df_filtered):,} bản ghi trong kỳ '{loai_loc}'"):
    df_show = df_filtered[['Thời gian', 'ten_app']].sort_values('Thời gian', ascending=False).copy()
    df_show['Thời gian'] = df_show['Thời gian'].dt.strftime('%H:%M:%S — %d/%m/%Y')
    df_show.columns = ['Thời gian truy cập', 'Tên ứng dụng']
    df_show.index = range(1, len(df_show) + 1)
    st.dataframe(df_show, use_container_width=True, height=400)

# Footer
st.markdown("""
<div style="text-align:center;padding:40px 0 20px;color:#64748b;font-size:0.8rem; font-weight: 500;">
    Hệ Sinh Thái Analytics Dashboard • Cập nhật tự động mỗi 60 giây
</div>
""", unsafe_allow_html=True)
