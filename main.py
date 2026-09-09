import datetime
import pandas as pd
import requests
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 제목 표시
# ==========================================
st.set_page_config(
    page_title="어제의 박스오피스",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 어제의 박스오피스")

# ==========================================
# 2. 한국 시간(KST) 기준 어제 날짜 계산
# ==========================================
# 서버 시계 타임존에 상관없이 한국 시간(UTC+9)으로 정확하게 계산합니다.
kst_timezone = datetime.timezone(datetime.timedelta(hours=9))
now_kst = datetime.datetime.now(tz=kst_timezone)  # tz 매개변수로 타임존 지정
yesterday_kst = now_kst - datetime.timedelta(days=1)

# API 요청용 날짜 형식 (YYYYMMDD)
target_dt = yesterday_kst.strftime("%Y%m%d")
# 화면 표시용 날짜 형식 (YYYY년 MM월 DD일)
display_date = yesterday_kst.strftime("%Y년 %m월 %d일")

st.caption(f"기준 일자: **{display_date}** (한국 시간 기준 자동 계산)")


# ==========================================
# 3. KOBIS API 데이터 불러오기 함수 (캐싱 적용)
# ==========================================
# st.cache_data를 써서 동일한 날짜 요청 시 1시간(3600초) 동안 API를 재호출하지 않고 저장된 데이터를 씁니다.
@st.cache_data(ttl=3600)
def fetch_box_office_data(api_key: str, date_str: str):
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        "key": api_key,
        "targetDt": date_str
    }
    # 10초 내에 응답이 없으면 타임아웃 오류 발생
    response = requests.get(url, params=params, timeout=10)
    return response.json()


# ==========================================
# 4. 시크릿 키 확인 및 API 데이터 호출
# ==========================================
# Streamlit Secrets(비밀 금고)에 KOBIS_KEY가 등록되어 있는지 검사합니다.
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
# 5-1. API 키 오류 또는 서비스 예외(faultInfo) 처리
if "faultInfo" in data:
    st.error("❌ KOBIS API 오류가 발생했습니다. (인증키 문제 가능성)")
    st.warning(f"오류 메시지: {data['faultInfo'].get('message', '알 수 없는 오류')}")
    st.info("💡 `secrets.toml` 또는 Streamlit Cloud Secrets에 입력한 인증키가 올바른지 확인해 주세요.")
    st.stop()

# 5-2. 응답 결과 구조 확인
box_office_result = data.get("boxOfficeResult", {})
daily_list = box_office_result.get("dailyBoxOfficeList", [])

# 5-3. 영화 목록 데이터가 비어 있는 경우 처리
if not daily_list:
    st.warning("⚠️ 어제 날짜의 박스오피스 데이터가 비어 있거나 아직 집계되지 않았습니다.")
    st.info("💡 잠시 후 다시 시도하시거나 KOBIS 공식 홈페이지의 집계 상태를 확인해 주세요.")
    st.stop()


# ==========================================
# 6. 데이터 전처리 (문자열 -> 숫자 변환)
# ==========================================
df = pd.DataFrame(daily_list)

# KOBIS API에서 텍스트로 넘어온 숫자 데이터를 정수(int) 타입으로 변환
numeric_columns = ["rank", "audiCnt", "audiAcc", "scrnCnt"]
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

# 순위 기준으로 오름차순 정렬
df = df.sort_values(by="rank", ascending=True)


# ==========================================
# 7. 화면 구성: 1위 영화 주요 지표 카드
# ==========================================
top_1 = df.iloc[0]

st.subheader(f"🥇 1위: {top_1['movieNm']}")

# 3개의 지표 카드를 옆으로 배치
col1, col2, col3 = st.columns(3)
col1.metric("일일 관객수", f"{top_1['audiCnt']:,} 명")
col2.metric("누적 관객수", f"{top_1['audiAcc']:,} 명")
col3.metric("스크린수", f"{top_1['scrnCnt']:,} 개")

st.divider()


# ==========================================
# 8. 화면 구성: 관객수 상위 5편 막대그래프
# ==========================================
st.subheader("📊 일일 관객수 TOP 5")

# 상위 5개 데이터 추출
top_5_df = df.head(5)

# 차트에 사용하기 쉽도록 영화명을 인덱스로 설정
chart_data = top_5_df.set_index("movieNm")[["audiCnt"]]
chart_data.columns = ["일일 관객수"]

st.bar_chart(chart_data)

st.divider()


# ==========================================
# 9. 화면 구성: 전체 순위 표
# ==========================================
st.subheader("📋 박스오피스 전체 순위")

# 요청된 컬럼만 추출 및 한글 컬럼명 변경
display_df = df[["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]].copy()
display_df.columns = ["순위", "영화명", "개봉일", "관객수", "누적관객", "스크린수"]

# 숫자 표기 시 천 단위 쉼표 추가를 위한 포맷팅
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
