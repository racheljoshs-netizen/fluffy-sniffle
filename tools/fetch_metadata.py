
import requests
import re
import sys

def get_video_info(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"[*] Fetching metadata for {video_id}...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
        
        # Extract Title
        title_match = re.search(r'<meta name="title" content="(.*?)">', html)
        title = title_match.group(1) if title_match else "Unknown Title"
        
        # Extract Description
        desc_match = re.search(r'<meta name="description" content="(.*?)">', html)
        description = desc_match.group(1) if desc_match else "No description found."
        
        print(f"\nVIDEO META:")
        print(f"Title: {title}")
        print(f"Description: {description}")
        return title, description
        
    except Exception as e:
        print(f"[!] Error fetching video: {e}")
        return None, None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        vid = sys.argv[1]
    else:
        vid = "Qkqe-uRhQJE" # Default from user
        
    get_video_info(vid)
