import streamlit as st
from googleapiclient.discovery import build
import random

st.set_page_config(page_title="유튜브 댓글 추첨기", layout="wide")

st.title("🎉 유튜브 댓글 추첨기 (YouTube Comment Picker)")
st.write("YouTube API로 댓글을 조회하고, 무작위로 당첨자를 선택합니다.")

# 입력 폼
api_key = st.text_input("🔑 YouTube API Key 입력", type="password")
video_id = st.text_input("🎬 유튜브 Video ID 입력 (예: dQw4w9WgXcQ)")

# 댓글 불러오기 함수
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
                "text": snippet["textDisplay"]
            })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return comments


# 버튼 클릭 시 실행
if st.button("📥 댓글 불러오기"):
    if not api_key or not video_id:
        st.error("API Key와 Video ID를 모두 입력해주세요.")
    else:
        with st.spinner("댓글을 불러오는 중입니다..."):
            try:
                comments = get_comments(api_key, video_id)
                st.success(f"총 {len(comments)}개의 댓글을 불러왔습니다!")
                st.session_state["comments"] = comments
            except Exception as e:
                st.error(f"오류 발생: {e}")

# 추첨하기
if "comments" in st.session_state:
    if st.button("🎯 당첨자 뽑기"):
        winner = random.choice(st.session_state["comments"])
        st.subheader("🎉 당첨자 발표")
        st.write(f"**작성자:** {winner['author']}")
        st.write(f"**댓글 내용:**")
        st.info(winner['text'])

    # 원하면 전체 댓글도 보여줄 수 있음
    with st.expander("📄 전체 댓글 보기"):
        for c in st.session_state["comments"]:
            st.write(f"👤 **{c['author']}**: {c['text']}")
