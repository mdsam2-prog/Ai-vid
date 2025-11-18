# app.py - Streamlit Kling AI Video Generator
import streamlit as st
import requests
import time

st.set_page_config(page_title="Kling AI Video Generator", layout="centered")

# Load API key from Streamlit secrets (you'll add this secret on Streamlit Cloud)
API_KEY = st.secrets.get("KLING_API_KEY")

CREATE_TASK_URL = "https://api.klingai.com/v1/videos/text2video"
QUERY_TASK_URL = "https://api.klingai.com/v1/videos/{task_id}"

def create_video_task(prompt, duration="5", aspect_ratio="16:9", model="kling-v1"):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "model": model
    }
    resp = requests.post(CREATE_TASK_URL, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()["data"]["task_id"]

def query_video_status(task_id):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    url = QUERY_TASK_URL.format(task_id=task_id)
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()["data"]
    return data["task_status"], data.get("video")

def generate_video(prompt, duration, aspect_ratio):
    task_id = create_video_task(prompt, duration, aspect_ratio)
    with st.spinner("Task created. Generating video... (this can take 1–5 minutes)"):
        while True:
            status, video_url = query_video_status(task_id)
            if status == "succeed":
                return video_url
            if status == "failed":
                st.error("Video generation failed.")
                return None
            time.sleep(8)

st.title("Kling AI Video Generator")
st.write("Enter a short description and click Generate. (You must add your Kling API key in Streamlit Secrets.)")

prompt = st.text_input("Video description", placeholder="e.g., A futuristic city with flying cars at sunset")
duration = st.selectbox("Duration (seconds)", ["5", "10"])
aspect_ratio = st.selectbox("Aspect Ratio", ["16:9", "9:16", "1:1"])

if st.button("Generate Video"):
    if not API_KEY:
        st.error("API key not set. Add KLING_API_KEY in Streamlit Cloud Secrets (see instructions).")
    elif not prompt:
        st.error("Please write a prompt.")
    else:
        try:
            video_url = generate_video(prompt, duration, aspect_ratio)
            if video_url:
                st.success("Video generated!")
                st.video(video_url)
                st.markdown(f"[Download Video]({video_url})")
        except Exception as e:
            st.error(f"Error: {e}")
