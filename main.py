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
    page_title="어제 박스오피스 순위", page_icon="🎬", layout="wide"
)

st.title("🎬 어제 일별 박스오피스")


# 2. KOBIS API 데이터 호출 함수 (1시간 간격 캐싱)
# 같은 날짜 요청 시 API 재호출을 방지하여 응답 속도를 높입니다.
@st.cache_data(ttl=3600)
def fetch_box_office_data(target_date):
    # 비밀 금고(st.secrets)에서 API 인증키 불러오기
    if "KOBIS_KEY" not in st.secrets:
        return None, "Secrets 설정에 'KOBIS_KEY'가 누락되었습니다."

    api_key = st.secrets["KOBIS_KEY"]
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_date}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 인증키 오류 등 faultInfo 상자가 반환된 경우 처리
        if "faultInfo" in data:
            fault_msg = data["faultInfo"].get(
                "message", "인증 오류가 발생했습니다."
            )
            return None, f"KOBIS 오류 응답: {fault_msg}"

        # 영화 목록 추출
        daily_list = (
            data.get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])
        )

        if not daily_list:
            return None, "조회된 영화 목록이 비어 있습니다."

        return daily_list, None

    except requests.exceptions.RequestException as err:
        return None, f"네트워크 요청 실패: {err}"


# 3. 한국 시간(KST) 기준 '어제' 날짜 구하기
# 배포 서버 시계와 무관하게 UTC+9 기준을 적용합니다.
kst_timezone = datetime.timezone(datetime.timedelta(hours=9))
today_kst = datetime.datetime.now(kst_timezone)
yesterday_kst = today_kst - datetime.timedelta(days=1)

target_date = yesterday_kst.strftime("%Y%m%d")  # API 조회용 (YYYYMMDD)
display_date = yesterday_kst.strftime("%Y년 %m월 %d일")  # 화면 표시용

st.caption(f"📅 조회 기준일(한국 시간): {display_date}")

# 4. 데이터 로드 및 예외/오류 처리
daily_list, error_message = fetch_box_office_data(target_date)

if error_message:
    st.error("데이터를 불러오지 못했습니다.")

    # 사용자 안내 박스
    st.warning("💡 **다음 사항을 확인해 주세요:**")
    st.markdown(
        """
    1. **Secrets 설정 확인**: Streamlit Cloud의 `Secrets` 항목에 `KOBIS_KEY = "발급받은키"`가 등록되어 있는지 확인해 주세요.
    2. **API 키 유효성**: KOBIS 오픈 API 마이페이지에서 발급받은 인증키가 활성화 상태인지 확인해 주세요.
    3. **네트워크 및 점검**: KOBIS 서버 응답 지연 또는 일시적 데이터 집계 지연일 수 있습니다.
    """
    )

    st.info(f"🔎 상세 메시지: {error_message}")

else:
    # 5. 데이터 전처리 (문자열 -> 숫자 형변환)
    df = pd.DataFrame(daily_list)

    # 문자열로 온 숫자 컬럼들을 정수(int) 타입으로 변환
    numeric_columns = ["rank", "audiCnt", "audiAcc", "scrnCnt"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 6. 1위 영화 지표 카드 3장
    top_movie = df.iloc[0]
    st.subheader(f"🏆 1위: {top_movie['movieNm']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("어제 관객수", f"{top_movie['audiCnt']:,} 명")
    col2.metric("누적 관객수", f"{top_movie['audiAcc']:,} 명")
    col3.metric("스크린수", f"{top_movie['scrnCnt']:,} 개")

    st.divider()

    # 7. 관객수 상위 5편 막대그래프
    st.subheader("📊 관객수 상위 5개 영화")
    top5_df = df.head(5)[["movieNm", "audiCnt"]].set_index("movieNm")
    st.bar_chart(top5_df)

    st.divider()

    # 8. 전체 순위 표 출력
    st.subheader("📋 전체 박스오피스 순위")

    # 출력용 데이터프레임 정리 및 컬럼명 변경
    display_df = df[
        ["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]
    ].copy()
    display_df.columns = [
        "순위",
        "영화명",
        "개봉일",
        "관객수",
        "누적관객",
        "스크린수",
    ]

    # 천 단위 쉼표 포맷을 적용하여 테이블 출력
    st.dataframe(
        display_df.style.format(
            {"관객수": "{:,}", "누적관객": "{:,}", "스크린수": "{:,}"}
        ),
        use_container_width=True,
        hide_index=True,
    )
