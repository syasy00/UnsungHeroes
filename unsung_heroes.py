import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Unsung Heroes: PPS Relief Centers in Action", layout="wide")

# --- Load data ---
df = pd.read_csv('DATA_BANJIR_CLEANED.csv', parse_dates=['TARIKH BUKA'])

# --- Session state for select-all/reset logic ---
if "kategori_selected" not in st.session_state:
    st.session_state.kategori_selected = sorted(df['KATEGORI'].unique())
if "mukim_selected" not in st.session_state:
    st.session_state.mukim_selected = sorted(df['MUKIM'].unique())
if "daerah_selected" not in st.session_state:
    st.session_state.daerah_selected = sorted(df['DAERAH'].unique())

# --- Dashboard Title/Subtitle ---
st.markdown("<h1 style='margin-bottom:0;'>🦸‍♂️ Unsung Heroes: PPS Relief Centers in Action</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='margin-top:0;'>Real stories from the flood: Who sheltered the most? Who responded first? Where did evacuees come from—and where did they find safety?</h4>", unsafe_allow_html=True)

st.markdown("""
<div style='background-color:#f1f1f6; padding:12px; border-radius:8px; margin-bottom:18px;'>
<b>This dashboard reveals the journey of evacuees during Malaysia's floods, highlighting <span style='color:#eab308'>hero</span> relief centers (PPS) and their impact across districts and time.</b>
</div>
""", unsafe_allow_html=True)

# --- Sidebar filters with select all / reset ---
with st.sidebar:
    st.header("🧭 Filter data")
    st.markdown("---")
    negeri_unique = sorted(df['NEGERI'].unique())
    negeri = st.multiselect("Select Negeri (State)", negeri_unique, default=negeri_unique)
    st.markdown("---")

    # Kategori filter with Select All button
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

    # Mukim filter with Select All button
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

    # Daerah filter with Select All button
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

# --- Apply filters (no date filter) ---
filtered = df[
    df['NEGERI'].isin(negeri) &
    df['KATEGORI'].isin(kategori) &
    df['MUKIM'].isin(mukim) &
    df['DAERAH'].isin(daerah)
]

if filtered.empty:
    st.warning("No data available for the selected filters. Try broadening your filter selection.")
else:
    # --- Storytelling headline (dynamically generated) ---
    headline = f"**{filtered['JUMLAH'].sum():,} evacuees** from {len(filtered['DAERAH'].unique())} districts ({', '.join(filtered['DAERAH'].unique()[:3]) + ('...' if len(filtered['DAERAH'].unique()) > 3 else '')}) found shelter at {filtered['NAMA PPS'].nunique()} PPS across {', '.join(filtered['MUKIM'].unique()[:3]) + ('...' if len(filtered['MUKIM'].unique()) > 3 else '')}."
    st.markdown(f"<div style='background-color:#eef3fb; padding:12px; border-radius:8px; margin-bottom:10px;'><b>{headline}</b></div>", unsafe_allow_html=True)

    # --- Key Metrics ---
    total_evacuees = filtered['JUMLAH'].sum()
    num_pps = filtered['NAMA PPS'].nunique()
    pps_evacuees = filtered.groupby('NAMA PPS')['JUMLAH'].sum()
    if not pps_evacuees.empty:
        pps_max = pps_evacuees.idxmax()
        max_evacuees = pps_evacuees.max()
    else:
        pps_max = "-"
        max_evacuees = 0

    child_mask = filtered['KATEGORI'].str.contains("Kanak|Bayi", case=False, na=False)
    child_pps = filtered[child_mask].groupby('NAMA PPS')['JUMLAH'].sum()
    if not child_pps.empty:
        most_child_pps = child_pps.idxmax()
    else:
        most_child_pps = "-"

    earliest_pps = filtered.loc[filtered['TARIKH BUKA'] == filtered['TARIKH BUKA'].min(), 'NAMA PPS'].values[0] if not filtered.empty else "-"

    # --- Pretty metrics section ---
    st.markdown(
        f"""
        <div style="background-color:#feefd4;padding:12px;border-radius:8px;margin-bottom:10px;">
        <b>Total Evacuees:</b> <span style='font-size:1.4em;color:#2563eb'><b>{total_evacuees:,}</b></span> &nbsp;&nbsp; | &nbsp;&nbsp; 
        <b>Total PPS:</b> <span style='font-size:1.4em;color:#16a34a'><b>{num_pps}</b></span><br>
        <ul>
            <li>🟧 <b>Largest PPS:</b> <b>{pps_max}</b> ({max_evacuees:,} evacuees)</li>
            <li>🟥 <b>PPS with Most Children/Infants:</b> <b>{most_child_pps}</b></li>
            <li>🟩 <b>First PPS to Open:</b> <b>{earliest_pps}</b></li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("### 🏆 Top 10 Relief Centers (PPS) by Total Evacuees")
    st.caption("See which centers carried the heaviest load. Hover to see totals.")

    # --- Leaderboard of PPS (Bar Chart) ---
    pps_sum = filtered.groupby('NAMA PPS')['JUMLAH'].sum().sort_values(ascending=False).reset_index()
    fig_bar = px.bar(
        pps_sum.head(10), 
        x='JUMLAH', y='NAMA PPS',
        orientation='h',
        labels={'JUMLAH': 'Total Evacuees', 'NAMA PPS': 'PPS'},
        title=""
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- Storytelling Map of PPS ---
    st.markdown("---")
    st.markdown("### 🗺️ Hero PPS Centers and Their Locations")
    st.caption("Map highlights hero PPS—hover for more. Orange: Largest, Red: Most Children, Green: First to Open.")

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
        }
    )
    fig_map.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":30,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🔄 How Districts Sent Evacuees to Relief Centers")
    st.caption("See the flow of evacuees from each Daerah to PPS (Sankey).")
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

    st.markdown("---")
    st.markdown("### 👨‍👩‍👧‍👦 Who Did the PPS Serve? (Breakdown by Category)")
    st.caption("Which centers sheltered more children, elderly, or other categories?")
    pps_demo = filtered.groupby(['NAMA PPS','KATEGORI'])['JUMLAH'].sum().reset_index()
    fig_demo = px.bar(
        pps_demo, 
        x='NAMA PPS', y='JUMLAH', color='KATEGORI',
        title="",
        labels={'JUMLAH':'Total Evacuees', 'NAMA PPS':'PPS'},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_demo, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📈 When Did People Arrive? (Timeline of Arrivals)")
    st.caption("See the rhythm of arrivals—when were the busiest days or times?")
    date_sum = filtered.groupby('TARIKH BUKA')['JUMLAH'].sum().reset_index()
    fig_line = px.line(
        date_sum, 
        x='TARIKH BUKA', y='JUMLAH',
        labels={'TARIKH BUKA':'Date Opened', 'JUMLAH':'Total Evacuees'},
        title=""
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown(
        "<div style='background-color:#d1fae5; padding:12px; border-radius:8px;'>"
        "Explore the filters to see which districts sent people to which PPS, who the centers sheltered, and when. "
        "<b>Hero PPS are highlighted. The story updates as you change filters!</b>"
        "</div>",
        unsafe_allow_html=True
    )
