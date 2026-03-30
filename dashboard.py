import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(
    page_title="COSMAX 시제품 분석",
    page_icon="🧴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 글로벌 CSS (다크 + 글래스모피즘) ─────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── 전체 배경 ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #080b14 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stHeader"] { background: transparent !important; }

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background: rgba(124,58,237,0.3) !important;
    border: 1px solid rgba(124,58,237,0.5) !important;
    border-radius: 999px !important;
}

/* ── 메인 텍스트 ── */
h1, h2, h3, h4, p, span, label, div {
    color: #e6edf3 !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── 글래스모피즘 KPI 카드 ── */
.kpi-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 16px 16px 0 0;
}
.kpi-card.purple::before { background: linear-gradient(90deg, #7c3aed, #a78bfa); }
.kpi-card.blue::before   { background: linear-gradient(90deg, #2563eb, #60a5fa); }
.kpi-card.green::before  { background: linear-gradient(90deg, #059669, #34d399); }
.kpi-card.orange::before { background: linear-gradient(90deg, #d97706, #fbbf24); }
.kpi-card.pink::before   { background: linear-gradient(90deg, #db2777, #f472b6); }

.kpi-icon   { font-size: 1.6rem; margin-bottom: 10px; }
.kpi-value  { font-size: 2.4rem; font-weight: 700; line-height: 1; margin-bottom: 6px; }
.kpi-label  { font-size: 0.78rem; color: #7d8590 !important;
              text-transform: uppercase; letter-spacing: 0.08em; font-weight: 500; }

.kpi-card.purple .kpi-value { color: #a78bfa !important; }
.kpi-card.blue   .kpi-value { color: #60a5fa !important; }
.kpi-card.green  .kpi-value { color: #34d399 !important; }
.kpi-card.orange .kpi-value { color: #fbbf24 !important; }
.kpi-card.pink   .kpi-value { color: #f472b6 !important; }

/* ── 섹션 타이틀 ── */
.section-title {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #7d8590 !important;
    margin: 28px 0 12px;
    padding-left: 2px;
}

/* ── 차트 카드 래퍼 ── */
.chart-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 4px;
    margin-bottom: 4px;
}

/* ── 구분선 ── */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* ── 데이터프레임 ── */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* ── 업로드 박스 ── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1.5px dashed rgba(124,58,237,0.4) !important;
    border-radius: 14px !important;
    padding: 12px !important;
}

/* ── 다운로드 버튼 ── */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
}

/* ── info 박스 ── */
[data-testid="stAlert"] {
    background: rgba(124,58,237,0.1) !important;
    border: 1px solid rgba(124,58,237,0.25) !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Plotly 다크 템플릿 ────────────────────────────────────────────────────
DARK_BG   = "#0d1117"
CARD_BG   = "#0f131a"
GRID_CLR  = "rgba(255,255,255,0.06)"
TEXT_CLR  = "#c9d1d9"
PALETTE   = ["#7c3aed","#2563eb","#059669","#d97706","#db2777",
             "#0891b2","#65a30d","#9333ea","#ea580c","#0284c7"]

def dark_layout(fig, height=360, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color=TEXT_CLR, family="Inter"), x=0.02, y=0.97),
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT_CLR, family="Inter"),
        height=height,
        margin=dict(l=16, r=16, t=44, b=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        xaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR, tickfont=dict(size=11)),
        yaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR, tickfont=dict(size=11)),
    )
    return fig

# ── 헤더 ────────────────────────────────────────────────────────────────
col_title, col_badge = st.columns([6, 1])
with col_title:
    st.markdown("""
    <h1 style="font-size:1.8rem;font-weight:700;margin-bottom:4px;">
        🧴 COSMAX 시제품 분석 대시보드
    </h1>
    <p style="color:#7d8590;font-size:0.87rem;margin-top:0;">
        엑셀 파일을 업로드하면 데이터를 자동으로 시각화합니다
    </p>
    """, unsafe_allow_html=True)

st.markdown('<hr/>', unsafe_allow_html=True)

# ── 파일 업로드 ──────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "📂 엑셀 파일 업로드 (.xlsx)",
    type=["xlsx"],
    label_visibility="collapsed",
)

if uploaded is None:
    st.markdown("""
    <div style="text-align:center;padding:60px 0;color:#7d8590;">
        <div style="font-size:3rem;margin-bottom:16px;">📊</div>
        <div style="font-size:1rem;font-weight:600;color:#c9d1d9;margin-bottom:8px;">
            엑셀 파일을 드래그하거나 클릭해서 업로드하세요
        </div>
        <div style="font-size:0.82rem;">
            .xlsx 형식 지원 · dummy_cosmax_data.xlsx 형식
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── 데이터 로드 ──────────────────────────────────────────────────────────
@st.cache_data
def load_data(file_bytes: bytes) -> pd.DataFrame:
    df = pd.read_excel(BytesIO(file_bytes))
    if "작성일" in df.columns:
        df["작성일"] = pd.to_datetime(df["작성일"])
        df["월"] = df["작성일"].dt.to_period("M").astype(str)
    return df

df = load_data(uploaded.read())

REQUIRED = {"제품유형", "제형", "개발단계", "목표피부타입", "주요컨셉", "담당팀"}
missing = REQUIRED - set(df.columns)
if missing:
    st.error(f"필수 컬럼 없음: {missing}")
    st.stop()

# ── 사이드바 필터 ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:4px 0 16px;">
        <div style="font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;
                    color:#7d8590;font-weight:600;margin-bottom:12px;">FILTERS</div>
    </div>
    """, unsafe_allow_html=True)

    sel_팀 = st.multiselect("담당팀", options=sorted(df["담당팀"].unique()),
                            default=sorted(df["담당팀"].unique()))
    sel_단계 = st.multiselect("개발단계", options=sorted(df["개발단계"].unique()),
                              default=sorted(df["개발단계"].unique()))
    sel_유형 = st.multiselect("제품유형", options=sorted(df["제품유형"].unique()),
                              default=sorted(df["제품유형"].unique()))
    sel_피부 = st.multiselect("목표피부타입", options=sorted(df["목표피부타입"].unique()),
                              default=sorted(df["목표피부타입"].unique()))

    st.markdown('<hr/>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:0.75rem;color:#7d8590;text-align:center;">
        총 <span style="color:#a78bfa;font-weight:600;">{len(df)}</span>개 레코드 로드됨
    </div>
    """, unsafe_allow_html=True)

fdf = df[
    df["담당팀"].isin(sel_팀) &
    df["개발단계"].isin(sel_단계) &
    df["제품유형"].isin(sel_유형) &
    df["목표피부타입"].isin(sel_피부)
]

# ── KPI 카드 ─────────────────────────────────────────────────────────────
kpis = [
    ("purple", "📦", str(len(fdf)),              "전체 시제품"),
    ("blue",   "🏷️", str(fdf["제품유형"].nunique()), "제품 유형"),
    ("green",  "👥", str(fdf["담당팀"].nunique()),  "담당팀"),
    ("orange", "🔬", str(fdf["개발단계"].nunique()), "개발단계"),
    ("pink",   "💡", str(fdf["주요컨셉"].nunique()), "주요컨셉"),
]

cols = st.columns(5, gap="small")
for col, (color, icon, value, label) in zip(cols, kpis):
    col.markdown(f"""
    <div class="kpi-card {color}">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-title">제품 구성 현황</div>', unsafe_allow_html=True)

# ── 차트 1행 ─────────────────────────────────────────────────────────────
c1, c2 = st.columns([3, 2], gap="small")

with c1:
    cnt = fdf["제품유형"].value_counts().reset_index()
    cnt.columns = ["제품유형", "건수"]
    fig = px.bar(cnt, x="제품유형", y="건수", color="제품유형",
                 color_discrete_sequence=PALETTE, text="건수")
    fig.update_traces(textposition="outside", textfont=dict(size=12, color=TEXT_CLR),
                      marker_line_width=0)
    fig.update_layout(showlegend=False)
    dark_layout(fig, 320, "제품유형별 시제품 수")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with c2:
    cnt = fdf["개발단계"].value_counts().reset_index()
    cnt.columns = ["개발단계", "건수"]
    fig = px.pie(cnt, names="개발단계", values="건수",
                 color_discrete_sequence=PALETTE, hole=0.55)
    fig.update_traces(textposition="inside", textinfo="percent+label",
                      textfont=dict(size=11), marker=dict(line=dict(color=CARD_BG, width=2)))
    fig.add_annotation(text=f"<b>{len(fdf)}</b><br><span style='font-size:10px'>Total</span>",
                       x=0.5, y=0.5, showarrow=False, font=dict(size=18, color=TEXT_CLR))
    dark_layout(fig, 320, "개발단계 분포")
    fig.update_layout(showlegend=True,
                      legend=dict(orientation="v", x=0.85, y=0.5,
                                  font=dict(size=10), bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── 차트 2행 ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">팀 · 컨셉 · 피부타입 분석</div>', unsafe_allow_html=True)
c3, c4, c5 = st.columns(3, gap="small")

with c3:
    cnt = fdf["담당팀"].value_counts().reset_index()
    cnt.columns = ["담당팀", "건수"]
    fig = px.bar(cnt, x="건수", y="담당팀", orientation="h",
                 color="건수", color_continuous_scale=["#1e1b4b","#7c3aed","#a78bfa"],
                 text="건수")
    fig.update_traces(textposition="outside", textfont=dict(size=12, color=TEXT_CLR),
                      marker_line_width=0)
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    dark_layout(fig, 300, "담당팀별 시제품 수")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with c4:
    cnt = fdf["주요컨셉"].value_counts().reset_index()
    cnt.columns = ["주요컨셉", "건수"]
    fig = px.bar(cnt, x="주요컨셉", y="건수", color="건수",
                 color_continuous_scale=["#1e3a5f","#2563eb","#60a5fa"],
                 text="건수")
    fig.update_traces(textposition="outside", textfont=dict(size=12, color=TEXT_CLR),
                      marker_line_width=0)
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    dark_layout(fig, 300, "주요컨셉별 시제품 수")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with c5:
    cnt = fdf["목표피부타입"].value_counts().reset_index()
    cnt.columns = ["목표피부타입", "건수"]
    fig = px.pie(cnt, names="목표피부타입", values="건수",
                 color_discrete_sequence=["#059669","#10b981","#34d399","#6ee7b7"],
                 hole=0.5)
    fig.update_traces(textposition="inside", textinfo="percent+label",
                      textfont=dict(size=10), marker=dict(line=dict(color=CARD_BG, width=2)))
    dark_layout(fig, 300, "목표피부타입 분포")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── 차트 3행: 제형 크로스 + 히트맵 ──────────────────────────────────────
st.markdown('<div class="section-title">크로스 분석</div>', unsafe_allow_html=True)
c6, c7 = st.columns([3, 2], gap="small")

with c6:
    cross = fdf.groupby(["제형", "제품유형"]).size().reset_index(name="건수")
    fig = px.bar(cross, x="제형", y="건수", color="제품유형",
                 barmode="stack", color_discrete_sequence=PALETTE, text="건수")
    fig.update_traces(textposition="inside", textfont=dict(size=10, color="white"),
                      marker_line_width=0)
    dark_layout(fig, 320, "제형 × 제품유형 크로스 분석")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with c7:
    pivot = fdf.pivot_table(index="담당팀", columns="개발단계", aggfunc="size", fill_value=0)
    fig = px.imshow(pivot, text_auto=True, aspect="auto",
                    color_continuous_scale=["#0d1117","#7c3aed","#a78bfa"])
    fig.update_traces(textfont=dict(size=12, color="white"))
    dark_layout(fig, 320, "팀 × 개발단계 히트맵")
    fig.update_layout(coloraxis_showscale=False,
                      xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                      yaxis=dict(gridcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── 월별 추이 ─────────────────────────────────────────────────────────────
if "월" in fdf.columns:
    st.markdown('<div class="section-title">시계열 추이</div>', unsafe_allow_html=True)
    monthly = fdf.groupby("월").size().reset_index(name="건수")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["월"], y=monthly["건수"],
        mode="lines+markers+text",
        text=monthly["건수"],
        textposition="top center",
        textfont=dict(size=11, color="#a78bfa"),
        line=dict(color="#7c3aed", width=2.5),
        marker=dict(size=8, color="#a78bfa", line=dict(color=CARD_BG, width=2)),
        fill="tozeroy",
        fillcolor="rgba(124,58,237,0.08)",
    ))
    dark_layout(fig, 280, "월별 시제품 등록 추이")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── 데이터 테이블 ─────────────────────────────────────────────────────────
st.markdown('<div class="section-title">원본 데이터</div>', unsafe_allow_html=True)

c_search, c_dl = st.columns([4, 1], gap="small")
with c_search:
    search = st.text_input("", placeholder="🔍  검색어 입력...", label_visibility="collapsed")
with c_dl:
    buf = BytesIO()
    fdf.to_excel(buf, index=False)
    st.download_button("📥 다운로드", data=buf.getvalue(),
                       file_name="filtered_cosmax_data.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)

display_df = fdf[fdf.apply(lambda r: search.lower() in str(r.values).lower(), axis=1)] if search else fdf
st.dataframe(display_df, use_container_width=True, height=300,
             column_config={"작성일": st.column_config.DateColumn("작성일", format="YYYY-MM-DD")})

st.markdown(f"""
<div style="text-align:right;font-size:0.75rem;color:#7d8590;margin-top:8px;">
    {len(display_df)}개 행 표시 중
</div>
""", unsafe_allow_html=True)
