import webbrowser
import urllib.parse

def search_google(query: str) -> str:
    """
    Opens default browser and performs a Google search.
    """
    cleaned_query = query.replace("search", "").replace("google", "").strip()
    if not cleaned_query:
        return "What would you like me to search for?"
    
    encoded_query = urllib.parse.quote(cleaned_query)
    url = f"https://www.google.com/search?q={encoded_query}"
    webbrowser.open(url)
    return f"Searching Google for {cleaned_query}."

def play_youtube(query: str) -> str:
    """
    Opens YouTube search or direct playback in browser.
    """
    cleaned_query = query.replace("play", "").replace("youtube", "").strip()
    if not cleaned_query:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."
    
    encoded_query = urllib.parse.quote(cleaned_query)
    url = f"https://www.youtube.com/results?search_query={encoded_query}"
    webbrowser.open(url)
    return f"Searching YouTube for {cleaned_query}."

def open_website(url: str) -> str:
    """
    Opens a specific URL or popular website directly.
    """
    url = url.lower().replace("open", "").strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        if "." in url:
            url = f"https://{url}"
        else:
            url = f"https://www.{url}.com"
            
    webbrowser.open(url)
    return f"Opening {url}."