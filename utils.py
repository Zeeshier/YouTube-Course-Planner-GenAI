import isodate
import requests
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()
import os

# Set your OpenAI API key in the .env file
groq_api_key = os.getenv("GROQ_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def fetch_playlist_videos(playlist_url):
    """
    Fetch video details from a YouTube playlist using the YouTube Data API.
    Returns a list of videos with their title and duration.
    """
    playlist_id = playlist_url.split("list=")[-1]
    api_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=50&key={YOUTUBE_API_KEY}"

    response = requests.get(api_url)
    if response.status_code != 200:
        raise ValueError("Failed to fetch playlist data. Check the playlist URL or API key.")

    playlist_data = response.json()
    video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_data['items']]

    # Fetch video durations
    videos = []
    for video_id in video_ids:
        video_details = fetch_video_details(video_id)
        if video_details:
            videos.append(video_details)

    return videos


def fetch_video_details(video_id):
    """
    Fetch the title and duration of a YouTube video using the YouTube Data API.
    """
    api_url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails,snippet&id={video_id}&key={YOUTUBE_API_KEY}"
    response = requests.get(api_url)
    if response.status_code != 200:
        return None

    video_data = response.json()
    if not video_data['items']:
        return None

    item = video_data['items'][0]
    duration = item['contentDetails']['duration']
    title = item['snippet']['title']
    return {
        'title': title,
        'duration': convert_duration_to_seconds(duration)
    }


def convert_duration_to_seconds(duration):
    """
    Convert ISO 8601 duration to seconds.
    """
    parsed_duration = isodate.parse_duration(duration)
    return int(parsed_duration.total_seconds())


def group_videos_by_topics(videos):
    """
    Use LLM to group videos into topics based on their titles.

    Parameters:
    - videos (list): List of dictionaries containing 'title' and 'duration'.

    Returns:
    - dict: Grouped videos by topic.
    """

    if not groq_api_key:
        raise ValueError("Groq API key not provided. Add it to the .env file.")

    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, groq_api_key=groq_api_key)
    
    video_titles = [video['title'] for video in videos]
    titles_text = "\n".join([f"- {title}" for title in video_titles])

    prompt = ChatPromptTemplate.from_template("""
You are an educational assistant. Categorize the following YouTube video titles into meaningful topics.
Return the results in JSON format: {{"Topic Name": ["Video 1", "Video 2", ...]}}

Video Titles:
{titles_text}
    """)

    response = llm.predict(prompt.format_messages(titles_text=titles_text))

    try:
        grouped_videos = eval(response.strip())  # Convert LLM output to dictionary
    except:
        raise ValueError("LLM response format is incorrect. Try again.")

    # Convert video titles to full video dictionaries
    final_grouped_videos = {}
    for topic, video_titles in grouped_videos.items():
        final_grouped_videos[topic] = [video for video in videos if video['title'] in video_titles]

    return final_grouped_videos


import random

def generate_study_plan(videos, total_days, videos_per_day):
    """
    Generate a study plan where videos are categorized by topic using LLM.

    Parameters:
    - videos (list): List of video dictionaries.
    - total_days (int): Number of days to complete the course.
    - videos_per_day (int): Number of videos per day.

    Returns:
    - list: Study plan with topic-based distribution.
    """

    grouped_videos = group_videos_by_topics(videos)
    topics = list(grouped_videos.keys())
    study_plan = []

    video_pool = []
    for topic in topics:
        video_pool.extend(grouped_videos[topic])

    random.shuffle(video_pool)  # Shuffle for variety

    index = 0
    for day in range(1, total_days + 1):
        day_videos = video_pool[index:index + videos_per_day]
        index += videos_per_day

        # Find the dominant topic of the selected videos
        dominant_topic = max(grouped_videos.keys(), key=lambda t: sum(1 for v in day_videos if v in grouped_videos[t]))

        study_plan.append({'day': day, 'topic': dominant_topic, 'videos': day_videos})

    return study_plan



def format_duration(seconds):
    """
    Format seconds into HH:MM:SS format.
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"
