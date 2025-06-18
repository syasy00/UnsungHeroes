import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set the page config
st.set_page_config(page_title="Unsung Heroes: PPS Relief Centers in Action", layout="wide")

# --- Dashboard CSS: cards, KPIs, dark mode aware ---
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
st.markdown(
    "<div class='card'>"
    "<b>This dashboard reveals the journey of evacuees during Malaysia's floods, highlighting <span style='color:#eab308'>hero</span> relief centers (PPS) and their impact across districts and time.</b>"
    "</div>",
    unsafe_allow_html=True
)

# Check if the filtered data is empty
if filtered.empty:
    st.warning("No data available for the selected filters. Try broadening your filter selection.")
else:
    # --- KPIs ---
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

    # --- BAR + PIE ---
    row2_col1, row2_col2 = st.columns([2,1])
    with row2_col1:
        if not filtered.empty:
            pps_sum = filtered.groupby('NAMA PPS')['JUMLAH'].sum().sort_values(ascending=False).reset_index()
            fig_bar = px.bar(pps_sum.head(10), x='JUMLAH', y='NAMA PPS', orientation='h', labels={'JUMLAH': 'Total Evacuees', 'NAMA PPS': 'PPS'})
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No data available to display Top 10 Relief Centers.")

    with row2_col2:
        if not filtered.empty:
            cat_sum = filtered.groupby('KATEGORI')['JUMLAH'].sum().reset_index()
            fig_pie = px.pie(cat_sum, names='KATEGORI', values='JUMLAH', title="Category Share")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No data available for category share.")

    # --- MAP + SANKEY ---
    mapcol, sankeycol = st.columns([2,2])
    with mapcol:
        if not filtered.empty:
            st.markdown("**Hero PPS Centers and Their Locations**")
            filtered['HERO STATUS'] = 'Regular'
            if pps_max and pps_max != "-":
                filtered.loc[filtered['NAMA PPS'] == pps_max, 'HERO STATUS'] = 'Largest Center'
            if most_child_pps and most_child_pps != "-":
                filtered.loc[filtered['NAMA PPS'] == most_child_pps, 'HERO STATUS'] = 'Most Children/Infants'
            if earliest_pps and earliest_pps != "-":
                filtered.loc[filtered['NAMA PPS'] == earliest_pps, 'HERO STATUS'] = 'First to Open'
            
            fig_map = px.scatter_mapbox(
                filtered,
                lat='Latitude', lon='Longitude',
                size='JUMLAH',
                color='HERO STATUS',
                hover_name='NAMA PPS',
                hover_data={'JUMLAH':True, 'KATEGORI':True, 'DAERAH':True, 'MUKIM':True, 'HERO STATUS':True},
                zoom=8,
                height=500,
                color_discrete_map={
                    'Regular': 'skyblue',
                    'Largest Center': 'orange',
                    'Most Children/Infants': 'red',
                    'First to Open': 'green'
                },
                mapbox_style="carto-positron"
            )
            fig_map.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No data available to display map.")
    with sankeycol:
        if not filtered.empty:
            st.markdown("**How Districts Sent Evacuees to Relief Centers**")
            sankey_data = filtered.groupby(['DAERAH', 'NAMA PPS'])['JUMLAH'].sum().reset_index()
            if not sankey_data.empty:
                labels = list(pd.concat([sankey_data['DAERAH'], sankey_data['NAMA PPS']]).unique())
                label_indices = {label: i for i, label in enumerate(labels)}
                sankey_fig = go.Figure(go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=15,
                        line=dict(color="black", width=0.5),
                        label=labels,
                    ),
                    link=dict(
                        source=[label_indices[d] for d in sankey_data['DAERAH']],
                        target=[label_indices[p] for p in sankey_data['NAMA PPS']],
                        value=sankey_data['JUMLAH']
                    )
                ))
                sankey_fig.update_layout(title_text="", font_size=12, height=400)
                st.plotly_chart(sankey_fig, use_container_width=True)
            else:
                st.info("Not enough data to show district-to-PPS flow for current filter.")

    # --- CATEGORY STACKED BAR + ARRIVAL TIMELINE ---
    demo_col, timeline_col = st.columns([2,2])
    with demo_col:
        if not filtered.empty:
            pps_demo = filtered.groupby(['NAMA PPS','KATEGORI'])['JUMLAH'].sum().reset_index()
            fig_demo = px.bar(
                pps_demo, 
                x='NAMA PPS', y='JUMLAH', color='KATEGORI',
                labels={'JUMLAH':'Total Evacuees', 'NAMA PPS':'PPS'},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_demo, use_container_width=True)
        else:
            st.info("No data available to show demographic breakdown.")

    with timeline_col:
        if not filtered.empty:
            date_sum = filtered.groupby('TARIKH BUKA')['JUMLAH'].sum().reset_index()
            fig_line = px.line(
                date_sum, 
                x='TARIKH BUKA', y='JUMLAH',
                labels={'TARIKH BUKA':'Date Opened', 'JUMLAH':'Total Evacuees'},
                title=""
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No data available for timeline of arrivals.")

    # --- Final Info Card ---
    st.markdown(
        "<div class='card'>"
        "Explore the filters to see which districts sent people to which PPS, who the centers sheltered, and when. "
        "<b>Hero PPS are highlighted. The story updates as you change filters!</b>"
        "</div>",
        unsafe_allow_html=True
    )
