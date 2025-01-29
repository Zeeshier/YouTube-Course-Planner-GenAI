import os
import json
import isodate
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema import AIMessage

# Load environment variables
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def fetch_playlist_videos(playlist_url):
    """Fetch video details from a YouTube playlist."""
    try:
        playlist_id = playlist_url.split("list=")[-1]
        api_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=50&key={YOUTUBE_API_KEY}"
        response = requests.get(api_url)
        response.raise_for_status()

        playlist_data = response.json()
        video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_data['items']]

        # Handle pagination
        while 'nextPageToken' in playlist_data:
            next_page_token = playlist_data['nextPageToken']
            api_url = f"{api_url}&pageToken={next_page_token}"
            response = requests.get(api_url)
            response.raise_for_status()
            playlist_data = response.json()
            video_ids.extend([item['snippet']['resourceId']['videoId'] for item in playlist_data['items']])

        videos = []
        for video_id in video_ids:
            video_details = fetch_video_details(video_id)
            if video_details:
                videos.append(video_details)

        return videos

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch playlist data: {str(e)}")

def fetch_video_details(video_id):
    """Fetch video title and duration from YouTube API."""
    try:
        api_url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails,snippet&id={video_id}&key={YOUTUBE_API_KEY}"
        response = requests.get(api_url)
        response.raise_for_status()

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

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch video details: {str(e)}")

def convert_duration_to_seconds(duration):
    """Convert ISO 8601 duration to seconds."""
    parsed_duration = isodate.parse_duration(duration)
    return int(parsed_duration.total_seconds())

def clean_json_response(text):
    """Extract JSON from LLM response with multiple cleanup strategies."""
    # Remove all markdown code blocks
    text = text.replace("```json", "").replace("```", "")
    
    # Find first [ and last ] to capture the JSON array
    start_idx = text.find('[')
    end_idx = text.rfind(']') + 1
    
    if start_idx != -1 and end_idx != -1:
        return text[start_idx:end_idx].strip()
    return text.strip()

def generate_study_plan(videos, total_days):
    """Use LLM to intelligently distribute videos across the given days."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ API key is missing. Add it to the .env file.")

    llm = ChatGroq(model="llama3-8b-8192", temperature=0, groq_api_key=GROQ_API_KEY)

    video_data = json.dumps(videos, indent=2)

    prompt = ChatPromptTemplate.from_template("""
    You are an educational AI. Organize these YouTube videos into a {total_days}-day study plan:
    - Group related topics
    - Balance daily workload
    - Maintain logical flow

    Videos:
    {video_data}

    Return ONLY valid JSON in this format:
    [
        {{"day": 1, "videos": ["Video 1", "Video 2"]}},
        {{"day": 2, "videos": ["Video 3"]}},
        ...
    ]
    """)

    response = llm.invoke(prompt.format(total_days=total_days, video_data=video_data))
    response_text = response.content.strip() if isinstance(response, AIMessage) else str(response).strip()

    try:
        cleaned_response = clean_json_response(response_text)
        return json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response: {str(e)}\nRaw response: {response_text}")