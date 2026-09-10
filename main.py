import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# [설정] 페이지 기본 설정 (타이틀, 아이콘, 레이아웃)
st.set_page_config(
    page_title="영화 박스오피스 분석 앱", page_icon="🎬", layout="wide"
)


# [1. 데이터 불러오기]
# @st.cache_data 데코레이터를 사용해 데이터를 캐싱하여 앱 속도를 최적화합니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # [2. 날짜 전처리]
    # 결측치 행 제거 및 날짜 형식(datetime) 변환 후 정렬
    df = df.dropna()
    df["기준일자"] = pd.to_datetime(df["기준일자"])
    df = df.sort_values(by="기준일자")

    return df


# 데이터 로드
df = load_data()

# 웹앱 상단 제목 표시
st.title("🎬 영화 박스오피스 데이터 분석 웹앱")
st.write(
    "1년간의 박스오피스 데이터를 바탕으로 영화별 및 전체 시장 관객 수 추이를 분석합니다."
)

st.divider()

# [3. 영화 선택 기능]
# 누적관객수가 높은 순(내림차순)으로 정렬된 중복 없는 영화 목록 생성
sorted_movie_list = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 영화 선택 드롭다운 (단일 영화 분석용)
selected_movie = st.selectbox(
    "📊 단일 영화 상세 분석 - 영화를 선택하세요 (누적관객수 순 정렬):",
    options=sorted_movie_list,
)

# 선택된 영화의 데이터만 추출
filtered_df = df[df["영화명"] == selected_movie]

# -------------------------------------------------------------------
# [4. 구역 1: 선그래프 (일일 관객수)]
# -------------------------------------------------------------------
st.write("---")
with st.container():
    st.subheader(f"📈 '{selected_movie}' 일자별 관객수 변화 (선그래프)")

    # Plotly 선그래프 생성
    fig_line = px.line(
        filtered_df,
        x="기준일자",
        y="해당일관객수",
        title=f"<{selected_movie}> 기준일자별 관객수 추이",
        labels={"기준일자": "날짜", "해당일관객수": "일일 관객수(명)"},
        markers=True,
    )

    fig_line.update_layout(hovermode="x unified")
    st.plotly_chart(fig_line, use_container_width=True)

    # 그래프 1 설명 문구
    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** 개봉 이후 시간의 흐름에 따라 '{selected_movie}'의 일일 관객수가 어떻게 변화했는지(흥행 유지력 및 주말/평일 차이 등)를 한눈에 파악할 수 있습니다."
    )

# -------------------------------------------------------------------
# [5. 구역 2: 영역차트 (누적 관객수)]
# -------------------------------------------------------------------
st.write("---")
with st.container():
    st.subheader(f"🌊 '{selected_movie}' 누적 관객수 증가 추이 (영역차트)")

    # Plotly 영역차트 생성
    fig_area = px.area(
        filtered_df,
        x="기준일자",
        y="누적관객수",
        title=f"<{selected_movie}> 기준일자별 누적관객수 변화",
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)"},
    )

    fig_area.update_layout(hovermode="x unified")
    st.plotly_chart(fig_area, use_container_width=True)

    # 그래프 2 설명 문구
    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** 개봉일 이후 관객수가 쌓이는 곡선의 기울기를 통해 관객 동원 속도가 급증한 구간과 흥행 정체 구간을 한눈에 파악할 수 있습니다."
    )

# -------------------------------------------------------------------
# [6. 구역 3: 다중 선그래프 (20일 이상 상위 5개 영화 비교)]
# -------------------------------------------------------------------
st.write("---")
with st.container():
    st.subheader("🏆 장기 흥행 영화 TOP 5 누적 관객수 비교 (다중 선그래프)")

    # 1. 영화별 차트(Top10) 등장 일수 계산
    movie_day_counts = df.groupby("영화명")["기준일자"].nunique()

    # 2. 등장 일수가 20일 이상인 영화 목록 추출
    qualified_movies = movie_day_counts[movie_day_counts >= 20].index

    # 3. 20일 이상 등장 영화 중 누적관객수 상위 5개 영화 추출
    top5_qualified_movies = (
        df[df["영화명"].isin(qualified_movies)]
        .groupby("영화명")["누적관객수"]
        .max()
        .nlargest(5)
        .index.tolist()
    )

    # 4. 해당 5개 영화의 전체 데이터 필터링
    top5_df = df[df["영화명"].isin(top5_qualified_movies)]

    # 5. Plotly 다중 선그래프 생성
    fig_multi = px.line(
        top5_df,
        x="기준일자",
        y="누적관객수",
        color="영화명",
        title="20일 이상 차트인한 주요 장기 흥행작 TOP 5의 누적관객수 추이 비교",
        labels={
            "기준일자": "날짜",
            "누적관객수": "누적 관객수(명)",
            "영화명": "영화 제목",
        },
    )

    fig_multi.update_layout(hovermode="x unified")
    st.plotly_chart(fig_multi, use_container_width=True)

    # 그래프 3 설명 문구
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 박스오피스 순위권에 최소 20일 이상 머무른 '장기 흥행작' 중 상위 5개 영화의 누적 관객 증가 곡선을 통해, 꾸준히 관객을 모으며 장기 흥행에 성공한 대작들의 관객 동원 추이를 비교해볼 수 있습니다."
    )

# -------------------------------------------------------------------
# [7. 구역 4: 이동평균선 (전체 박스오피스 관객수 합계 및 7일 이동평균)]
# -------------------------------------------------------------------
st.write("---")
with st.container():
    st.subheader("📉 전체 박스오피스 관객수 추이 및 7일 이동평균선")

    # 1. 기준일자별 TOP10 영화 전체의 해당일관객수 합계 구하기
    daily_total = df.groupby("기준일자")["해당일관객수"].sum().reset_index()

    # 2. 7일 이동평균값 계산
    daily_total["7일_이동평균"] = (
        daily_total["해당일관객수"].rolling(window=7).mean()
    )

    # 3. Plotly graph_objects를 활용하여 두 개의 선 그래프를 커스텀 스타일로 작성
    fig_ma = go.Figure()

    # 원본 선: 일일 관객수 합계 (연한 색상, 얇은 선)
    fig_ma.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["해당일관객수"],
            mode="lines",
            name="일일 관객수 합계 (일별)",
            line=dict(color="rgba(180, 180, 180, 0.6)", width=1.5),
        )
    )

    # 이동평균 선: 7일 이동평균 (진한 색상, 두꺼운 선)
    fig_ma.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["7일_이동평균"],
            mode="lines",
            name="7일 이동평균",
            line=dict(color="#E53935", width=3),
        )
    )

    # 레이아웃 설정
    fig_ma.update_layout(
        title="전체 박스오피스 일일 총 관객수 및 7일 이동평균 추이",
        xaxis_title="날짜",
        yaxis_title="관객수(명)",
        hovermode="x unified",
    )

    st.plotly_chart(fig_ma, use_container_width=True)

    # 그래프 4 설명 문구
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 평일과 주말 간의 심한 관객수 변동(노이즈)을 평탄화하여, 전체 극장가의 성수기/비수기 시즌 흐름과 연중 총 관객수의 거시적인 상승/하락 트렌드를 명확하게 파악할 수 있습니다."
    )
