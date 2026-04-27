import streamlit as st
import pandas as pd
from supabase import create_client, Client
import plotly.express as px
import plotly.graph_objects as go
import pytz
from datetime import datetime, timedelta

# =============================================
# CAU HINH TRANG
# =============================================
st.set_page_config(
    page_title="He Sinh Thai | Analytics",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================
# CSS NANG CAO - GIAO DIEN DARK PREMIUM
# =============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Be Vietnam Pro', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 40%, #0a1628 100%);
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
        width: 80px;
        height: 3px;
        background: linear-gradient(90deg, #C8102E, #ff6b35);
        margin: 16px auto 0;
        border-radius: 2px;
    }
    .dashboard-title {
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #ffffff 0%, #a8c8ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .dashboard-subtitle {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 400;
        margin-top: 8px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 24px 20px;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        border-radius: 16px 16px 0 0;
    }
    .metric-card.red::before    { background: linear-gradient(90deg, #C8102E, #ff4d6d); }
    .metric-card.blue::before   { background: linear-gradient(90deg, #004B87, #0078d4); }
    .metric-card.orange::before { background: linear-gradient(90deg, #ff9900, #ffcc44); }
    .metric-card.green::before  { background: linear-gradient(90deg, #10b981, #34d399); }

    .metric-icon  { font-size: 1.8rem; margin-bottom: 12px; display: block; }
    .metric-label { font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; }
    .metric-value { font-size: 2.5rem; font-weight: 900; line-height: 1; letter-spacing: -1px; }

    .metric-card.red    .metric-value { color: #ff4d6d; }
    .metric-card.blue   .metric-value { color: #60a5fa; }
    .metric-card.orange .metric-value { color: #fbbf24; }
    .metric-card.green  .metric-value { color: #34d399; }

    .metric-delta { font-size: 0.78rem; margin-top: 8px; padding: 3px 8px; border-radius: 20px; display: inline-block; font-weight: 600; }
    .delta-up  { background: rgba(16,185,129,0.15); color: #34d399; }
    .delta-down{ background: rgba(239,68,68,0.15);  color: #f87171; }
    .delta-neu { background: rgba(100,116,139,0.15); color: #94a3b8; }

    .section-title {
        font-size: 0.8rem; font-weight: 700; color: #64748b;
        text-transform: uppercase; letter-spacing: 2px;
        margin: 32px 0 16px;
        display: flex; align-items: center; gap: 8px;
    }
    .section-title::after { content: ''; flex: 1; height: 1px; background: rgba(255,255,255,0.06); }

    .insight-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 20px; margin-bottom: 12px; }
    .insight-title { font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .insight-value { font-size: 1.4rem; font-weight: 800; color: #e2e8f0; }
    .insight-sub   { font-size: 0.8rem; color: #475569; margin-top: 4px; }

    .status-live { display: inline-flex; align-items: center; gap: 6px; font-size: 0.75rem; color: #34d399; font-weight: 600; }
    .dot-live { width: 8px; height: 8px; border-radius: 50%; background: #34d399; animation: pulse 2s infinite; }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%       { opacity: 0.5; transform: scale(1.3); }
    }

    .stSelectbox > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #C8102E, #ff4d6d) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important;
        font-family: 'Be Vietnam Pro', sans-serif !important;
        font-weight: 700 !important; letter-spacing: 0.5px !important;
        padding: 10px 24px !important; transition: opacity 0.2s !important;
    }
    .stButton > button:hover { opacity: 0.85 !important; }

    div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.02) !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: 12px !important;
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
    <p class="dashboard-subtitle">&#127758; He Sinh Thai Ung Dung</p>
    <h1 class="dashboard-title">Trung Tam Phan Tich Truy Cap</h1>
</div>
""", unsafe_allow_html=True)

col_time, col_btn = st.columns([3, 1])
with col_time:
    time_str = now_vn.strftime('%H:%M:%S \u2014 %d/%m/%Y')
    st.markdown(
        '<div style="padding:8px 0;">'
        '<span class="status-live"><span class="dot-live"></span> Du lieu thoi gian thuc</span>'
        '<span style="color:#475569;font-size:0.8rem;margin-left:16px;">Cap nhat luc: ' + time_str + '</span>'
        '</div>',
        unsafe_allow_html=True
    )
with col_btn:
    if st.button("Lam moi du lieu", use_container_width=True):
        st.session_state.pop("df_log_cache", None)
        st.session_state.pop("df_log_ts", None)
        st.rerun()

# =============================================
# LAY DU LIEU
# =============================================
def get_log_data():
    if not supabase_ok:
        return pd.DataFrame()
    try:
        res = supabase.table("thong_ke_truy_cap").select("*").order("created_at", desc=True).limit(5000).execute()
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
    st.info("Chua co du lieu truy cap nao duoc ghi nhan.")
    st.stop()

# =============================================
# XU LY THOI GIAN + CHUAN HOA TEN APP
# =============================================
df_log['Thoi gian'] = pd.to_datetime(df_log['created_at']).dt.tz_convert(tz_vn)

# Chuan hoa ten app: gop cac bien the khong dau / loi chinh ta vao ten chinh
app_rename = {
    'Diem Tin Bao Chi':      'Diem tin Bao chi',
    'diem tin bao chi':      'Diem tin Bao chi',
    'DiemTinBaoChi':         'Diem tin Bao chi',
}
df_log['ten_app'] = df_log['ten_app'].replace(app_rename)

df_log['Ngay']      = df_log['Thoi gian'].dt.strftime('%d/%m/%Y')
df_log['Thang']     = df_log['Thoi gian'].dt.strftime('%m/%Y')
df_log['Gio']       = df_log['Thoi gian'].dt.hour
df_log['Thu']       = df_log['Thoi gian'].dt.day_name()
df_log['month_int'] = df_log['Thoi gian'].dt.month
df_log['year_int']  = df_log['Thoi gian'].dt.year

# =============================================
# BO LOC
# =============================================
col_filter, col_app_filter = st.columns(2)

with col_filter:
    st.markdown("<span style='font-size:0.8rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:1px;'>Ky thong ke</span>", unsafe_allow_html=True)
    loai_loc = st.selectbox("Ky", [
        "Tat ca thoi gian", "Hom nay", "7 Ngay Gan Nhat", "Thang nay",
        "Quy I", "Quy II", "Quy III", "Quy IV",
        "6 Thang Dau Nam", "6 Thang Cuoi Nam", "9 Thang", "Nam nay"
    ], label_visibility="collapsed")

with col_app_filter:
    st.markdown("<span style='font-size:0.8rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:1px;'>Ung dung</span>", unsafe_allow_html=True)
    app_list = ["Tat ca ung dung"] + sorted(df_log["ten_app"].dropna().unique().tolist())
    selected_app = st.selectbox("App", app_list, label_visibility="collapsed")

# Ap dung bo loc
df_filtered    = df_log.copy()
current_year   = now_vn.year
current_month  = now_vn.month

if loai_loc != "Tat ca thoi gian":
    if loai_loc == "Hom nay":
        df_filtered = df_filtered[df_filtered['Ngay'] == now_vn.strftime('%d/%m/%Y')]
    elif loai_loc == "7 Ngay Gan Nhat":
        cutoff = now_vn - timedelta(days=7)
        df_filtered = df_filtered[df_filtered['Thoi gian'] >= cutoff]
    else:
        df_filtered = df_filtered[df_filtered['year_int'] == current_year]
        if   loai_loc == "Thang nay":        df_filtered = df_filtered[df_filtered['month_int'] == current_month]
        elif loai_loc == "Quy I":            df_filtered = df_filtered[df_filtered['month_int'].isin([1,2,3])]
        elif loai_loc == "Quy II":           df_filtered = df_filtered[df_filtered['month_int'].isin([4,5,6])]
        elif loai_loc == "Quy III":          df_filtered = df_filtered[df_filtered['month_int'].isin([7,8,9])]
        elif loai_loc == "Quy IV":           df_filtered = df_filtered[df_filtered['month_int'].isin([10,11,12])]
        elif loai_loc == "6 Thang Dau Nam":  df_filtered = df_filtered[df_filtered['month_int'].isin([1,2,3,4,5,6])]
        elif loai_loc == "6 Thang Cuoi Nam": df_filtered = df_filtered[df_filtered['month_int'].isin([7,8,9,10,11,12])]
        elif loai_loc == "9 Thang":          df_filtered = df_filtered[df_filtered['month_int'].isin([1,2,3,4,5,6,7,8,9])]

if selected_app != "Tat ca ung dung":
    df_filtered = df_filtered[df_filtered['ten_app'] == selected_app]

# =============================================
# TINH TOAN METRICS
# =============================================
tong_all     = len(df_log)
luot_loc     = len(df_filtered)
luot_hom_nay = len(df_log[df_log['Ngay'] == now_vn.strftime('%d/%m/%Y')])
app_count    = df_filtered["ten_app"].nunique()

hom_qua_str  = (now_vn - timedelta(days=1)).strftime('%d/%m/%Y')
luot_hom_qua = len(df_log[df_log['Ngay'] == hom_qua_str])
if luot_hom_qua > 0:
    delta_pct   = ((luot_hom_nay - luot_hom_qua) / luot_hom_qua) * 100
    arrow       = "▲" if delta_pct >= 0 else "▼"
    delta_str   = arrow + " " + str(round(abs(delta_pct), 1)) + "% so hom qua"
    delta_class = "delta-up" if delta_pct >= 0 else "delta-down"
else:
    delta_str   = "Chua co du lieu hom qua"
    delta_class = "delta-neu"

# =============================================
# METRIC CARDS
# =============================================
c1, c2, c3, c4 = st.columns(4)

card_data = [
    (c1, "red",    "🌐", "Tong Toan He Thong", str(tong_all),        "Tat ca thoi gian", "delta-neu"),
    (c2, "blue",   "📊", "Ky Dang Xem",         str(luot_loc),        loai_loc,           "delta-neu"),
    (c3, "orange", "⚡", "Hom Nay",             str(luot_hom_nay),    delta_str,          delta_class),
    (c4, "green",  "📱", "App Hoat Dong",        str(app_count),       "Trong ky chon",    "delta-neu"),
]

for col, color, icon, label, value, sub, dclass in card_data:
    with col:
        st.markdown(
            '<div class="metric-card ' + color + '">'
            '<span class="metric-icon">' + icon + '</span>'
            '<div class="metric-label">' + label + '</div>'
            '<div class="metric-value">' + value + '</div>'
            '<span class="metric-delta ' + dclass + '">' + sub + '</span>'
            '</div>',
            unsafe_allow_html=True
        )

if df_filtered.empty:
    st.warning("Khong co du lieu trong ky da chon.")
    st.stop()

# =============================================
# PLOTLY THEME
# =============================================
CHART_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Be Vietnam Pro', color='#94a3b8', size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(
        bgcolor='rgba(255,255,255,0.03)',
        bordercolor='rgba(255,255,255,0.08)',
        borderwidth=1,
        font=dict(size=11)
    )
)

# =============================================
# BIEU DO 1: Pie + Line
# =============================================
st.markdown('<div class="section-title">Phan tich tong quan</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 2])

with col1:
    df_app = df_filtered['ten_app'].value_counts().reset_index()
    df_app.columns = ['App', 'Luot']
    COLORS = ['#C8102E','#004B87','#ff9900','#10b981','#8b5cf6','#f43f5e','#0ea5e9']
    fig_pie = go.Figure(go.Pie(
        labels=df_app['App'], values=df_app['Luot'],
        hole=0.55,
        marker=dict(colors=COLORS[:len(df_app)], line=dict(color='#0a0e1a', width=2)),
        textinfo='percent',
        textfont=dict(size=11, family='Be Vietnam Pro'),
        hovertemplate="<b>%{label}</b><br>%{value} luot<br>%{percent}<extra></extra>"
    ))
    fig_pie.add_annotation(
        text="<b>" + str(luot_loc) + "</b><br>tong luot",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color='#e2e8f0', family='Be Vietnam Pro')
    )
    fig_pie.update_layout(
        title=dict(text="Ty trong theo App", font=dict(size=13, color='#94a3b8')),
        showlegend=True, **CHART_LAYOUT
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    df_day = df_filtered.groupby('Ngay').size().reset_index(name='Luot')
    df_day['sort_key'] = pd.to_datetime(df_day['Ngay'], format='%d/%m/%Y')
    df_day = df_day.sort_values('sort_key')
    df_day['MA7'] = df_day['Luot'].rolling(7, min_periods=1).mean()

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=df_day['Ngay'], y=df_day['Luot'],
        name='Luot truy cap',
        fill='tozeroy', fillcolor='rgba(200,16,46,0.08)',
        line=dict(color='#C8102E', width=2.5),
        marker=dict(size=6, color='#ff4d6d'),
        hovertemplate="<b>%{x}</b><br>%{y} luot<extra></extra>"
    ))
    if len(df_day) >= 3:
        fig_line.add_trace(go.Scatter(
            x=df_day['Ngay'], y=df_day['MA7'].round(1),
            name='Trung binh 7 ngay',
            line=dict(color='#60a5fa', width=1.5, dash='dot'),
            hovertemplate="<b>%{x}</b><br>TB: %{y}<extra></extra>"
        ))
    fig_line.update_layout(
        title=dict(text="Tang truong theo Ngay", font=dict(size=13, color='#94a3b8')),
        xaxis=dict(gridcolor='rgba(255,255,255,0.04)', tickangle=-30),
        yaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
        hovermode='x unified', **CHART_LAYOUT
    )
    st.plotly_chart(fig_line, use_container_width=True)

# =============================================
# BIEU DO 2: Gio + App ranking
# =============================================
st.markdown('<div class="section-title">Phan tich hanh vi</div>', unsafe_allow_html=True)
col3, col4 = st.columns(2)

with col3:
    df_hour = df_filtered.groupby('Gio').size().reset_index(name='Luot')
    all_hours = pd.DataFrame({'Gio': range(24)})
    df_hour = all_hours.merge(df_hour, on='Gio', how='left').fillna(0)

    fig_bar_hour = go.Figure(go.Bar(
        x=df_hour['Gio'], y=df_hour['Luot'],
        marker=dict(
            color=df_hour['Luot'],
            colorscale=[[0,'rgba(200,16,46,0.2)'],[1,'#C8102E']],
            line=dict(width=0)
        ),
        hovertemplate="<b>%{x}:00</b><br>%{y} luot<extra></extra>"
    ))
    tick_vals = list(range(0, 24, 2))
    fig_bar_hour.update_layout(
        title=dict(text="Phan bo theo Gio trong Ngay", font=dict(size=13, color='#94a3b8')),
        xaxis=dict(tickmode='array', tickvals=tick_vals,
                   ticktext=[str(h) + "h" for h in tick_vals],
                   gridcolor='rgba(255,255,255,0.04)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
        bargap=0.2, **CHART_LAYOUT
    )
    st.plotly_chart(fig_bar_hour, use_container_width=True)

with col4:
    df_app_bar = df_filtered['ten_app'].value_counts().reset_index()
    df_app_bar.columns = ['App', 'Luot']
    df_app_bar = df_app_bar.sort_values('Luot')

    fig_bar_app = go.Figure(go.Bar(
        x=df_app_bar['Luot'], y=df_app_bar['App'],
        orientation='h',
        marker=dict(
            color=df_app_bar['Luot'],
            colorscale=[[0,'rgba(0,75,135,0.3)'],[1,'#004B87']],
            line=dict(width=0)
        ),
        hovertemplate="<b>%{y}</b><br>%{x} luot<extra></extra>"
    ))
    fig_bar_app.update_layout(
        title=dict(text="Xep Hang Ung Dung", font=dict(size=13, color='#94a3b8')),
        xaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
        **CHART_LAYOUT
    )
    st.plotly_chart(fig_bar_app, use_container_width=True)

# =============================================
# INSIGHT TU DONG
# =============================================
st.markdown('<div class="section-title">Nhan xet tu dong</div>', unsafe_allow_html=True)

peak_hour = int(df_filtered.groupby('Gio').size().idxmax()) if not df_filtered.empty else 0
top_app   = df_filtered['ten_app'].value_counts().idxmax() if not df_filtered.empty else "—"
top_day   = df_filtered.groupby('Ngay').size().idxmax() if not df_filtered.empty else "—"
avg_day   = df_filtered.groupby('Ngay').size().mean() if not df_filtered.empty else 0

ins1, ins2, ins3, ins4 = st.columns(4)
insights = [
    (ins1, "Gio cao diem",  str(peak_hour) + ":00 – " + str(peak_hour+1) + ":00", "Luot truy cap dat dinh"),
    (ins2, "App dan dau",   top_app,                                                "Nhieu luot nhat ky nay"),
    (ins3, "Ngay ban nhat", top_day,                                                "Dinh truy cap trong ky"),
    (ins4, "TB moi ngay",   str(round(avg_day, 1)) + " luot",                      "Trong ky: " + loai_loc),
]
for col, title, val, sub in insights:
    with col:
        st.markdown(
            '<div class="insight-card">'
            '<div class="insight-title">' + title + '</div>'
            '<div class="insight-value">' + val + '</div>'
            '<div class="insight-sub">' + sub + '</div>'
            '</div>',
            unsafe_allow_html=True
        )

# =============================================
# BANG CHI TIET
# =============================================
st.markdown('<div class="section-title">Nhat ky chi tiet</div>', unsafe_allow_html=True)
with st.expander("Xem tat ca " + str(len(df_filtered)) + " ban ghi trong ky '" + loai_loc + "'"):
    df_show = df_filtered[['Thoi gian', 'ten_app']].sort_values('Thoi gian', ascending=False).copy()
    df_show['Thoi gian'] = df_show['Thoi gian'].dt.strftime('%H:%M:%S — %d/%m/%Y')
    df_show.columns = ['Thoi gian truy cap', 'Ten ung dung']
    df_show.index = range(1, len(df_show) + 1)
    st.dataframe(df_show, use_container_width=True, height=400)

# Footer
st.markdown(
    '<div style="text-align:center;padding:40px 0 20px;color:#1e293b;font-size:0.75rem;">'
    'He Sinh Thai Analytics Dashboard • Cap nhat tu dong moi 60 giay'
    '</div>',
    unsafe_allow_html=True
)
