import streamlit as st
import pandas as pd
import plotly.express as px

# 앱 웹페이지 제목 및 레이아웃 설정
st.set_page_config(page_title="영화 박스오피스 분석", layout="wide")

st.title("🎬 영화 박스오피스 데이터 분석 앱")

# [1. 데이터 불러오기 및 캐싱]
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    data = pd.read_csv(url)
    
    # [2. 날짜 및 데이터 전처리]
    data = data.dropna()
    data['기준일자'] = pd.to_datetime(data['기준일자'])
    data = data.sort_values('기준일자')
    
    return data

# 전처리 완료된 데이터 로드
df = load_data()

# [3. 영화 선택 기능]
sorted_movies = (
    df.groupby('영화명')['누적관객수']
    .max()
    .sort_values(ascending=False)
    .index
    .tolist()
)

# 사이드바 선택 메뉴
st.sidebar.header("🔍 개별 영화 조건 선택")
selected_movie = st.sidebar.selectbox("분석할 영화를 선택해 주세요:", sorted_movies)

# 선택한 영화 데이터 필터링
filtered_df = df[df['영화명'] == selected_movie]

# [5. 레이아웃 구역 나누기]
tab1, tab2, tab3 = st.tabs([
    "📊 개별 영화 일별 관객수", 
    "📈 개별 영화 누적 관객수", 
    "🏆 Top 5 영화 누적 관객수 비교"
])

# 첫 번째 탭: 개별 영화 일별 관객수
with tab1:
    st.subheader(f"📊 [{selected_movie}] 일별 관객수 변화")
    
    fig1 = px.line(
        filtered_df,
        x='기준일자',
        y='해당일관객수',
        title=f"'{selected_movie}' 기준일자별 일별 관객수 변화",
        labels={'기준일자': '날짜', '해당일관객수': '관객수(명)'},
        markers=True
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    st.info("💡 **이 그래프로 알 수 있는 것:** 해당 영화의 상영 기간 동안 개봉일 직후 관객수 집중도와 요일별/주차별 관객수 변화 추이를 한눈에 파악할 수 있습니다.")

# 두 번째 탭: 개별 영화 누적 관객수
with tab2:
    st.subheader(f"📈 [{selected_movie}] 누적 관객수 변화")
    
    fig2 = px.area(
        filtered_df,
        x='기준일자',
        y='누적관객수',
        title=f"'{selected_movie}' 기준일자별 누적 관객수 변화",
        labels={'기준일자': '날짜', '누적관객수': '누적 관객수(명)'}
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    st.info("💡 **이 그래프로 알 수 있는 것:** 영화 상영 기간에 따른 누적 관객수의 지속적인 증가 기울기 및 주요 흥행 진폭이 둔화되는 시점을 쉽게 파악할 수 있습니다.")

# 세 번째 탭: 조건을 만족하는 Top 5 영화 누적 관객수 비교
with tab3:
    st.subheader("🏆 장기 흥행(20일 이상) Top 5 영화 누적 관객수 추이 비교")
    
    # 1. 각 영화별 TOP 10 차트 등장 일수(데이터 행 수) 계산
    movie_counts = df['영화명'].value_counts()
    
    # 2. 20일 이상 등장한 영화의 목록 추출
    movies_over_20days = movie_counts[movie_counts >= 20].index
    
    # 3. 20일 이상 등장 영화 중 누적관객수 상위 5개 영화 필터링
    top5_movies = (
        df[df['영화명'].isin(movies_over_20days)]
        .groupby('영화명')['누적관객수']
        .max()
        .sort_values(ascending=False)
        .head(5)
        .index
        .tolist()
    )
    
    # 4. 상위 5개 영화 데이터 추출
    top5_df = df[df['영화명'].isin(top5_movies)]
    
    # 5. 다중 선 그래프 그리기
    fig3 = px.line(
        top5_df,
        x='기준일자',
        y='누적관객수',
        color='영화명',
        title="20일 이상 상위 차트에 유지된 Top 5 영화의 누적 관객수 추이",
        labels={'기준일자': '날짜', '누적관객수': '누적 관객수(명)', '영화명': '영화 제목'}
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    st.info("💡 **이 그래프로 알 수 있는 것:** 반짝 흥행에 그치지 않고 최소 20일 이상 박스오피스 상위권을 유지한 대표 장기 흥행작들의 누적 관객수 모객 속도와 최종 흥행 스케일을 비교할 수 있습니다.")
