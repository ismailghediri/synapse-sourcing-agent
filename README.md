
# Synapse Recruitment Automation

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Caching](https://img.shields.io/badge/caching-pickle%2Btimestamp-yellowgreen)
![License](https://img.shields.io/badge/license-MIT-green)

This work takes part of Synapse Annual First Ever AI Hackathon - Sourcing Agent Challenge.

It's an automated pipeline that:
1. 📝 Processes job descriptions
2. 🔍 Finds matching LinkedIn candidates, caches them to avoid refetching
3. 💯 Scores candidates intelligently
4. ✉️ Generates personalized outreach

### Advanced Cache Features
```python
# cache.pkl structure (automatically maintained)
{
    "linkedin_url": {
        "profile": {candidate_data},
        "timestamp": "2023-11-20T14:30:00"  # 7-day expiration
    }
}
```

## 🚀 Quick Start

# 1. Clone repo
```bash
git clone https://github.com/ismailghediri/synapse-sourcing-agent.git
cd synapse-ai-sourcing-agent
```

# 2. Install dependencies
```bash
pip install -r requirements-api.txt
```

# 3. Configure API Keys (Optional for Local Use)
Create a .env file in the root directory with your own API keys:
```bash
SERPER_API_KEY=your_serper_api_key
GEMINI_API_KEY=your_gemini_api_key
```
Note: .env is ignored in .gitignore to prevent exposure. Not required if using the Space.

# 4. Run Locally
```bash
uvicorn app:app --reload
```
Access the FastAPI UI at http://127.0.0.1:8000/docs to test endpoints. Without keys, test mode activates.

# 5. Run with Docker:
```bash
docker build -t synapse-agent .
docker run -p 8000:8000 synapse-agent
```
Add your .env file to the container if using local keys.


## 🛠️ Usage
Hosted on Hugging Face Spaces with an Interactive UI: https://ismailghediri-synapse-recruiter-api.hf.space/docs
Uses Space Secrets for SERPER_API_KEY and GEMINI_API_KEY, enabling full functionality without local configuration.

Or run directly:
```bash
python main.py
```
You can change job_url variable in main.py with the job description you want.

## ⚙️ How It Works
Pipeline Architecture

```mermaid
graph TD
    A[Job URL] --> B[Pre-Process Description]
    B --> C{{Cache Check}}
    C -->|Cached| D[Load Candidates]
    C -->|New| E[Fetch from LinkedIn]
    E --> F[Score & Cache]
    F --> G[Generate Messages]
    G --> H[Output Ranked Candidates]
```

Data Flow
```mermaid
sequenceDiagram
    participant User
    participant Cache
    participant LinkedIn
    participant Gemini
    
    User->>Cache: Check existing candidates
    alt Cache Hit
        Cache-->>User: Return cached data
    else Cache Miss
        User->>LinkedIn: Search profiles
        LinkedIn-->>User: New candidates
        User->>Cache: Store with timestamp
    end
    User->>Gemini: Generate messages
    Gemini-->>User: Personalized outreach
```

## 🔑Key Components
File	Purpose

job_input.py	Extracts job details using Selenium

search_linkedin.py	Finds candidates via Serper API

score_candidates.py	Rates candidates (0-10)

generate_outreach.py	Crafts messages with Gemini AI

## 📊 Scoring Metrics

35% Skills match

25% Experience level

20% Education

10% Location

10% Career trajectory

## 🚨 Troubleshooting
Cache-Specific Issues:
```bash
# Reset corrupted cache
echo "{}" > cache.pkl

# Permission issues
chmod 644 cache.pkl

# Debug cache hits
grep "Loading from cache" search_linkedin.py
```

Common Issues:
```bash
# If Selenium fails:
pip install --upgrade webdriver-manager selenium

# Missing Chrome (Linux):
sudo apt install -y chromium-browser

# API errors:
1. Check quota at https://ai.google.dev
2. Verify keys in .env
```
