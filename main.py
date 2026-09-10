import pandas as pd
import plotly.express as px
import streamlit as st

# [설정] 페이지 기본 설정 (타이틀, 아이콘, 레이아웃)
st.set_page_config(
    page_title="영화 박스오피스 분석 앱", page_icon="🎬", layout="wide"
)


# [1. 데이터 불러오기]
# @st.cache_data 데코레이터를 사용하면 데이터를 처음 한 번만 다운로드하여 캐시에 저장합니다.
# 앱을 새로고침하거나 옵션을 변경해도 재다운로드하지 않아 속도가 크게 향상됩니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # [2. 날짜 전처리]
    # 결측치(빈 데이터)가 포함된 행을 삭제합니다.
    df = df.dropna()

    # "기준일자" 컬럼을 날짜(datetime) 형식으로 변환합니다.
    df["기준일자"] = pd.to_datetime(df["기준일자"])

    # 전체 데이터를 기준일자 순서대로 오름차순 정렬합니다.
    df = df.sort_values(by="기준일자")

    return df


# 데이터 불러오기 실행
df = load_data()

# 웹앱 상단 제목 표시
st.title("🎬 영화 박스오피스 데이터 분석 웹앱")
st.write(
    "1년간의 박스오피스 데이터를 바탕으로 영화별 관객 수 추이를 분석합니다."
)

st.divider()  # 구분선 추가

# [3. 영화 선택 기능]
# 영화별 최대 누적관객수를 구해서 내림차순(가장 높은 순)으로 정렬된 영화 목록을 만듭니다.
sorted_movie_list = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 사용자 선택용 드롭다운 상자 생성
selected_movie = st.selectbox(
    "📊 분석할 영화를 선택하세요 (누적관객수 순 정렬):", options=sorted_movie_list
)

# 사용자가 선택한 영화 데이터만 필터링합니다.
filtered_df = df[df["영화명"] == selected_movie]

# [5. 기타 - 구역 1: 선그래프 영역]
st.write("---")
with st.container():
    st.subheader(f"📈 '{selected_movie}' 일자별 관객수 변화")

    # [4. 선그래프 그리기]
    # Plotly를 사용하여 기준일자별 해당일관객수 변화를 그립니다.
    fig = px.line(
        filtered_df,
        x="기준일자",
        y="해당일관객수",
        title=f"<{selected_movie}> 기준일자별 관객수 추이",
        labels={"기준일자": "날짜", "해당일관객수": "일일 관객수(명)"},
        markers=True,  # 그래프 선에 데이터 점 표시
    )

    # 그래프 디자인 레이아웃 조정
    fig.update_layout(hovermode="x unified")

    # Streamlit 화면에 그래프 출력
    st.plotly_chart(fig, use_container_width=True)

    # 그래프 하단 설명 문구 영역
    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** 개봉 이후 시간의 흐름에 따라 '{selected_movie}'의 일일 관객수가 어떻게 변화했는지(흥행 유지력 및 주말/평일 차이 등)를 한눈에 파악할 수 있습니다."
    )

# [5. 기타 - 구역 2: 추후 그래프 추가용 예시 공간]
st.write("---")
with st.container():
    st.subheader("📌 추가 분석 구역 (예정)")
    st.caption("이곳에 새로운 데이터 그래프를 추가로 배치할 수 있습니다.")

    # 하단 설명 문구 틀 미리 생성
    st.info("💡 **이 그래프로 알 수 있는 것:** (추가 분석 내용을 입력하세요)")
