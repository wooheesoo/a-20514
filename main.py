import pandas as pd
import plotly.express as px
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
    "1년간의 박스오피스 데이터를 바탕으로 영화별 관객 수 추이를 분석합니다."
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

# 영화 선택 드롭다운
selected_movie = st.selectbox(
    "📊 분석할 영화를 선택하세요 (누적관객수 순 정렬):", options=sorted_movie_list
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

    # Plotly 영역차트(px.area) 생성
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
