import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import re
from collections import Counter
from wordcloud import WordCloud
from bs4 import BeautifulSoup

import matplotlib.font_manager as fm

font_path = "NanumGothic.ttf"
fm.fontManager.addfont(font_path)
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="2030세대 불교 붐 분석", layout="wide")
st.title("📿 2030세대 불교 붐 데이터 분석")
st.subheader("불교박람회 · MZ세대 불교 뉴스 분석")

# 사이드바 키워드 입력
query = st.sidebar.text_input("검색 키워드 입력", value="불교박람회", placeholder="예: 불교, 불교 굿즈")

# 뉴스 수집 함수
def crawl_news(query):
    url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")
    news_data = []
    for item in items[:30]:
        title = item.title.text
        link = item.link.text
        news_data.append({"title": title, "link": link})
    return pd.DataFrame(news_data)

# 메인 화면에 버튼
if st.button("🔍 뉴스 데이터 수집"):
    with st.spinner("뉴스 수집 중..."):
        df = crawl_news(query)
        st.session_state["df"] = df
    st.success(f"'{query}' 뉴스 {len(df)}개 수집 완료!")

# 분석
if "df" in st.session_state:
    df = st.session_state["df"]

    if len(df) == 0:
        st.error("뉴스 데이터를 가져오지 못했습니다.")
    else:
        st.subheader("📰 수집된 뉴스 데이터")
        st.dataframe(df)

        text = " ".join(df["title"].astype(str))
        words = re.findall(r"[가-힣]{2,}", text)

        stopwords = ["세대", "관련", "기자", "뉴스", "한국", "대한", "이번", "통해", "불교", "박람회"]
        words = [w for w in words if w not in stopwords]

        counter = Counter(words)
        top_words = counter.most_common(15)
        word_df = pd.DataFrame(top_words, columns=["keyword", "count"])

        st.subheader("📊 주요 키워드 분석")
        st.dataframe(word_df)

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.bar(word_df["keyword"], word_df["count"], color="steelblue")
        ax.set_title("주요 키워드 빈도수")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        st.subheader("☁️ 워드클라우드")
        try:
           wc = WordCloud(font_path="NanumGothic.ttf", background_color="white", width=1000, height=500)
            cloud = wc.generate_from_frequencies(counter)
            fig2, ax2 = plt.subplots(figsize=(14, 7))
            ax2.imshow(cloud)
            ax2.axis("off")
            st.pyplot(fig2)
        except Exception as e:
            st.warning(f"워드클라우드 오류: {e}")

        positive_words = ["힐링", "인기", "열풍", "확산", "행복", "공감", "성장", "위로", "안정", "관심", "유행"]
        negative_words = ["논란", "비판", "우려", "감소", "문제", "갈등", "부족"]

        positive, negative = 0, 0
        for title in df["title"]:
            for p in positive_words:
                if p in title:
                    positive += 1
            for n in negative_words:
                if n in title:
                    negative += 1

        neutral = max(len(df) - (positive + negative), 0)

        sentiment_df = pd.DataFrame({
            "감정": ["긍정", "부정", "중립"],
            "개수": [positive, negative, neutral]
        })

        st.subheader("😊 감정분석 결과")
        st.dataframe(sentiment_df)

        fig3, ax3 = plt.subplots(figsize=(6, 6))
        ax3.pie(sentiment_df["개수"], labels=sentiment_df["감정"], autopct="%1.1f%%")
        ax3.set_title("감정분석 비율")
        st.pyplot(fig3)

        st.subheader("🧠 분석 결과 해석")
        st.write("""
        최근 2030세대 사이에서 불교는 힐링·명상·마음 안정 콘텐츠로 소비되고 있다.
        특히 불교박람회, 템플스테이 등이 MZ세대 문화와 결합하며 새로운 트렌드로 확산되고 있다.
        """)