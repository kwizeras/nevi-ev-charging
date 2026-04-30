"""
NEVI Dashboard: Interactive U.S. EV Charging Infrastructure Explorer

Run locally: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

from utils import (
    load_station_data,
    compute_state_summary,
    compute_deployment_timeline,
    compute_network_breakdown,
    enrich_with_metadata,
    get_eva_response,
    _get_secret,
)

# Page config
st.set_page_config(
    page_title="NEVI Dashboard | EV Charging Infrastructure",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/kwizeras/nevi-ev-charging",
        "Report a bug": "https://github.com/kwizeras/nevi-ev-charging/issues",
        "About": (
            "## NEVI EV Charging Dashboard\n"
            "Built by **Sotaire Kwizera** for DEVP 226 at UC Berkeley.\n\n"
            "An interactive analysis of 80,000+ U.S. EV charging stations from the "
            "Alternative Fuels Data Center, with an embedded AI assistant (EVA) powered "
            "by Google Gemini."
        ),
    },
)

# Custom CSS for floating chat button and chat interface
st.markdown("""
<style>
    /* Floating chat button */
    .floating-chat-btn {
        position: fixed;
        bottom: 24px;
        right: 24px;
        width: 64px;
        height: 64px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .floating-chat-btn:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Chat container */
    .eva-chat-container {
        position: fixed;
        bottom: 100px;
        right: 24px;
        width: 380px;
        max-height: 500px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 5px 40px rgba(0,0,0,0.16);
        z-index: 9998;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }
    
    /* Chat header */
    .eva-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .eva-header h3 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
    }
    .eva-header p {
        margin: 0;
        font-size: 12px;
        opacity: 0.9;
    }
    .eva-avatar {
        width: 40px;
        height: 40px;
        background: rgba(255,255,255,0.2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    
    /* Chat messages area */
    .eva-messages {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        background: #f8f9fa;
        max-height: 300px;
    }
    
    .message {
        margin-bottom: 12px;
        display: flex;
        flex-direction: column;
    }
    .message.user {
        align-items: flex-end;
    }
    .message.eva {
        align-items: flex-start;
    }
    .message-bubble {
        max-width: 85%;
        padding: 10px 14px;
        border-radius: 16px;
        font-size: 14px;
        line-height: 1.4;
    }
    .message.user .message-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-bottom-right-radius: 4px;
    }
    .message.eva .message-bubble {
        background: white;
        color: #333;
        border-bottom-left-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Metrics styling - ensure visibility in both light and dark themes */
    [data-testid="stMetric"] {
        background-color: #1e3a5f !important;
        padding: 15px 20px !important;
        border-radius: 10px !important;
        border: 1px solid #2d5a87 !important;
    }
    
    [data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 14px !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #10b981 !important;
    }
    
    /* Hide default streamlit elements in chat */
    .chat-input-container {
        padding: 12px 16px;
        background: white;
        border-top: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_data():
    """Load station data, auto-fetching from NREL API on first boot."""
    data_path = Path("data/afdc_stations.csv")

    if not data_path.exists():
        api_key = _get_secret("NREL_API_KEY")
        if not api_key or api_key == "your_nrel_api_key_here":
            st.error(
                "⚠️ **NREL_API_KEY not configured.**  \n"
                "Set it in *App settings → Secrets* on Streamlit Cloud, "
                "or in a local `.env` file. Get a free key at "
                "[developer.nrel.gov/signup](https://developer.nrel.gov/signup/)."
            )
            st.stop()

        with st.spinner(
            "⚡ First-time setup: fetching ~80,000 charging stations "
            "from the NREL API. This takes ~2 minutes — only happens once."
        ):
            try:
                from fetch_data import fetch_all_stations, clean_and_enrich
                data_path.parent.mkdir(parents=True, exist_ok=True)
                df_raw = fetch_all_stations(api_key)
                if df_raw.empty:
                    st.error("❌ No data returned from NREL. Check your API key.")
                    st.stop()
                df = clean_and_enrich(df_raw)
                df.to_csv(data_path, index=False)
                st.success(f"✅ Loaded {len(df):,} stations. Rerun complete!")
            except Exception as exc:  # noqa: BLE001
                st.error(f"❌ Failed to fetch data from NREL: {exc}")
                st.stop()

    return load_station_data(str(data_path))


def render_eva_chat(df_filtered):
    """Render the EVA chat interface in the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 EVA - EV Analysis Assistant")
    st.sidebar.caption("Ask questions about the charging data")
    
    # Initialize chat history
    if "eva_messages" not in st.session_state:
        st.session_state.eva_messages = [
            {"role": "eva", "content": "Hi! I'm EVA, your EV Analysis Assistant. Ask me anything about U.S. charging infrastructure! 🔌"}
        ]
    
    # Display chat messages in sidebar
    for msg in st.session_state.eva_messages[-6:]:  # Show last 6 messages
        if msg["role"] == "eva":
            st.sidebar.markdown(f"🤖 **EVA:** {msg['content']}")
        else:
            st.sidebar.markdown(f"👤 **You:** {msg['content']}")
    
    # Chat input
    user_input = st.sidebar.text_input(
        "Ask EVA:",
        key="eva_input",
        placeholder="e.g., Which state leads in DCFC?",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        ask_btn = st.button("Ask EVA", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️", help="Clear chat"):
            st.session_state.eva_messages = [
                {"role": "eva", "content": "Chat cleared! How can I help you? 🔌"}
            ]
            st.rerun()
    
    if ask_btn and user_input:
        # Add user message
        st.session_state.eva_messages.append({"role": "user", "content": user_input})
        
        # Get EVA response
        with st.sidebar:
            with st.spinner("EVA is thinking..."):
                response = get_eva_response(user_input, df_filtered)
        
        # Add EVA response
        st.session_state.eva_messages.append({"role": "eva", "content": response})
        st.rerun()


def main():
    # Header
    st.title("⚡ U.S. EV Charging Infrastructure Dashboard")
    st.markdown(
        """
        <div style="color: #cbd5e1; font-size: 15px; margin-bottom: 8px;">
            Explore public EV charging deployment across all 50 states + D.C. — filter,
            visualize, compare, and ask <strong style="color: #a5b4fc;">EVA</strong> any question.
        </div>
        <div style="color: #94a3b8; font-size: 13px;">
            Data: <a href="https://afdc.energy.gov/" target="_blank" style="color: #a5b4fc;">Alternative Fuels Data Center (AFDC)</a>
            via the NREL API &middot; <a href="https://kwizeras.github.io/nevi-ev-charging/" target="_blank" style="color: #a5b4fc;">Read the research paper →</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Load data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # State filter
    all_states = sorted(df["state"].unique())
    selected_states = st.sidebar.multiselect(
        "Select States",
        options=all_states,
        default=all_states,
        help="Filter by state(s)"
    )
    
    # Charger type filter
    charger_types = df["charger_type"].unique().tolist()
    selected_chargers = st.sidebar.multiselect(
        "Charger Type",
        options=charger_types,
        default=charger_types,
    )
    
    # Status filter
    statuses = df["status"].unique().tolist()
    selected_statuses = st.sidebar.multiselect(
        "Status",
        options=statuses,
        default=["Available"],
    )
    
    # Network filter
    networks = df["ev_network"].dropna().unique().tolist()
    networks = sorted([n for n in networks if pd.notna(n)])
    selected_networks = st.sidebar.multiselect(
        "Charging Network",
        options=networks,
        default=networks,
    )
    
    # Year range filter
    if df["open_year"].notna().any():
        min_year = int(df["open_year"].min())
        max_year = int(df["open_year"].max())
        year_range = st.sidebar.slider(
            "Year Opened",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
        )
    else:
        year_range = None
    
    # Apply filters
    mask = (
        (df["state"].isin(selected_states)) &
        (df["charger_type"].isin(selected_chargers)) &
        (df["status"].isin(selected_statuses))
    )
    if selected_networks:
        mask &= df["ev_network"].isin(selected_networks)
    if year_range:
        mask &= (df["open_year"] >= year_range[0]) & (df["open_year"] <= year_range[1])
    
    df_filtered = df[mask].copy()
    
    # Render EVA chat in sidebar
    render_eva_chat(df_filtered)
    
    # Key metrics
    st.header("📊 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Stations", f"{len(df_filtered):,}")
    with col2:
        dcfc_count = (df_filtered["charger_type"] == "DCFC").sum()
        st.metric("DCFC Stations", f"{dcfc_count:,}")
    with col3:
        l2_count = (df_filtered["charger_type"] == "Level 2").sum()
        st.metric("Level 2 Stations", f"{l2_count:,}")
    with col4:
        total_ports = df_filtered["total_ports"].sum()
        st.metric("Total Ports", f"{int(total_ports):,}")
    with col5:
        states_covered = df_filtered["state"].nunique()
        st.metric("States", f"{states_covered}")
    
    # Color map for charger types (vibrant colors)
    color_map = {
        "DCFC": "#ff6b6b",      # Coral red
        "Level 2": "#4ecdc4",    # Teal
        "Level 1": "#ffe66d",    # Yellow
        "Unknown": "#95a5a6"     # Gray
    }
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺️ Map", "📈 Charts", "📋 State Comparison", "🔢 Raw Data"
    ])
    
    # TAB 1: Map
    with tab1:
        st.subheader("🗺️ Station Locations")
        
        # Map controls
        map_col1, map_col2, map_col3 = st.columns([2, 2, 1])
        with map_col1:
            map_style = st.selectbox(
                "Map Style",
                ["Dark", "Streets", "Satellite", "Light"],
                index=0,
                key="map_style"
            )
        with map_col2:
            size_by = st.selectbox(
                "Size markers by",
                ["Uniform", "Number of Ports"],
                index=0,
                key="size_by"
            )
        
        # Map style mapping
        style_map = {
            "Dark": "carto-darkmatter",
            "Streets": "open-street-map", 
            "Satellite": "carto-positron",
            "Light": "carto-positron"
        }
        
        # Sample for performance if too many points
        df_map = df_filtered.copy()
        if len(df_map) > 8000:
            st.caption(f"📍 Showing sample of 8,000 stations from {len(df_map):,} total for performance.")
            df_map = df_map.sample(n=8000, random_state=42)
        else:
            st.caption(f"📍 Showing {len(df_map):,} stations")
        
        # Better color scheme
        color_map_enhanced = {
            "DCFC": "#ff6b6b",      # Coral red for DC Fast
            "Level 2": "#4ecdc4",    # Teal for Level 2
            "Level 1": "#ffe66d",    # Yellow for Level 1
            "Unknown": "#95a5a6"     # Gray for unknown
        }
        
        # Calculate marker size
        if size_by == "Number of Ports":
            df_map["marker_size"] = df_map["total_ports"].clip(1, 20) * 2
        else:
            df_map["marker_size"] = 8
        
        fig_map = px.scatter_map(
            df_map,
            lat="latitude",
            lon="longitude",
            color="charger_type",
            color_discrete_map=color_map_enhanced,
            size="marker_size",
            hover_name="station_name",
            hover_data={
                "city": True,
                "state": True, 
                "ev_network": True,
                "total_ports": True,
                "status": True,
                "marker_size": False,
                "latitude": False,
                "longitude": False,
            },
            zoom=3.5,
            center={"lat": 39.8283, "lon": -98.5795},
            height=650,
            opacity=0.8,
        )
        
        fig_map.update_layout(
            map_style=style_map[map_style],
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(0,0,0,0.7)",
                font=dict(color="white", size=12),
                title=dict(text="Charger Type", font=dict(color="white", size=14)),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        
        fig_map.update_traces(
            marker=dict(
                sizemin=4,
            ),
            hovertemplate="<b>%{hovertext}</b><br>" +
                          "City: %{customdata[0]}<br>" +
                          "State: %{customdata[1]}<br>" +
                          "Network: %{customdata[2]}<br>" +
                          "Ports: %{customdata[3]}<br>" +
                          "Status: %{customdata[4]}<extra></extra>"
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
    
    # TAB 2: Charts
    with tab2:
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("Stations by State")
            state_counts = df_filtered.groupby("state").size().reset_index(name="count")
            state_counts = state_counts.sort_values("count", ascending=True).tail(20)
            
            fig_states = px.bar(
                state_counts,
                x="count",
                y="state",
                orientation="h",
                color="count",
                color_continuous_scale="Blues",
            )
            fig_states.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig_states, use_container_width=True)
        
        with chart_col2:
            st.subheader("Stations by Charger Type")
            type_counts = df_filtered["charger_type"].value_counts().reset_index()
            type_counts.columns = ["charger_type", "count"]
            
            fig_types = px.pie(
                type_counts,
                values="count",
                names="charger_type",
                color="charger_type",
                color_discrete_map=color_map,
                hole=0.4,
            )
            fig_types.update_layout(height=400)
            st.plotly_chart(fig_types, use_container_width=True)
        
        # Deployment timeline
        st.subheader("Deployment Over Time")
        timeline = compute_deployment_timeline(df_filtered)
        if not timeline.empty:
            fig_timeline = px.area(
                timeline,
                x="open_year",
                y="stations_opened",
                color="charger_type",
                color_discrete_map=color_map,
            )
            fig_timeline.update_layout(
                xaxis_title="Year",
                yaxis_title="Stations Opened",
                height=400,
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("No timeline data available for selected filters.")
        
        # Network breakdown
        st.subheader("Top Charging Networks")
        network_data = compute_network_breakdown(df_filtered).head(15)
        if not network_data.empty:
            fig_network = px.bar(
                network_data,
                x="stations",
                y="ev_network",
                orientation="h",
                color="dcfc_ports",
                color_continuous_scale="Reds",
            )
            fig_network.update_layout(height=450, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_network, use_container_width=True)
    
    # TAB 3: State Comparison
    with tab3:
        st.subheader("State-Level Comparison")
        
        summary = compute_state_summary(df_filtered)
        summary = enrich_with_metadata(summary)
        
        # Metric selector
        metric_options = {
            "Total Stations": "total_stations",
            "DCFC Stations": "dcfc_stations",
            "Stations per 100k Population": "stations_per_100k",
            "DCFC per 100k Population": "dcfc_per_100k",
            "Stations per 1,000 sq mi": "stations_per_1000_sqmi",
            "% DCFC": "pct_dcfc",
            "% Available": "pct_available",
        }
        
        selected_metric = st.selectbox("Select Metric", options=list(metric_options.keys()))
        metric_col = metric_options[selected_metric]
        
        # Choropleth map
        fig_choropleth = px.choropleth(
            summary,
            locations="state",
            locationmode="USA-states",
            color=metric_col,
            scope="usa",
            color_continuous_scale="Viridis",
            hover_name="state_name",
            hover_data=["total_stations", "dcfc_stations", "stations_per_100k"],
        )
        fig_choropleth.update_layout(
            title=f"{selected_metric} by State",
            height=500,
        )
        st.plotly_chart(fig_choropleth, use_container_width=True)
        
        # Data table
        st.subheader("State Summary Table")
        display_cols = [
            "state_name", "total_stations", "dcfc_stations", "level2_stations",
            "total_ports", "stations_per_100k", "dcfc_per_100k", "pct_dcfc", "pct_available"
        ]
        display_cols = [c for c in display_cols if c in summary.columns]
        st.dataframe(
            summary[display_cols].sort_values("total_stations", ascending=False),
            use_container_width=True,
            height=400,
        )
    
    # TAB 4: Raw Data
    with tab4:
        st.subheader("Filtered Station Data")
        st.write(f"Showing {len(df_filtered):,} stations")
        
        # Column selector
        all_cols = df_filtered.columns.tolist()
        default_cols = ["station_name", "city", "state", "charger_type", "total_ports", "ev_network", "status", "open_date"]
        default_cols = [c for c in default_cols if c in all_cols]
        
        selected_cols = st.multiselect(
            "Select columns to display",
            options=all_cols,
            default=default_cols,
        )
        
        if selected_cols:
            st.dataframe(df_filtered[selected_cols], use_container_width=True, height=500)
        
        # Download button
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name="ev_stations_filtered.csv",
            mime="text/csv",
        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 24px 0; color: #94a3b8; font-size: 13px; line-height: 1.8;">
            <div style="font-size: 15px; color: #cbd5e1; margin-bottom: 6px;">
                <strong>NEVI, Utilities, and Installers:</strong> Bottlenecks in U.S. EV Charging Deployment
            </div>
            <div>
                Built by <strong style="color: #a5b4fc;">Sotaire Kwizera</strong> &middot;
                Data Analyst &middot; UC Berkeley &middot; DEVP 226 Final Project
            </div>
            <div style="margin-top: 10px;">
                Data: <a href="https://afdc.energy.gov/" target="_blank" style="color: #a5b4fc; text-decoration: none;">AFDC / NREL</a>
                &nbsp;·&nbsp; AI: <a href="https://ai.google.dev/" target="_blank" style="color: #a5b4fc; text-decoration: none;">Google Gemini</a>
                &nbsp;·&nbsp; <a href="https://github.com/kwizeras/nevi-ev-charging" target="_blank" style="color: #a5b4fc; text-decoration: none;">View Source</a>
                &nbsp;·&nbsp; <a href="https://kwizeras.github.io/nevi-ev-charging/" target="_blank" style="color: #a5b4fc; text-decoration: none;">Project Site</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
