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

genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['genre', 'count']

fig_donut = px.pie(
    genre_counts,
    values='count',
    names='genre',
    hole=0.4,
    title='장르별 영화 편수 비율'
)

fig_donut.update_traces(
    hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>"
)

st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("##### 💡 이 그래프로 알 수 있는 것")
st.caption("박스오피스 상위권 영화 중 가장 높은 비중을 차지하는 대표 장르가 무엇인지 한눈에 파악할 수 있습니다.")

st.divider()

# -------------------------------------------------------------------
# 구역 2: 장르 및 영화별 총 관객 수 (트리맵)
# -------------------------------------------------------------------
st.subheader("2. 장르 및 영화별 총 관객 수 분포")

fig_treemap = px.treemap(
    df,
    path=['genre', 'movieNm'],
    values='total_audi',
    title='장르 및 영화별 총 관객 수 (트리맵)'
)

fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객 수: %{value:,}명<extra></extra>"
)

st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("##### 💡 이 그래프로 알 수 있는 것")
st.caption("장르별 전체 관객 규모와 더불어, 특정 장르 내에서 어떤 영화가 가장 많은 관객을 모으며 흥행을 이끌었는지 직관적으로 알 수 있습니다.")

st.divider()

# -------------------------------------------------------------------
# 구역 3: 총 관객 수 분포 (히스토그램)
# -------------------------------------------------------------------
st.subheader("3. 총 관객 수 분포")

fig_hist = px.histogram(
    df,
    x='total_audi',
    nbins=20,
    title='영화별 총 관객 수 분포 (히스토그램)',
    labels={'total_audi': '총 관객 수'}
)

fig_hist.update_traces(
    hovertemplate="관객 수 구간: %{x}<br>영화 수: %{y}편<extra></extra>"
)

st.plotly_chart(fig_hist, use_container_width=True)

# 가장 관객 수가 많은 영화 정보 동적 추출
top_movie = df.loc[df['total_audi'].idxmax()]
top_movie_name = top_movie['movieNm']
top_movie_audi = top_movie['total_audi']

st.markdown("##### 💡 이 그래프로 알 수 있는 것")
st.caption(
    f"대부분의 영화가 **500만 명 미만 구간**에 집중되어 있으며, "
    f"가장 많은 관객을 모은 영화는 **'{top_movie_name}'**(약 {top_movie_audi:,}명)입니다."
)

st.divider()

# -------------------------------------------------------------------
# 구역 4: 개봉일 스크린 수와 총 관객 수의 관계 (산점도)
# -------------------------------------------------------------------
st.subheader("4. 개봉일 스크린 수와 총 관객 수의 관계")

fig_scatter = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    color='genre',
    hover_name='movieNm',
    title='개봉일 스크린 수 vs 총 관객 수 (장르별 구분)',
    labels={
        'first_scrn': '개봉일 스크린 수',
        'total_audi': '총 관객 수',
        'genre': '장르'
    }
)

fig_scatter.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린 수: %{x:,}개<br>총 관객 수: %{y:,}명<extra></extra>"
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("##### 💡 이 그래프로 알 수 있는 것")
st.caption("개봉일 스크린 수가 많을수록 총 관객 수가 늘어나는 양의 상관관계를 볼 수 있으며, 장르별 스크린 확보 및 흥행 성과의 분포 양상을 파악할 수 있습니다.")

st.divider()

# -------------------------------------------------------------------
# 구역 5: 주요 장르별 총 관객 수 분포 (상자 그림)
# -------------------------------------------------------------------
st.subheader("5. 주요 장르별 총 관객 수 분포")

genre_counts_series = df['genre'].value_counts()
major_genres = genre_counts_series[genre_counts_series >= 10].index
df_major = df[df['genre'].isin(major_genres)]

fig_box = px.box(
    df_major,
    x='genre',
    y='total_audi',
    color='genre',
    hover_name='movieNm',
    title='영화 10편 이상인 장르별 총 관객 수 분포 (상자 그림)',
    labels={
        'genre': '장르',
        'total_audi': '총 관객 수'
    }
)

fig_box.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>총 관객 수: %{y:,}명<extra></extra>"
)

st.plotly_chart(fig_box, use_container_width=True)

st.markdown("##### 💡 이 그래프로 알 수 있는 것")
st.caption("주요 장르별 관객 수의 중앙값과 범위를 비교할 수 있으며, 정상 범위를 넘어서는 대흥행작(이상치)이 어느 장르에 존재하는지 한눈에 파악할 수 있습니다.")

st.divider()

# -------------------------------------------------------------------
# 구역 6: 스크린 수, 총 관객 수, 첫 주 관객 수의 관계 (버블 그래프)
# -------------------------------------------------------------------
st.subheader("6. 스크린 수, 총 관객 수, 첫 주 관객 수의 관계")

fig_bubble = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    size='first_week_audi',
    color='genre',
    hover_name='movieNm',
    title='개봉일 스크린 수 vs 총 관객 수 (버블 크기: 개봉 첫 주 관객 수)',
    labels={
        'first_scrn': '개봉일 스크린 수',
        'total_audi': '총 관객 수',
        'first_week_audi': '개봉 첫 주 관객 수',
        'genre': '장르'
    },
    size_max=40
)

fig_bubble.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린 수: %{x:,}개<br>총 관객 수: %{y:,}명<extra></extra>"
)

st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("##### 💡 이 그래프로 알 수 있는 것")
st.caption("초반 흥행 화력(첫 주 관객 수)이 클수록 버블이 커지며, 개봉일 스크린 수와 최종 관객 수 사이에서 첫 주 관객 수의 영향력을 함께 다차원적으로 확인할 수 있습니다.")

st.divider()

# -------------------------------------------------------------------
# 구역 7: 제작 국가 및 장르별 영화 편수 (선버스트)
# -------------------------------------------------------------------
st.subheader("7. 제작 국가 및 장르별 영화 편수 분포")

# 선버스트 그래프 생성 (계층: nation -> genre)
fig_sunburst = px.sunburst(
    df,
    path=['nation', 'genre'],
    title='제작 국가 및 장르별 영화 편수 (선버스트)'
)

fig_sunburst.update_traces(
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<extra></extra>"
)

st.plotly_chart(fig_sunburst, use_container_width=True)

st.markdown("##### 💡 이 그래프로 알 수 있는 것")
st.caption("주요 제작 국가별로 어떤 장르의 영화들이 주로 개봉했는지 국가와 장르 간의 계층 구조와 비중을 한눈에 비교해 볼 수 있습니다.")

st.divider()
