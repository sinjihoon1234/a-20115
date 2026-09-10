import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 개별 영화 일별 관객수", 
    "📈 개별 영화 누적 관객수", 
    "🏆 Top 5 영화 누적 관객수 비교",
    "📉 전체 시장 관객수 추이 (7일 이동평균)"
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
    
    movie_counts = df['영화명'].value_counts()
    movies_over_20days = movie_counts[movie_counts >= 20].index
    
    top5_movies = (
        df[df['영화명'].isin(movies_over_20days)]
        .groupby('영화명')['누적관객수']
        .max()
        .sort_values(ascending=False)
        .head(5)
        .index
        .tolist()
    )
    
    top5_df = df[df['영화명'].isin(top5_movies)]
    
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

# 네 번째 탭: 전체 영화 시장 관객수 합계 및 7일 이동평균
with tab4:
    st.subheader("📉 전체 박스오피스 관객수 추이 및 7일 이동평균")
    
    # 1. 기준일자별 전체 TOP 10 영화 관객수 합계 산출
    daily_total = df.groupby('기준일자')['해당일관객수'].sum().reset_index()
    
    # 2. 7일 이동평균(Rolling Mean) 계산
    daily_total['7일이동평균'] = daily_total['해당일관객수'].rolling(window=7).mean()
    
    # 3. Plotly Graph Objects로 그래프 생성
    fig4 = go.Figure()
    
    # 원본 일별 총 관객수 (연한 회색, 얇은 선)
    fig4.add_trace(go.Scatter(
        x=daily_total['기준일자'],
        y=daily_total['해당일관객수'],
        mode='lines',
        name='일별 총 관객수',
        line=dict(color='lightgray', width=1.5)
    ))
    
    # 7일 이동평균선 (진한 파란색, 두꺼운 선)
    fig4.add_trace(go.Scatter(
        x=daily_total['기준일자'],
        y=daily_total['7일이동평균'],
        mode='lines',
        name='7일 이동평균',
        line=dict(color='#1f77b4', width=3)
    ))
    
    # 그래프 레이아웃 설정
    fig4.update_layout(
        title="전체 영화 기준일자별 관객수 합계 및 7일 이동평균 추이",
        xaxis_title="날짜",
        yaxis_title="총 관객수(명)",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig4, use_container_width=True)
    st.info("💡 **이 그래프로 알 수 있는 것:** 주말과 평일 간의 극심한 일별 관객수 변동(노이즈)을 평탄화하여, 전체 극장가 박스오피스 시장의 성수기/비수기 등 장기적인 관객 유입 흐름을 명확하게 파악할 수 있습니다.")
