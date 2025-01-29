import streamlit as st
from utils import (
    fetch_playlist_videos,
    generate_study_plan,
    format_duration,
    group_videos_by_topics
)

st.title("YouTube Course Study Plan Generator")
st.write("Provide a YouTube playlist URL and customize your study preferences!")

# Input fields
playlist_url = st.text_input("Enter YouTube Playlist URL:")
total_days = st.number_input("Enter total days to complete the course:", min_value=1, step=1)
max_videos_per_day = st.number_input("Maximum videos per day:", min_value=1, step=1)

if st.button("Generate Study Plan"):
    if not playlist_url:
        st.error("Please enter a valid YouTube playlist URL.")
    else:
        with st.spinner("Fetching playlist details..."):
            try:
                videos = fetch_playlist_videos(playlist_url)

                if not videos:
                    st.warning("No videos found in the playlist!")
                else:
                    group_topics = st.checkbox("Group videos by topics using LLM")

                    if group_topics:
                        with st.spinner("Grouping videos by topics..."):
                            grouped_videos = group_videos_by_topics(videos)
                            st.success("Videos grouped by topics!")
                            for category, titles in grouped_videos.items():
                                st.subheader(category)
                                for title in titles:
                                    st.write(f"- {title}")

                    with st.spinner("Generating study plan..."):
                        study_plan = generate_study_plan(videos, total_days, max_videos_per_day)
                        st.success("Your study plan is ready!")
                        for day_plan in study_plan:
                            st.subheader(f"Day {day_plan['day']}")
                            for video in day_plan["videos"]:
                                st.write(f"- {video['title']} ({format_duration(video['duration'])})")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
