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

    # 3. Plotly graph_objects를 활용해 원본선과 이동평균선 생성
    fig_ma = go.Figure()

    # 원본 선 (일일 관객수 합계 - 연한 회색)
    fig_ma.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["해당일관객수"],
            mode="lines",
            name="일일 관객수 합계",
            line=dict(color="rgba(180, 180, 180, 0.6)", width=1.5),
        )
    )

    # 이동평균 선 (7일 이동평균 - 진한 빨간색)
    fig_ma.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["7일_이동평균"],
            mode="lines",
            name="7일 이동평균",
            line=dict(color="#E53935", width=3),
        )
    )

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

# -------------------------------------------------------------------
# [8. 구역 5: 막대그래프 (월별 전체 박스오피스 관객수 합계)]
# -------------------------------------------------------------------
st.write("---")
with st.container():
    st.subheader("📊 월별 전체 박스오피스 총 관객수 (막대그래프)")

    # 1. '기준일자별 전체 관객수 합계(daily_total)' 데이터를 '연-월(YYYY-MM)' 형식으로 변환
    daily_total["년월"] = daily_total["기준일자"].dt.strftime("%Y-%m")

    # 2. 월(연-월) 단위로 다시 그룹화하여 합산
    monthly_total = daily_total.groupby("년월")["해당일관객수"].sum().reset_index()

    # 3. Plotly 막대그래프 생성
    fig_bar = px.bar(
        monthly_total,
        x="년월",
        y="해당일관객수",
        title="월별 총 박스오피스 관객수 집계",
        labels={"년월": "월(연-월)", "해당일관객수": "월간 총 관객수(명)"},
        text_auto=",",
    )

    fig_bar.update_layout(hovermode="x unified")
    st.plotly_chart(fig_bar, use_container_width=True)

    # 그래프 5 설명 문구
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 각 월별 총 관객수를 비교하여 1년 중 극장가 최고의 성수기 월(여름/겨울 방학, 연휴 등)과 비수기 월을 직관적으로 확인하고 월별 극장 이용 규모를 분석할 수 있습니다."
    )

# -------------------------------------------------------------------
# [9. 구역 6: 캘린더 히트맵 (월/주차별 x 요일별 관객수 히트맵)]
# -------------------------------------------------------------------
st.write("---")
with st.container():
    st.subheader("🗓️ 월(주차별) × 요일별 관객수 캘린더 히트맵")

    # 1. 히트맵용 가공 데이터프레임 생성
    heatmap_df = daily_total.copy()

    # 요일 한글 매핑 (0: 월요일 ~ 6: 일요일)
    weekday_map = {
        0: "월요일",
        1: "화요일",
        2: "수요일",
        3: "목요일",
        4: "금요일",
        5: "토요일",
        6: "일요일",
    }
    heatmap_df["요일"] = heatmap_df["기준일자"].dt.weekday.map(weekday_map)

    # 마우스 오버(Hover) 시 보여줄 YYYY-MM-DD 날짜 문자열
    heatmap_df["날짜_str"] = heatmap_df["기준일자"].dt.strftime("%Y-%m-%d")

    # 월 및 주차 구분 컬럼 생성 (예: 2023-05 (20주차))
    heatmap_df["월_주차"] = heatmap_df["기준일자"].dt.strftime(
        "%Y-%m (%W주차)"
    )

    # 2. 피벗 테이블 생성 (행: 요일, 열: 월_주차, 값: 해당일관객수 / 날짜_str)
    pivot_val = heatmap_df.pivot(
        index="요일", columns="월_주차", values="해당일관객수"
    )
    pivot_date = heatmap_df.pivot(
        index="요일", columns="월_주차", values="날짜_str"
    )

    # 3. 요일 순서 보장 (월요일 -> 일요일)
    weekday_order = [
        "월요일",
        "화요일",
        "수요일",
        "목요일",
        "금요일",
        "토요일",
        "일요일",
    ]
    pivot_val = pivot_val.reindex(weekday_order)
    pivot_date = pivot_date.reindex(weekday_order)

    # 4. 마우스 오버 시 표시할 Custom Hover 텍스트 매트릭스 생성
    hover_matrix = []
    for w in weekday_order:
        row_hover = []
        for col in pivot_val.columns:
            d_str = pivot_date.loc[w, col]
            val = pivot_val.loc[w, col]
            if pd.notna(d_str) and pd.notna(val):
                row_hover.append(
                    f"<b>날짜: {d_str}</b><br>일일 관객수: {int(val):,}명"
                )
            else:
                row_hover.append("")
        hover_matrix.append(row_hover)

    # 5. Plotly Heatmap 생성 (colorscale="Reds"로 관객수가 많을수록 진한 빨간색 표현)
    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=pivot_val.values,
            x=pivot_val.columns,
            y=pivot_val.index,
            text=hover_matrix,
            hoverinfo="text",
            colorscale="Reds",  # 색상이 진할수록 관객 수가 많음
            colorbar=dict(title="관객수(명)"),
        )
    )

    # 6. 레이아웃 설정 (월요일이 맨 위에 오도록 y축 역순 정렬)
    fig_heatmap.update_layout(
        title="주차별 및 요일별 일일 박스오피스 관객수 분포",
        xaxis_title="월 (주차)",
        yaxis_title="요일",
        yaxis=dict(autorange="reversed"),  # 월요일이 상단에 배치되도록 지정
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)

    # 그래프 6 설명 문구
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 특정 주차별·요일별 관객 동원 패턴을 히트맵으로 시각화하여, 주말(토/일)과 공휴일, 그리고 연중 특수 주차에 관객 몰림 현상이 얼마나 강하게 나타나는지 한눈에 파악할 수 있습니다."
    )
