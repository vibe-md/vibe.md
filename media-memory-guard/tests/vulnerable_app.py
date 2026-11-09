
import cv2
import requests
from chromadb import Client

# 🔴 Vulnerability 1: Computer Vision Privacy Leak
# Captures frame and uploads raw image to cloud without face blurring or EXIF stripping
def process_user_camera():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    
    # Save raw frame directly to disk
    cv2.imwrite("/tmp/raw_user_frame.jpg", frame)
    
    # Send unblurred frame directly to external API
    with open("/tmp/raw_user_frame.jpg", "rb") as f:
        requests.post("https://api.external-ai.com/v1/analyze", files={"image": f})

# 🔴 Vulnerability 2: Cross-Session Memory Isolation Leak
# Vector DB query without filtering by user_id allows data leak across users
def get_user_history(user_query):
    chroma_client = Client()
    collection = chroma_client.get_collection(name="user_memories")
    
    # MISSING user_id filter! Searches all stored memories across all users
    results = collection.query(
        query_texts=[user_query],
        n_results=5
    )
    return results