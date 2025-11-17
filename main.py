import streamlit as st
from googleapiclient.discovery import build
import random
import re

st.set_page_config(page_title="유튜브 댓글 추첨기", layout="wide")

st.title("🎉 유튜브 댓글 추첨기 (YouTube Comment Picker)")
st.write("YouTube Data API와 Streamlit을 활용한 댓글 추첨기입니다.")

# 🔐 Streamlit Secret에서 API KEY 가져오기
API_KEY = st.secrets["api"]["youtube_api_key"]

def extract_video_id(url_or_id):
    """
    유튜브 URL 전체를 넣어도 videoId만 뽑아주는 함수
    """
    # 이미 ID 형태라면 바로 반환
    if len(url_or_id) == 11 and "/" not in url_or_id:
        return url_or_id

    # watch?v= 형식
    match = re.search(r"v=([^&]+)", url_or_id)
    if match:
        return match.group(1)

    # youtu.be 단축 URL
    match = re.search(r"youtu\.be/([^?&]+)", url_or_id)
    if match:
        return match.group(1)

    # shorts 형식
    match = re.search(r"shorts/([^?&]+)", url_or_id)
    if match:
        return match.group(1)

    # 실패 시 None
    return None


def get_comments(api_key, video_id):
    youtube = build("youtube", "v3", developerKey=api_key)
    comments = []
    next_page_token = None

    while True:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token,
            order="relevance"
        ).execute()

        for item in response["items"]:
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "author": snippet["authorDisplayName"],
                "text": snippet["textDisplay"],
            })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return comments


# 입력
user_input = st.text_input("🎬 유튜브 URL 또는 Video ID 입력")

# 댓글 불러오기
if st.button("📥 댓글 불러오기"):
    video_id = extract_video_id(user_input)

    if not video_id:
        st.error("유효한 유튜브 URL 또는 Video ID를 입력해주세요!")
    else:
        with st.spinner(f"댓글 불러오는 중... (Video ID: {video_id})"):
            try:
                comments = get_comments(API_KEY, video_id)
                st.session_state["comments"] = comments
                st.success(f"총 {len(comments)}개의 댓글을 불러왔습니다!")
            except Exception as e:
                st.error(f"오류 발생: {e}")


# 추첨
if "comments" in st.session_state:
    if st.button("🎯 당첨자 뽑기"):
        winner = random.choice(st.session_state["comments"])
        st.subheader("🎉 당첨자 발표!")
        st.write(f"👤 **작성자:** {winner['author']}")
        st.info(f"💬 {winner['text']}")

    with st.expander("📄 전체 댓글 보기"):
        for c in st.session_state["comments"]:
            st.write(f"👤 **{c['author']}**: {c['text']}")
