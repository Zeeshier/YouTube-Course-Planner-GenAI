# 🎥 AI-Powered YouTube Study Planner 📚

An AI-powered tool that transforms YouTube playlists into structured study plans using LangChain and Groq LLM. Perfect for online courses, tutorials, and educational content.

## 🌟 Features

* **Intelligent Video Distribution**: Uses AI to organize videos into logical, balanced study sessions  
* **Custom Study Duration**: Flexible planning based on your available study days  
* **PDF Export**: Download your study plan for offline reference  
* **Topic Grouping**: Keeps related content together for better learning flow  
* **Equal Distribution**: Ensures balanced workload across study days  
* **Beautiful UI**: Clean, responsive interface built with Streamlit  

## 💡 How It Works 

**1. Video Fetching**
- Uses the YouTube Data API to retrieve playlist information. 

**2. AI Processing**
- Analyzes video titles and metadata.
- Groups related topics together. 
- Distributes content evenly across study days. 

**3. Study Plan Generation**
- Creates balanced daily schedules. 
- Ensures logical learning progression. 

**4. PDF Creation**
- Generates downloadable study plans.

## 🔑 Getting API Keys 

### YouTube API Key 
1. Go to Google Cloud Console. 
2. Create a new project or select an existing one. 
3. Enable YouTube Data API v3. 
4. Generate API credentials and copy the API key. 
5. Add the key to your .env file. 

### Groq API Key
1. Sign up at Groq. 
2. Generate an API key from your dashboard. 
3. Add the key to your .env file. 

## 🔧 Project Structure 
YouTube-Course-Planner-GenAI/ 

1. app.py              # Main Streamlit application 
2. utils.py            # Utility functions 
3. requirements.txt    # Project dependencies 
4. .env                # Environment variables (create this) 
5. .gitignore          # Git ignore file 
6.  README.md           # Project documentation 



## Install required packages:

pip install -r requirements.txt

**Set up environment variables:**
Create a .env file in the project root with:

* YOUTUBE_API_KEY=your_youtube_api_key_here
* GROQ_API_KEY=your_groq_api_key_here

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/zeeshier/YouTube-Course-Planner-GenAI.git
cd YouTube-Course-Planner-GenAI
