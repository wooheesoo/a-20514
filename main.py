import streamlit as st
st.title("나의 데이터 과학 포트폴리오")
st.write("반갑습니다! 이제부터 여기에 제 작업을 기록합니다.")
st.write("우희수.")
import datetime
import pandas as pd
import requests
import streamlit as st

# 1. 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(
    page_title="일별 박스오피스 순위", page_icon="🎬", layout="wide"
)

st.title("🎬 일별 박스오피스 조회")

# 2. 한국 시간(KST) 기준 '오늘'과 '어제' 날짜 계산
# 배포 서버의 시계(UTC 등)와 무관하게 항상 한국 시간을 적용합니다.
kst_timezone = datetime.timezone(datetime.timedelta(hours=9))
today_kst = datetime.datetime.now(kst_timezone).date()
yesterday_kst = today_kst - datetime.timedelta(days=1)

# 3. 달력(날짜 선택기) 배치
# 선택 가능한 가장 늦은 날짜는 어제(yesterday_kst)로 제한합니다.
selected_date = st.date_input(
    "📅 조회할 날짜를 선택하세요 (오늘 날짜는 미집계 상태이므로 어제까지만 선택 가능합니다)",
    value=yesterday_kst,
    max_value=yesterday_kst,
    min_value=datetime.date(2004, 1, 1),  # KOBIS 데이터 제공 시작 시점
)

target_date = selected_date.strftime("%Y%m%d")  # API 요청용 포맷 (YYYYMMDD)
display_date = selected_date.strftime("%Y년 %m월 %d일")  # 화면 표시용 포맷


# 4. KOBIS API 데이터 호출 함수 (1시간 간격 캐싱)
# 같은 날짜를 선택했을 때 API를 다시 호출하지 않고 캐시된 결과를 사용합니다.
@st.cache_data(ttl=3600)
def fetch_box_office_data(target_date_str):
    # 비밀 금고(st.secrets)에서 API 인증키 검증
    if "KOBIS_KEY" not in st.secrets:
        return None, "Secrets 설정에 'KOBIS_KEY'가 누락되었습니다."

    api_key = st.secrets["KOBIS_KEY"]
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_date_str}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # faultInfo가 응답에 포함된 경우 (인증키 오류 등)
        if "faultInfo" in data:
            fault_msg = data["faultInfo"].get(
                "message", "인증 오류가 발생했습니다."
            )
            return None, f"KOBIS 오류 응답: {fault_msg}"

        # 영화 목록 추출
        daily_list = (
            data.get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])
        )

        # 영화 목록이 비어 있는 경우 특수 상태 반환
        if not daily_list:
            return [], "EMPTY"

        return daily_list, None

    except requests.exceptions.RequestException as err:
        return None, f"네트워크 요청 실패: {err}"


# 5. 데이터 로드 및 예외/오류 처리
daily_list, error_message = fetch_box_office_data(target_date)

# 영화 목록이 비어 있을 때
if error_message == "EMPTY":
    st.info("💡 그날은 아직 집계 전입니다.")

# 그 외 API 또는 네트워크 오류 발생 시
elif error_message:
    st.error("데이터를 불러오지 못했습니다.")

    st.warning("💡 **다음 사항을 확인해 주세요:**")
    st.markdown(
        """
    1. **Secrets 설정 확인**: Streamlit Cloud의 `Secrets` 항목에 `KOBIS_KEY = "발급받은키"`가 제대로 입력되어 있는지 확인해 주세요.
    2. **API 키 유효성**: KOBIS 오픈 API 마이페이지에서 발급받은 인증키가 활성화 상태인지 확인해 주세요.
    3. **네트워크 및 점검**: KOBIS 서버 응답 지연일 수 있으니 잠시 후 다시 시도해 주세요.
    """
    )
    st.info(f"🔎 상세 메시지: {error_message}")

# 데이터가 정상적으로 수신된 경우
else:
    # 6. 데이터 전처리 (문자열 -> 숫자 형변환)
    df = pd.DataFrame(daily_list)

    numeric_columns = ["rank", "rankInten", "audiCnt", "audiAcc", "scrnCnt"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 7. 누적관객 100만 명 이상 영화에 트로피 이모지(🏆) 추가
    def format_movie_name(row):
        name = row["movieNm"]
        if row["audiAcc"] >= 1_000_000:
            return f"{name} 🏆"
        return name

    df["movieNm_display"] = df.apply(format_movie_name, axis=1)

    # 8. 전날 대비 순위 증감(rankInten) 화살표 포맷팅
    # 양수: 빨간 위 화살표(🔺), 음수: 파란 아래 화살표(🔻)
    def format_rank_change(val):
        if val > 0:
            return f"🔺 {val}"
        elif val < 0:
            return f"🔻 {abs(val)}"
        else:
            return "-"

    df["rankInten_display"] = df["rankInten"].apply(format_rank_change)

    st.caption(f"📌 **{display_date}** 박스오피스 집계 결과입니다.")

    # 9. 1위 영화 지표 카드 3장
    top_movie = df.iloc[0]
    st.subheader(f"🏆 1위: {top_movie['movieNm_display']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("당일 관객수", f"{top_movie['audiCnt']:,} 명")
    col2.metric("누적 관객수", f"{top_movie['audiAcc']:,} 명")
    col3.metric("스크린수", f"{top_movie['scrnCnt']:,} 개")

    st.divider()

    # 10. 관객수 상위 5편 막대그래프
    st.subheader("📊 관객수 상위 5개 영화")
    top5_df = df.head(5)[["movieNm_display", "audiCnt"]].set_index(
        "movieNm_display"
    )
    st.bar_chart(top5_df)

    st.divider()

    # 11. 전체 순위 표 출력 (순위 증감 및 트로피 표기 포함)
    st.subheader("📋 전체 박스오피스 순위")

    display_df = df[
        [
            "rank",
            "rankInten_display",
            "movieNm_display",
            "openDt",
            "audiCnt",
            "audiAcc",
            "scrnCnt",
        ]
    ].copy()

    display_df.columns = [
        "순위",
        "전날 대비",
        "영화명",
        "개봉일",
        "관객수",
        "누적관객",
        "스크린수",
    ]

    # 천 단위 쉼표 포맷 적용 및 정렬된 데이터프레임 출력
    st.dataframe(
        display_df.style.format(
            {"관객수": "{:,}", "누적관객": "{:,}", "스크린수": "{:,}"}
        ),
        use_container_width=True,
        hide_index=True,
    )
