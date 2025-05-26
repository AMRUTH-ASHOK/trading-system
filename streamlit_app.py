"""Run with: streamlit run streamlit_app.py"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from pathlib import Path
import yaml
from trading.utils.pipeline_tracker import PipelineTracker

# Add this at the top of the file, right after the imports
CONFIG_DIR = Path(__file__).parent / "config"

# Load settings
with open(CONFIG_DIR / "settings.yaml", "r") as f:
    settings = yaml.safe_load(f)
ui_settings = settings.get("ui", {})

# Set page config and base styling
st.set_page_config(
    page_title="Trading System Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced styling with focus on sidebar visibility
st.markdown(f"""
    <style>
        /* Sidebar specific styling */
        section[data-testid="stSidebar"] {{
            background-color: {ui_settings['colors']['background']};
            border-right: 3px solid {ui_settings['colors']['primary']};
        }}
        
        section[data-testid="stSidebar"] > div {{
            padding: {ui_settings['layout']['container_padding']};
        }}
        
        section[data-testid="stSidebar"] label {{
            color: {ui_settings['colors']['text']} !important;
            font-size: {ui_settings['fonts']['size']['medium']}rem !important;
            font-weight: {ui_settings['fonts']['weights']['semibold']} !important;
            letter-spacing: 0.2px;
        }}
        
        section[data-testid="stSidebar"] .stMarkdown {{
            color: {ui_settings['colors']['text']} !important;
            font-size: {ui_settings['fonts']['size']['medium']}rem !important;
            font-weight: {ui_settings['fonts']['weights']['normal']} !important;
        }}
        
        /* Sidebar headers */
        .sidebar-header h1 {{
            color: {ui_settings['colors']['primary']};
            font-size: {ui_settings['fonts']['size']['xxlarge']}rem;
            font-weight: {ui_settings['fonts']['weights']['extrabold']};
            margin-bottom: 2rem;
            padding-bottom: 0.75rem;
            border-bottom: 3px solid {ui_settings['colors']['primary']};
            text-shadow: 1px 1px 1px rgba(0,0,0,0.1);
        }}
        
        .filter-header h2 {{
            color: {ui_settings['colors']['primary']};
            font-size: {ui_settings['fonts']['size']['xlarge']}rem;
            font-weight: {ui_settings['fonts']['weights']['bold']};
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid {ui_settings['colors']['primary']};
            text-shadow: 1px 1px 1px rgba(0,0,0,0.1);
        }}
        
        /* Pipeline selection styling */
        .pipeline-select {{
            background-color: #FFFFFF;
            padding: 1.5rem;
            border-radius: 8px;
            border: 2px solid #1976D2;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .pipeline-select label {{
            color: #1976D2 !important;
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            margin-bottom: 0.75rem !important;
            text-shadow: 1px 1px 1px rgba(0,0,0,0.1);
        }}
        
        /* Sidebar selectbox enhancement */
        section[data-testid="stSidebar"] .stSelectbox > div > div {{
            background-color: #FFFFFF;
            border: 2px solid #1976D2 !important;
            border-radius: 6px;
            padding: 0.75rem;
            font-size: 1.1rem !important;
            font-weight: 500 !important;
            color: #000000 !important;
        }}
        
        /* Checkbox styling in sidebar */
        section[data-testid="stSidebar"] .stCheckbox {{
            background-color: #FFFFFF;
            padding: 1rem;
            border-radius: 6px;
            margin: 0.75rem 0;
            border: 2px solid #1976D2;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        section[data-testid="stSidebar"] .stCheckbox label {{
            color: #000000 !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
        }}
        
        /* Date input in sidebar */
        section[data-testid="stSidebar"] .stDateInput > div {{
            background-color: #FFFFFF;
            border: 2px solid #1976D2;
            border-radius: 6px;
            padding: 0.75rem;
        }}
        
        section[data-testid="stSidebar"] .stDateInput label {{
            color: #000000 !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            margin-bottom: 0.5rem !important;
        }}
        
        /* Expander in sidebar */
        section[data-testid="stSidebar"] .streamlit-expanderHeader {{
            background-color: #F8F9FA !important;
            border: 2px solid #1976D2 !important;
            border-radius: 6px !important;
            padding: 1rem !important;
            font-weight: 700 !important;
            color: #1976D2 !important;
            font-size: 1.2rem !important;
            text-shadow: 1px 1px 1px rgba(0,0,0,0.1);
        }}
        
        /* Active filters in sidebar */
        section[data-testid="stSidebar"] .stMarkdown strong {{
            color: #1976D2 !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
        }}
        
        section[data-testid="stSidebar"] .stMarkdown p {{
            color: #000000 !important;
            font-weight: 500 !important;
            font-size: 1.1rem !important;
            margin: 0.5rem 0;
        }}

        /* Filter container in sidebar */
        section[data-testid="stSidebar"] .filter-container {{
            background-color: #FFFFFF;
            padding: 1.5rem;
            border-radius: 8px;
            border: 2px solid #1976D2;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        /* Warning/Info messages in sidebar */
        section[data-testid="stSidebar"] .stAlert {{
            background-color: #FFFFFF !important;
            border: 2px solid #1976D2 !important;
            color: #000000 !important;
            font-size: 1.1rem !important;
            font-weight: 500 !important;
            padding: 1rem !important;
            border-radius: 6px !important;
            margin: 1rem 0 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}

        /* Global text styling */
        .stApp, .stApp label, .stApp p {{
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            color: #000000;
        }}
        
        /* Main app styling */
        .stApp {{
            background-color: #FFFFFF;
        }}
        
        /* Filter container styling */
        .filter-container {{
            background-color: #F8F9FA;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #1976D2;
            margin: 1rem 0;
        }}
        
        /* Selectbox styling */
        .stSelectbox > div {{
            border: 1px solid #1976D2 !important;
        }}
        
        .stSelectbox label {{
            color: #000000 !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            margin-bottom: 0.5rem !important;
        }}
        
        /* Expander styling */
        .streamlit-expanderHeader {{
            background-color: #F8F9FA !important;
            border: 1px solid #1976D2 !important;
            border-radius: 6px !important;
            padding: 1rem !important;
            font-weight: 600 !important;
            color: #000000 !important;
            font-size: 1.1rem !important;
        }}
        
        /* Active filters styling */
        .stMarkdown {{
            background-color: #FFFFFF;
            padding: 0.75rem;
            border-radius: 6px;
            margin-top: 1rem;
        }}
        
        .stMarkdown p {{
            margin: 0;
            padding: 0.25rem 0;
            color: #000000;
            font-weight: 500;
            font-size: 1rem;
        }}
        
        /* Metric styling */
        div[data-testid="stMetricValue"] {{
            color: #000000 !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
            background-color: #FFFFFF;
            padding: 1.5rem !important;
            border-radius: 8px;
            border: 2px solid #1976D2;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }}
        
        div[data-testid="stMetricLabel"] {{
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            color: #000000 !important;
        }}
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 2px;
            background-color: #F8F9FA;
            padding: 1rem 0.5rem 0 0.5rem;
            border-radius: 8px 8px 0 0;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            padding: 0 20px;
            color: #000000;
            font-weight: 600;
            font-size: 1rem;
            background-color: #FFFFFF;
            border: 1px solid #1976D2;
            border-radius: 8px 8px 0 0;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: #1976D2 !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }}
        
        /* Headers */
        h1, h2, h3 {{
            color: #000000 !important;
            font-weight: 700 !important;
        }}
        
        /* Main content headers */
        .main-header {{
            color: #000000;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 2rem;
            padding-bottom: 0.75rem;
            border-bottom: 3px solid #1976D2;
        }}
        
        /* Chart title and labels */
        .js-plotly-plot .plotly .gtitle {{
            font-size: 1.2rem !important;
            font-weight: 600 !important;
            color: #000000 !important;
        }}
        
        .js-plotly-plot .plotly .xtitle,
        .js-plotly-plot .plotly .ytitle {{
            font-size: 1rem !important;
            font-weight: 500 !important;
            color: #000000 !important;
        }}
    </style>
""", unsafe_allow_html=True)

FEATURE_DIR = Path(__file__).parent / "data" / "features"

def plot_candlestick(df, symbol, title):
    """Create a candlestick chart with volume"""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                       vertical_spacing=0.03, subplot_titles=(title, 'Volume'),
                       row_heights=[0.7, 0.3])
    
    fig.add_trace(go.Candlestick(x=df.index.get_level_values('timestamp'),
                                open=df['open'],
                                high=df['high'],
                                low=df['low'],
                                close=df['close'],
                                increasing_line_color=ui_settings['candlestick_colors']['increasing'],
                                decreasing_line_color=ui_settings['candlestick_colors']['decreasing'],
                                name='OHLC'),
                  row=1, col=1)
    
    colors = [ui_settings['candlestick_colors']['increasing'] if row['close'] >= row['open'] 
             else ui_settings['candlestick_colors']['decreasing'] 
             for _, row in df.iterrows()]
    
    fig.add_trace(go.Bar(x=df.index.get_level_values('timestamp'),
                        y=df['volume'],
                        marker_color=colors,
                        name='Volume'),
                  row=2, col=1)
    
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=ui_settings['chart_height'],
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color=ui_settings['colors']['text'],
        title_font_color=ui_settings['colors']['text'],
        margin=dict(l=50, r=50, t=50, b=50),
        showlegend=False
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=ui_settings['colors']['muted'])
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=ui_settings['colors']['muted'])
    
    return fig

def plot_features(df, symbol):
    """Plot technical indicators"""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                       vertical_spacing=0.03,
                       subplot_titles=('Price & Moving Averages', 'RSI'),
                       row_heights=[0.7, 0.3])
    
    # Price and MAs
    df_sym = df[df['symbol'] == symbol]
    fig.add_trace(go.Scatter(x=df_sym['timestamp'],
                            y=df_sym['close'],
                            name='Close',
                            line=dict(color='#111111', width=1)),
                 row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df_sym['timestamp'],
                            y=df_sym['sma_fast'],
                            name='Fast MA',
                            line=dict(color='#1976D2', width=1.5)),  # Blue
                 row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df_sym['timestamp'],
                            y=df_sym['sma_slow'],
                            name='Slow MA',
                            line=dict(color='#E64A19', width=1.5)),  # Orange
                 row=1, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=df_sym['timestamp'],
                            y=df_sym['rsi'],
                            name='RSI',
                            line=dict(color='#7B1FA2', width=1.5)),  # Purple
                 row=2, col=1)
    
    # Add RSI levels
    fig.add_hline(y=70, line_dash="dash", line_color="#EF5350", row=2, col=1)  # Red
    fig.add_hline(y=30, line_dash="dash", line_color="#26A69A", row=2, col=1)  # Green
    
    fig.update_layout(
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#111111',
        title_font_color='#111111'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5')
    
    return fig

def format_pipeline_id(pipeline_id: str, timestamp: str) -> str:
    """Format pipeline ID for display in a more readable way"""
    dt = datetime.fromisoformat(timestamp)
    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
    # Extract configurable number of characters from the hash
    short_hash = pipeline_id.split('_')[-1][:ui_settings['pipeline_id_hash_length']]
    return f"Pipeline {formatted_time} ({short_hash})"

def main():
    st.markdown('<h1 class="main-header">Trading System Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar - Pipeline Selection and Filtering
    with st.sidebar:
        st.markdown("""
            <div class="sidebar-header">
                <h1>Pipeline Selection</h1>
            </div>
        """, unsafe_allow_html=True)
        
        pipelines = PipelineTracker.list_pipelines()
        if not pipelines:
            st.warning("No pipeline runs found. Please run the trading system first.")
            return
        
        pipeline_df = pd.DataFrame(pipelines)
        pipeline_df['datetime'] = pd.to_datetime(pipeline_df['timestamp'])
        pipeline_df['date'] = pipeline_df['datetime'].dt.date
        pipeline_df['hour'] = pipeline_df['datetime'].dt.hour
        pipeline_df['minute'] = pipeline_df['datetime'].dt.minute
        
        # Pipeline selection with better formatting
        filtered_df = pipeline_df.copy()
        
        # Create pipeline selection options
        pipeline_options = {
            format_pipeline_id(row['pipeline_id'], row['timestamp']): row['pipeline_id']
            for _, row in filtered_df.iterrows()
        }
        
        # Sort pipeline options by timestamp (most recent first)
        sorted_options = sorted(
            pipeline_options.keys(),
            key=lambda x: datetime.strptime(x.split('(')[0].strip(), 'Pipeline %Y-%m-%d %H:%M:%S'),
            reverse=True
        )
        
        st.markdown('<div class="pipeline-select">', unsafe_allow_html=True)
        selected_pipeline_display = st.selectbox(
            "📊 Select Pipeline Run",
            options=sorted_options
        )
        selected_pipeline_id = pipeline_options[selected_pipeline_display]
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Optional Filters Section
        st.markdown("""
            <div class="filter-header">
                <h2>Filter Pipelines (Optional)</h2>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("🔍 Show Filters"):
            st.markdown('<div class="filter-container">', unsafe_allow_html=True)
            
            # Date Filter
            if st.checkbox("📅 Filter by Date", value=False, key="date_filter"):
                min_date = pipeline_df['date'].min()
                max_date = pipeline_df['date'].max()
                selected_date = st.date_input(
                    "Select Date",
                    value=None,
                    min_value=min_date,
                    max_value=max_date
                )
                if selected_date:
                    filtered_df = filtered_df[filtered_df['date'] == selected_date]
            
            # Hour Filter
            if st.checkbox("🕐 Filter by Hour", value=False, key="hour_filter"):
                hours = sorted(filtered_df['hour'].unique())
                hour_options = {f"{h:02d}:00": h for h in hours}
                selected_hour = st.selectbox(
                    "Select Hour",
                    options=list(hour_options.keys()),
                )
                if selected_hour:
                    filtered_df = filtered_df[filtered_df['hour'] == hour_options[selected_hour]]
            
            # Minute Filter
            if st.checkbox("🕒 Filter by Minute", value=False, key="minute_filter"):
                minutes = sorted(filtered_df['minute'].unique())
                minute_options = {f"{m:02d}": m for m in minutes}
                selected_minute = st.selectbox(
                    "Select Minute",
                    options=list(minute_options.keys()),
                )
                if selected_minute:
                    filtered_df = filtered_df[filtered_df['minute'] == minute_options[selected_minute]]
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Show current filters
            active_filters = []
            if st.session_state.get("date_filter") and selected_date:
                active_filters.append(f"Date: {selected_date}")
            if st.session_state.get("hour_filter") and selected_hour:
                active_filters.append(f"Hour: {selected_hour}")
            if st.session_state.get("minute_filter") and selected_minute:
                active_filters.append(f"Minute: {selected_minute}")
            
            if active_filters:
                st.markdown("**Active Filters:**")
                for f in active_filters:
                    st.markdown(f"- {f}")

    # Load and display pipeline data
    pipeline_data = PipelineTracker.load_pipeline(selected_pipeline_id)
    metadata = pipeline_data["metadata"]
    raw_data = pipeline_data["raw_data"]
    features = pipeline_data["features"]
    
    # Pipeline Overview with improved styling
    st.header("Pipeline Overview")
    
    # Status with color coding
    status = metadata["status"].upper()
    status_color = {
        "COMPLETED": "🟢",
        "FAILED": "🔴",
        "RUNNING": "🟡"
    }.get(status, "⚪")
    
    cols = st.columns(4)
    with cols[0]:
        st.metric("Status", f"{status_color} {status}")
    with cols[1]:
        st.metric("Symbols", f"📊 {len(metadata['raw_data'].get('symbols', []))}")
    with cols[2]:
        st.metric("Signals", f"📈 {len(metadata['signals'])}")
    with cols[3]:
        duration = metadata.get("duration", "N/A")
        st.metric("Duration", f"⏱️ {duration}")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Market Data", "Technical Analysis", "Signals", "Trades"])
    
    with tab1:
        st.subheader("Raw Market Data")
        with st.container():
            st.markdown('<div class="symbol-select">', unsafe_allow_html=True)
            symbol = st.selectbox(
                "📈 Select Symbol",
                options=metadata["raw_data"].get("symbols", []),
                key="symbol_raw"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            if raw_data is not None and symbol:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                df_symbol = raw_data.loc[pd.IndexSlice[:, symbol], :]
                fig = plot_candlestick(df_symbol, symbol, f"{symbol} - Price & Volume")
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Technical Analysis")
        with st.container():
            st.markdown('<div class="symbol-select">', unsafe_allow_html=True)
            symbol = st.selectbox(
                "📊 Select Symbol",
                options=metadata["features"].get("symbols", []),
                key="symbol_tech"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            if features is not None and symbol:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                fig = plot_features(features, symbol)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.subheader("Trading Signals")
        if metadata["signals"]:
            st.markdown('<div class="filter-section">', unsafe_allow_html=True)
            signals_df = pd.DataFrame(metadata["signals"])
            signals_df["timestamp"] = pd.to_datetime(signals_df["timestamp"])
            signals_df = signals_df.sort_values("timestamp")
            
            # Add signal filtering
            st.markdown("### Signal Filters")
            col1, col2 = st.columns(2)
            with col1:
                signal_symbols = sorted(signals_df["symbol"].unique())
                selected_signal_symbol = st.multiselect(
                    "📈 Filter by Symbol",
                    options=signal_symbols,
                    default=signal_symbols
                )
            with col2:
                signal_types = sorted(signals_df["signal_type"].unique())
                selected_signal_types = st.multiselect(
                    "🔍 Filter by Signal Type",
                    options=signal_types,
                    default=signal_types
                )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Apply filters
            mask = (signals_df["symbol"].isin(selected_signal_symbol) & 
                   signals_df["signal_type"].isin(selected_signal_types))
            filtered_signals = signals_df[mask]
            
            if not filtered_signals.empty:
                st.markdown('<div class="data-container">', unsafe_allow_html=True)
                st.dataframe(filtered_signals, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No signals match the selected filters")
        else:
            st.info("No signals generated in this pipeline run")
    
    with tab4:
        st.subheader("Executed Trades")
        if metadata["trades"]:
            st.markdown('<div class="filter-section">', unsafe_allow_html=True)
            trades_df = pd.DataFrame(metadata["trades"])
            trades_df["timestamp"] = pd.to_datetime(trades_df["timestamp"])
            trades_df = trades_df.sort_values("timestamp")
            
            # Add trade filtering
            st.markdown("### Trade Filters")
            col1, col2 = st.columns(2)
            with col1:
                trade_symbols = sorted(trades_df["symbol"].unique())
                selected_trade_symbol = st.multiselect(
                    "📊 Filter by Symbol",
                    options=trade_symbols,
                    default=trade_symbols,
                    key="trade_symbols"
                )
            with col2:
                trade_types = sorted(trades_df["trade_type"].unique())
                selected_trade_types = st.multiselect(
                    "🔍 Filter by Trade Type",
                    options=trade_types,
                    default=trade_types,
                    key="trade_types"
                )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Apply filters
            mask = (trades_df["symbol"].isin(selected_trade_symbol) & 
                   trades_df["trade_type"].isin(selected_trade_types))
            filtered_trades = trades_df[mask]
            
            if not filtered_trades.empty:
                st.markdown('<div class="data-container">', unsafe_allow_html=True)
                st.dataframe(filtered_trades, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No trades match the selected filters")
        else:
            st.info("No trades executed in this pipeline run")
    
    # Error Display with improved styling
    if metadata.get("error"):
        st.error(f"Pipeline Error: {metadata['error']}")
    
    # Logs with improved styling
    with st.expander("Pipeline Logs"):
        log_file = f"logs/{selected_pipeline_id}.log"
        try:
            with open(log_file, "r") as f:
                logs = f.read()
            st.text_area("Logs", logs, height=ui_settings['log_display_height'])
        except FileNotFoundError:
            st.warning("Log file not found")

    # Add CSS for new containers
    st.markdown("""
        <style>
            /* Data container styling */
            .data-container {
                background-color: #FFFFFF;
                padding: 1rem;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
                margin: 1rem 0;
            }
            
            /* Symbol selector enhancements */
            .symbol-select {
                background-color: #FFFFFF;
                padding: 1.5rem;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
                margin-bottom: 1rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            
            .symbol-select label {
                color: #1976D2 !important;
                font-weight: 500 !important;
                font-size: 1rem !important;
            }
            
            /* Chart container enhancements */
            .chart-container {
                background-color: #FFFFFF;
                padding: 2rem;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
                margin: 1rem 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            
            /* Remove undefined text */
            .js-plotly-plot .plotly .modebar {
                display: none !important;
            }
            
            /* Better table styling */
            .stDataFrame {
                border: none !important;
            }
            
            .stDataFrame table {
                border-collapse: separate;
                border-spacing: 0;
                border-radius: 8px;
                overflow: hidden;
            }
            
            .stDataFrame th {
                background-color: #F8F9FA !important;
                color: #1976D2 !important;
                font-weight: 500 !important;
                padding: 0.75rem !important;
                border-top: 1px solid #E0E0E0;
                border-bottom: 2px solid #E0E0E0;
            }
            
            .stDataFrame td {
                padding: 0.75rem !important;
                border-bottom: 1px solid #E0E0E0;
                color: #424242 !important;
            }
        </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
