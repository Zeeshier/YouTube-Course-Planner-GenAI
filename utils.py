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
    """Use LLM to intelligently distribute videos equally across the given days."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ API key is missing. Add it to the .env file.")

    llm = ChatGroq(model="llama3-8b-8192", temperature=0, groq_api_key=GROQ_API_KEY)
    
    # Create a list of video titles
    video_titles = [video['title'] for video in videos]
    videos_per_day = len(video_titles) / total_days
    
    prompt = ChatPromptTemplate.from_template("""
    You are an educational AI. Organize these {total_videos} YouTube videos into a {total_days}-day study plan.
    Requirements:
    1. MUST distribute videos as equally as possible across days
    2. Each day should have approximately {videos_per_day} videos
    3. Maintain logical topic sequence
    4. Keep related topics together when possible
    5. CRITICAL: Include ALL {total_videos} videos in the plan
    6. Videos must be distributed within ±1 of the target {videos_per_day} videos per day

    Videos to organize:
    {video_titles}

    Return ONLY valid JSON in this format:
    [
        {{"day": 1, "videos": ["exactly {videos_per_day} videos here"]}},
        {{"day": 2, "videos": ["exactly {videos_per_day} videos here"]}},
        ...
    ]

    Verify before responding:
    1. Each day has {videos_per_day} videos (±1)
    2. All {total_videos} videos are included
    3. No videos are duplicated
    4. No videos are missing
    """)

    response = llm.invoke(
        prompt.format(
            total_days=total_days,
            video_titles=json.dumps(video_titles, indent=2),
            total_videos=len(video_titles),
            videos_per_day=round(videos_per_day, 1)
        )
    )
    
    response_text = response.content.strip() if isinstance(response, AIMessage) else str(response).strip()

    try:
        cleaned_response = clean_json_response(response_text)
        study_plan = json.loads(cleaned_response)
        
        # Verify the study plan meets requirements
        total_assigned = sum(len(day['videos']) for day in study_plan)
        videos_set = set()
        for day in study_plan:
            videos_set.update(day['videos'])
            
        # Check if any videos are missing
        all_videos_set = set(video_titles)
        missing_videos = all_videos_set - videos_set
        extra_videos = videos_set - all_videos_set
        
        if missing_videos or extra_videos or total_assigned != len(video_titles):
            # Redistribute if there are any issues
            videos_copy = video_titles.copy()
            base_per_day = len(videos_copy) // total_days
            extra = len(videos_copy) % total_days
            
            study_plan = []
            start_idx = 0
            
            for day in range(1, total_days + 1):
                videos_today = base_per_day + (1 if day <= extra else 0)
                end_idx = start_idx + videos_today
                
                study_plan.append({
                    "day": day,
                    "videos": videos_copy[start_idx:end_idx]
                })
                
                start_idx = end_idx
        
        return study_plan
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response: {str(e)}\nRaw response: {response_text}")