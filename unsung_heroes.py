import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set up the page configuration
st.set_page_config(page_title="Unsung Heroes: PPS Relief Centers in Action", layout="wide")

# --- Dashboard CSS ---
st.markdown("""
<style>
    .dashboard-title {
        font-size:2.3em; font-weight:900; letter-spacing:-1px; margin-bottom:0;
    }
    .dashboard-subtitle {
        font-size:1.1em; font-weight:400; color:#555; margin-bottom:18px;
    }
    .card {
        background: #fff;
        border-radius: 13px;
        box-shadow: 0 3px 14px rgba(30,30,60,0.10);
        padding: 22px 28px 13px 28px;
        margin-bottom: 18px;
        min-height: 100px;
    }
    @media (prefers-color-scheme: dark) {
        .card {background: #202127 !important; color: #f3f6fc !important;}
    }
    .kpi-big {
        font-size:2.1em;
        font-weight:bold;
        margin-bottom:3px;
        color: #2563eb;
    }
    .kpi-label {
        font-size:1.05em;
        color: #888;
        font-weight:600;
        margin-bottom: 2px;
    }
    .kpi-sub {
        color:#1abc9c; font-size:1.13em; font-weight:600; margin-bottom:4px;
    }
    .card .big-list {font-size:1.1em;}
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
df = pd.read_csv('DATA_BANJIR_CLEANED.csv', parse_dates=['TARIKH BUKA'])

# --- Session state for select-all/reset logic ---
if "kategori_selected" not in st.session_state:
    st.session_state.kategori_selected = sorted(df['KATEGORI'].unique())
if "mukim_selected" not in st.session_state:
    st.session_state.mukim_selected = sorted(df['MUKIM'].unique())
if "daerah_selected" not in st.session_state:
    st.session_state.daerah_selected = sorted(df['DAERAH'].unique())

# --- SIDEBAR: Filter controls ---
with st.sidebar:
    st.header("🧭 Filter data")
    st.markdown("---")
    negeri_unique = sorted(df['NEGERI'].unique())
    negeri = st.multiselect("Select Negeri (State)", negeri_unique, default=negeri_unique)
    st.markdown("---")
    kategori_unique = sorted(df['KATEGORI'].unique())
    if st.button("Select All Kategori"):
        st.session_state.kategori_selected = kategori_unique
    kategori = st.multiselect(
        "Select Category", 
        kategori_unique, 
        default=[k for k in st.session_state.kategori_selected if k in kategori_unique], 
        key='kategori_selected'
    )
    st.markdown("---")
    mukim_unique = sorted(df[df['NEGERI'].isin(negeri) & df['KATEGORI'].isin(kategori)]['MUKIM'].unique())
    if st.button("Select All Mukim"):
        st.session_state.mukim_selected = mukim_unique
    mukim = st.multiselect(
        "Select Mukim", 
        mukim_unique, 
        default=[m for m in st.session_state.mukim_selected if m in mukim_unique], 
        key='mukim_selected'
    )
    st.markdown("---")
    daerah_unique = sorted(df[df['NEGERI'].isin(negeri) & df['KATEGORI'].isin(kategori) & df['MUKIM'].isin(mukim)]['DAERAH'].unique())
    if st.button("Select All Daerah"):
        st.session_state.daerah_selected = daerah_unique
    daerah = st.multiselect(
        "Select Daerah", 
        daerah_unique, 
        default=[d for d in st.session_state.daerah_selected if d in daerah_unique], 
        key='daerah_selected'
    )
    st.markdown("---")
    st.download_button("⬇️ Download Cleaned Data", data=df.to_csv(index=False), file_name="filtered_DATA_BANJIR.csv")

# --- FILTER DATA ---
filtered = df[
    df['NEGERI'].isin(negeri) &
    df['KATEGORI'].isin(kategori) &
    df['MUKIM'].isin(mukim) &
    df['DAERAH'].isin(daerah)
]

# --- DASHBOARD HEADER ---
st.markdown('<div class="dashboard-title">🦸‍♂️ Unsung Heroes: PPS Relief Centers in Action</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">Real stories from the flood: Who sheltered the most? Who responded first? Where did evacuees come from—and where did they find safety?</div>', unsafe_allow_html=True)

# --- KPIs in Cards ---
total_evacuees = filtered['JUMLAH'].sum()
num_pps = filtered['NAMA PPS'].nunique()
pps_evacuees = filtered.groupby('NAMA PPS')['JUMLAH'].sum()
pps_max = pps_evacuees.idxmax() if not pps_evacuees.empty else "-"
max_evacuees = pps_evacuees.max() if not pps_evacuees.empty else 0
child_mask = filtered['KATEGORI'].str.contains("Kanak|Bayi", case=False, na=False)
child_pps = filtered[child_mask].groupby('NAMA PPS')['JUMLAH'].sum()
most_child_pps = child_pps.idxmax() if not child_pps.empty else "-"
earliest_pps = filtered.loc[filtered['TARIKH BUKA'] == filtered['TARIKH BUKA'].min(), 'NAMA PPS'].values[0] if not filtered.empty else "-"
num_districts = filtered['DAERAH'].nunique()

# ---- KPI "cards" ----
kpi1, kpi2, kpi3, kpi4 = st.columns([1,1,1,1])
with kpi1:
    st.markdown('<div class="card"><div class="kpi-label">Total Evacuees</div><div class="kpi-big">{:,}</div></div>'.format(total_evacuees), unsafe_allow_html=True)
with kpi2:
    st.markdown('<div class="card"><div class="kpi-label">Total PPS</div><div class="kpi-big">{}</div></div>'.format(num_pps), unsafe_allow_html=True)
with kpi3:
    st.markdown('<div class="card"><div class="kpi-label">Largest PPS</div><div class="kpi-big">{}</div><div class="kpi-sub">{:,} evacuees</div></div>'.format(pps_max, max_evacuees), unsafe_allow_html=True)
with kpi4:
    st.markdown('<div class="card"><div class="kpi-label">Districts</div><div class="kpi-big">{}</div></div>'.format(num_districts), unsafe_allow_html=True)

# ---- KPI highlights list card (centered) ----
st.markdown(
    f"""<div class="card big-list">
    <ul>
    <li>🟧 <b>Largest PPS:</b> <b>{pps_max}</b> ({max_evacuees:,} evacuees)</li>
    <li>🟥 <b>PPS with Most Children/Infants:</b> <b>{most_child_pps}</b></li>
    <li>🟩 <b>First PPS to Open:</b> <b>{earliest_pps}</b></li>
    </ul>
    </div>
    """, unsafe_allow_html=True
)
