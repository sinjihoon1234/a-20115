import datetime
import pandas as pd
import requests
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 제목 표시
# ==========================================
st.set_page_config(
    page_title="일별 박스오피스 조회",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 일별 박스오피스 조회")

# ==========================================
# 2. 한국 시간(KST) 기준 날짜 설정 및 달력 위젯
# ==========================================
# 배포 서버의 시계와 상관없이 한국 시간(UTC+9)으로 현재/어제 날짜를 정확히 계산합니다.
kst_timezone = datetime.timezone(datetime.timedelta(hours=9))
now_kst = datetime.datetime.now(tz=kst_timezone)
yesterday_kst = (now_kst - datetime.timedelta(days=1)).date()

# 달력(st.date_input)으로 날짜를 고를 수 있게 합니다.
# 오늘 건 집계 전이므로 선택 가능한 최대 날짜(max_value)는 '어제'로 제한합니다.
selected_date = st.date_input(
    label="조회할 날짜를 선택하세요 (어제 날짜까지 선택 가능):",
    value=yesterday_kst,
    max_value=yesterday_kst,
    min_value=datetime.date(2004, 1, 1)  # KOBIS 데이터 시작 시점 근처
)

# API 요청용 날짜 문자열 (YYYYMMDD)
target_dt = selected_date.strftime("%Y%m%d")
# 화면 표시용 날짜 문자열 (YYYY년 MM월 DD일)
display_date = selected_date.strftime("%Y년 %m월 %d일")


# ==========================================
# 3. KOBIS API 데이터 불러오기 함수 (캐싱 적용)
# ==========================================
# st.cache_data(ttl=3600): 같은 날짜로 요청하면 1시간(3600초) 동안 API를 재호출하지 않고 저장된 데이터를 활용합니다.
@st.cache_data(ttl=3600)
def fetch_box_office_data(api_key: str, date_str: str):
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        "key": api_key,
        "targetDt": date_str
    }
    response = requests.get(url, params=params, timeout=10)
    return response.json()


# ==========================================
# 4. 시크릿 키 확인 및 API 데이터 호출
# ==========================================
if "KOBIS_KEY" not in st.secrets or not st.secrets["KOBIS_KEY"]:
    st.error("❌ 비밀 금고(st.secrets)에 `KOBIS_KEY`가 설정되지 않았습니다.")
    st.info(
        "💡 **확인 방법**\n"
        "1. 로컬 개발 환경: `.streamlit/secrets.toml` 파일에 `KOBIS_KEY = '발급받은키'`를 작성하세요.\n"
        "2. Streamlit Cloud: 앱 설정의 **Secrets** 메뉴에서 `KOBIS_KEY` 항목을 추가해 주세요."
    )
    st.stop()

api_key = st.secrets["KOBIS_KEY"]

try:
    data = fetch_box_office_data(api_key, target_dt)
except Exception as e:
    st.error("❌ KOBIS 서버와 통신하는 중 네트워크 오류가 발생했습니다.")
    st.caption(f"오류 상세 내용: {e}")
    st.stop()


# ==========================================
# 5. API 응답 데이터 검증 및 오류 처리
# ==========================================
# 5-1. 인증키 오류 등 faultInfo 예외 응답 처리
if "faultInfo" in data:
    st.error("❌ KOBIS API 오류가 발생했습니다. (인증키 문제 가능성)")
    st.warning(f"오류 메시지: {data['faultInfo'].get('message', '알 수 없는 오류')}")
    st.info("💡 `secrets.toml` 또는 Streamlit Cloud Secrets에 입력한 인증키가 올바른지 확인해 주세요.")
    st.stop()

# 5-2. 응답 결과 목록 가져오기
box_office_result = data.get("boxOfficeResult", {})
daily_list = box_office_result.get("dailyBoxOfficeList", [])

# 5-3. 고른 날짜의 영화 목록이 비어 있는 경우 처리
if not daily_list:
    st.warning("그날은 아직 집계 전입니다")
    st.stop()


# ==========================================
# 6. 데이터 전처리 (숫자 변환, 순위변동, 트로피 표시)
# ==========================================
df = pd.DataFrame(daily_list)

# API에서 텍스트로 넘어온 숫자 데이터를 정수(int) 타입으로 변환
numeric_columns = ["rank", "rankInten", "audiCnt", "audiAcc", "scrnCnt"]
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

# 순위 기준 오름차순 정렬
df = df.sort_values(by="rank", ascending=True)

# 6-1. 순위 증감(rankInten)에 따라 화살표 붙이기
def format_rank_change(val):
    if val > 0:
        return f"🔺 +{val}"  # 순위 상승 (빨간 위 화살표)
    elif val < 0:
        return f"🔵 {val}"   # 순위 하락 (파란 아래 표시)
    else:
        return "-"           # 변동 없음

df["순위변동"] = df["rankInten"].apply(format_rank_change)

# 6-2. 누적관객이 100만 명 이상(>= 1,000,000)인 경우 트로피(🏆) 이모지 추가
def format_movie_title(row):
    title = row["movieNm"]
    if row["audiAcc"] >= 1_000_000:
        return f"{title} 🏆"
    return title

df["표시영화명"] = df.apply(format_movie_title, axis=1)


# ==========================================
# 7. 화면 구성: 1위 영화 주요 지표 카드
# ==========================================
top_1 = df.iloc[0]

st.subheader(f"🥇 1위: {top_1['표시영화명']}")

col1, col2, col3 = st.columns(3)
col1.metric("일일 관객수", f"{top_1['audiCnt']:,} 명")
col2.metric("누적 관객수", f"{top_1['audiAcc']:,} 명")
col3.metric("스크린수", f"{top_1['scrnCnt']:,} 개")

st.divider()


# ==========================================
# 8. 화면 구성: 관객수 상위 5편 막대그래프
# ==========================================
st.subheader("📊 일일 관객수 TOP 5")

top_5_df = df.head(5)

# 차트 인덱스를 트로피가 반영된 영화명으로 설정
chart_data = top_5_df.set_index("표시영화명")[["audiCnt"]]
chart_data.columns = ["일일 관객수"]

st.bar_chart(chart_data)

st.divider()


# ==========================================
# 9. 화면 구성: 전체 순위 표
# ==========================================
st.subheader(f"📋 {display_date} 박스오피스 순위")

# 표에 보여줄 컬럼 지정 및 한글명 변경
display_df = df[["rank", "순위변동", "표시영화명", "openDt", "audiCnt", "audiAcc", "scrnCnt"]].copy()
display_df.columns = ["순위", "순위변동", "영화명", "개봉일", "관객수", "누적관객", "스크린수"]

st.dataframe(
    display_df,
    use_container_width=True,
    column_config={
        "관객수": st.column_config.NumberColumn(format="%d명"),
        "누적관객": st.column_config.NumberColumn(format="%d명"),
        "스크린수": st.column_config.NumberColumn(format="%d개"),
    },
    hide_index=True
)
