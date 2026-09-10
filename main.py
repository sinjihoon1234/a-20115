import streamlit as st
import pandas as pd
import plotly.express as px

# 앱 웹페이지 제목 및 레이아웃 설정
st.set_page_config(page_title="영화 박스오피스 분석", layout="wide")

st.title("🎬 영화 박스오피스 데이터 분석 앱")

# [1. 데이터 불러오기 및 캐싱]
# @st.cache_data를 사용해 앱이 실행될 때 매번 데이터를 다시 불러오지 않고 저장해둔 데이터를 재사용합니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    data = pd.read_csv(url)
    
    # [2. 날짜 및 데이터 전처리]
    # 결측치(빈 값)가 포함된 행을 삭제합니다.
    data = data.dropna()
    
    # '기준일자' 컬럼을 문자열에서 날짜(datetime) 형식으로 변환합니다.
    data['기준일자'] = pd.to_datetime(data['기준일자'])
    
    # 전체 데이터를 기준일자 오름차순으로 정렬합니다.
    data = data.sort_values('기준일자')
    
    return data

# 전처리 완료된 데이터 로드
df = load_data()

# [3. 영화 선택 기능]
# 영화별 최대 누적관객수를 구해 내림차순 정렬한 뒤 영화명 목록을 추출합니다.
sorted_movies = (
    df.groupby('영화명')['누적관객수']
    .max()
    .sort_values(ascending=False)
    .index
    .tolist()
)

# 사이드바에 영화 선택 드롭다운 메뉴 추가
st.sidebar.header("🔍 조건 선택")
selected_movie = st.sidebar.selectbox("분석할 영화를 선택해 주세요:", sorted_movies)

# 선택한 영화의 데이터만 추출
filtered_df = df[df['영화명'] == selected_movie]

# [5. 레이아웃 구역 나누기]
# 탭(Tab) 구역을 만들어 '일별 관객수'와 '누적 관객수' 분석을 분리합니다.
tab1, tab2 = st.tabs(["📊 일별 관객수 추이", "📈 누적 관객수 추이"])

# 첫 번째 탭: 일별 관객수 (선 그래프)
with tab1:
    st.subheader(f"📊 [{selected_movie}] 일별 관객수 변화")
    
    # [4. Plotly 선 그래프 그리기]
    fig1 = px.line(
        filtered_df,
        x='기준일자',
        y='해당일관객수',
        title=f"'{selected_movie}' 기준일자별 일별 관객수 변화",
        labels={'기준일자': '날짜', '해당일관객수': '관객수(명)'},
        markers=True
    )
    
    # 그래프 표시 (너비에 맞춤)
    st.plotly_chart(fig1, use_container_width=True)
    
    # 그래프 하단 설명 문구
    st.info("💡 **이 그래프로 알 수 있는 것:** 해당 영화의 상영 기간 동안 개봉일 직후 관객수 집중도와 요일별/주차별 관객수 변화 추이를 한눈에 파악할 수 있습니다.")

# 두 번째 탭: 누적 관객수 (영역 차트)
with tab2:
    st.subheader(f"📈 [{selected_movie}] 누적 관객수 변화")
    
    # [두 번째 그래프: Plotly 영역 차트 그리기]
    fig2 = px.area(
        filtered_df,
        x='기준일자',
        y='누적관객수',
        title=f"'{selected_movie}' 기준일자별 누적 관객수 변화",
        labels={'기준일자': '날짜', '누적관객수': '누적 관객수(명)'}
    )
    
    # 그래프 표시 (너비에 맞춤)
    st.plotly_chart(fig2, use_container_width=True)
    
    # 그래프 하단 설명 문구
    st.info("💡 **이 그래프로 알 수 있는 것:** 영화 상영 기간에 따른 누적 관객수의 지속적인 증가 기울기 및 주요 흥행 진폭이 둔화되는 시점을 쉽게 파악할 수 있습니다.")
