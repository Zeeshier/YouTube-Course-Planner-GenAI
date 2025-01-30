import json
import streamlit as st
from utils import fetch_playlist_videos, generate_study_plan
from fpdf import FPDF
import os

# Correct page configuration
st.set_page_config(
    page_title="🎥YouTube Study Planner 📚",
    page_icon="📚",
    layout="wide"
)

st.title("🎥 AI-Powered YouTube Study Planner 📚")

def create_pdf(study_plan, course_name, filename="study_plan.pdf"):
    """Generate a PDF file from the study plan."""
    pdf = FPDF()
    pdf.add_page()
    
    # Add course name with larger font
    pdf.set_font("Arial", 'B', size=24)
    pdf.cell(200, 20, txt=course_name, ln=True, align="C")
    pdf.ln(10)
    
    # Add "Study Plan" subtitle
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="Study Plan", ln=True, align="C")
    pdf.ln(10)
    
    # Add each day's plan
    for day in study_plan:
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Day {day['day']} - {len(day['videos'])} videos", ln=True)
        pdf.set_font("Arial", size=10)
        
        for video in day["videos"]:
            # Clean the video title of any problematic characters
            clean_title = ''.join(char for char in video if ord(char) < 128)
            pdf.cell(200, 10, txt=f"- {clean_title}", ln=True)
        pdf.ln(5)
    
    # Save the PDF
    pdf.output(filename, 'F')
    return filename

def display_study_plan(study_plan, course_name):
    """Render study plan in beautiful card layout"""
    # Display course name prominently
    st.markdown(f"""
        <h1 style="
            text-align: center;
            color: #1f1f1f;
            margin-bottom: 30px;
            font-size: 2.5em;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 10px;">
            {course_name}
        </h1>
    """, unsafe_allow_html=True)
    
    cols = st.columns(3)
    col_idx = 0
    
    for day in study_plan:
        with cols[col_idx]:
            st.markdown(f"""
                <div style="
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 10px 0;
                    background-color: white;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1)">
                    <h3 style="color: #1f1f1f;">Day {day['day']}</h3>
                    <p style="color: #666;">{len(day['videos'])} videos</p>
                    <div style="margin-top: 10px;">
                """, 
                unsafe_allow_html=True
            )
            
            for idx, video in enumerate(day["videos"], 1):
                st.markdown(f"""
                    <div style="
                        padding: 8px;
                        margin: 5px 0;
                        background-color: #f8f9fa;
                        border-radius: 5px;
                        font-size: 14px;">
                        {idx}. {video}
                    </div>
                """, 
                unsafe_allow_html=True
            )
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        col_idx = (col_idx + 1) % 3

# Input Section
with st.sidebar:
    st.header("Settings")
    course_name = st.text_input(
        "Course Name:",
        placeholder="Enter course name...",
        help="Enter the name of your course or study topic"
    )
    playlist_url = st.text_input(
        "YouTube Playlist URL:", 
        placeholder="Paste playlist link here..."
    )
    total_days = st.number_input(
        "Number of Days:", 
        min_value=1, 
        value=7
    )
    st.markdown("---")
    st.info("Tip: Use a well-organized playlist for best results!")

# Main Processing
if st.button("Generate Study Plan", use_container_width=True):
    if not playlist_url:
        st.error("Please enter a YouTube playlist URL")
    elif not course_name:
        st.error("Please enter a course name")
    else:
        with st.spinner("🔍 Fetching playlist data from YouTube..."):
            try:
                videos = fetch_playlist_videos(playlist_url)
                if not videos:
                    st.error("No videos found in the playlist")
                    st.stop()

                with st.spinner("🤖 AI is generating your study plan..."):
                    study_plan = generate_study_plan(videos, total_days)
                
                st.success("Study Plan Generated Successfully!")
                st.balloons()
                display_study_plan(study_plan, course_name)

                try:
                    # Generate and download PDF
                    pdf_filename = create_pdf(study_plan, course_name)
                    with open(pdf_filename, "rb") as pdf_file:
                        st.download_button(
                            label="Download Study Plan (PDF)",
                            data=pdf_file,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
                    # Clean up the PDF file
                    if os.path.exists(pdf_filename):
                        os.remove(pdf_filename)
                except Exception as pdf_error:
                    st.warning("Could not generate PDF. Study plan is still available on screen.")
                    st.error(f"PDF Error: {str(pdf_error)}")

            except Exception as e:
                st.error("Error generating study plan")
                st.error(str(e))