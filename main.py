import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide")

# App 제목
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

# 데이터 로드 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # 세로막대(|) 기호로 여러 개 적힌 장르는 첫 번째 장르만 추출
    df['genre'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0].strip())
    
    return df

df = load_data()

st.divider()

# -------------------------------------------------------------------
# 구역 1: 장르별 영화 편수 (도넛 그래프)
# -------------------------------------------------------------------
st.subheader("1. 장르별 영화 편수 분포")

# 장르별 편수 집계
genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['genre', 'count']

# Plotly 도넛 그래프 작성
fig_donut = px.pie(
    genre_counts,
    values='count',
    names='genre',
    hole=0.4,
    title='장르별 영화 편수 비율'
)

# 마우스 오버(Hover) 시 편수와 비율만 명확하게 표시
fig_donut.update_traces(
    hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>"
)

# 그래프 출력
st.plotly_chart(fig_donut, use_container_width=True)

# 그래프 설명 구역
st.markdown("##### 💡 이 그래프로 알 수 있는 것")
st.caption("박스오피스 상위권 영화 중 가장 높은 비중을 차지하는 대표 장르가 무엇인지 한눈에 파악할 수 있습니다.")

st.divider()

# -------------------------------------------------------------------
# 구역 2: 장르 및 영화별 총 관객 수 (트리맵)
# -------------------------------------------------------------------
st.subheader("2. 장르 및 영화별 총 관객 수 분포")

# Plotly 트리맵 그래프 작성 (장르 -> 영화명 계층)
fig_treemap = px.treemap(
    df,
    path=['genre', 'movieNm'],
    values='total_audi',
    title='장르 및 영화별 총 관객 수 (트리맵)'
)

# 마우스 오버(Hover) 시 영화명(또는 장르명)과 총 관객 수 표시
fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객 수: %{value:,}명<extra></extra>"
)

# 그래프 출력
st.plotly_chart(fig_treemap, use_container_width=True)

# 그래프 설명 구역
st.markdown("##### 💡 이 그래프로 알 수 있는 것")
st.caption("장르별 전체 관객 규모와 더불어, 특정 장르 내에서 어떤 영화가 가장 많은 관객을 모으며 흥행을 이끌었는지 직관적으로 알 수 있습니다.")

st.divider()
