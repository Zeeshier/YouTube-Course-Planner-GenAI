import json
import streamlit as st
from utils import fetch_playlist_videos, generate_study_plan

st.set_page_config(page_title="YouTube Study Planner", page_icon="📚", layout="wide")
st.title("🎥 AI-Powered YouTube Study Planner")

# Custom CSS for better styling
st.markdown("""
<style>
    .day-card {
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background: white;
    }
    .video-item {
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        border-left: 3px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

def display_study_plan(study_plan):
    """Render study plan in beautiful card layout"""
    cols = st.columns(3)
    col_idx = 0
    
    for day in study_plan:
        with cols[col_idx]:
            with st.container():
                st.markdown(f"""
                <div class="day-card">
                    <h3>📅 Day {day['day']}</h3>
                    <p>{len(day['videos'])} videos</p>
                    <div class="video-list">
                """, unsafe_allow_html=True)
                
                for idx, video in enumerate(day["videos"], 1):
                    st.markdown(f"""
                    <div class="video-item">
                        #{idx} {video}
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div></div>", unsafe_allow_html=True)
        
        col_idx = (col_idx + 1) % 3

# Input Section
with st.sidebar:
    st.header("⚙️ Settings")
    playlist_url = st.text_input("YouTube Playlist URL:", placeholder="Paste playlist link here...")
    total_days = st.number_input("Number of Days:", min_value=1, value=7)
    st.markdown("---")
    st.info("💡 Tip: Use a well-organized playlist for best results!")

# Main Processing
if st.button("🚀 Generate Study Plan", use_container_width=True):
    if not playlist_url:
        st.error("Please enter a YouTube playlist URL")
    else:
        with st.spinner("🔍 Analyzing playlist content..."):
            try:
                videos = fetch_playlist_videos(playlist_url)
                if not videos:
                    st.error("No videos found in the playlist")
                    st.stop()

                with st.spinner("🧠 AI is crafting your perfect study plan..."):
                    study_plan = generate_study_plan(videos, total_days)
                
                st.success("✅ Study Plan Generated Successfully!")
                st.balloons()
                display_study_plan(study_plan)

            except Exception as e:
                st.error("⚠️ Error generating study plan")
                st.error(str(e))