import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

# 타이틀
st.title("🎬 영화 데이터 그래프 - 분포와 관계")
st.caption("1년간 박스오피스 Top 10에 든 개봉 영화 216편의 데이터 시각화")

# 1. 데이터 불러오기 및 전처리
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    # 장르 전처리: 세로막대(|)로 구분된 경우 첫 번째 장르만 사용
    df['genre_clean'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0] if pd.notna(x) else x)
    return df

df = load_data()

# 데이터 미리보기 (선택사항)
with st.expander("📊 원본 데이터 확인하기"):
    st.dataframe(df, use_container_width=True)

st.divider()

# ==========================================
# 그래프 1: 장르별 영화 편수 (플롯리 도넛 그래프)
# ==========================================
st.subheader("1. 장르별 영화 편수 분포")

# 장르별 편수 집계
genre_counts = df['genre_clean'].value_counts().reset_index()
genre_counts.columns = ['장르', '편수']

# 도넛 그래프 생성
fig1 = px.pie(
    genre_counts,
    names='장르',
    values='편수',
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Pastel
)

# 마우스 오버 시 편수와 비율이 보이도록 툴팁 설정
fig1.update_traces(
    textposition='inside',
    textinfo='label+percent',
    hovertemplate='<b>장르: %{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>'
)

fig1.update_layout(
    margin=dict(t=30, b=30, l=10, r=10),
    legend_title_text='장르 목록'
)

st.plotly_chart(fig1, use_container_width=True)

# 그래프 설명 구역
st.info("💡 **이 그래프로 알 수 있는 것:** 1년간 상위권 박스오피스에 진입한 영화 중 드라마와 액션, 코미디 등 특정 장르가 차지하는 비중과 편수 분포를 직관적으로 파악할 수 있습니다.")

st.divider()

# ==========================================
# 그래프 2: 개봉일 스크린수 vs 총 관객수 (관계 분석)
# ==========================================
st.subheader("2. 개봉일 스크린 수와 총 관객 수의 관계")

fig2 = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    color='genre_clean',
    hover_name='movieNm',
    hover_data={'first_scrn': ':,', 'total_audi': ':,', 'days_in_top10': True},
    labels={
        'first_scrn': '개봉일 스크린 수 (개)',
        'total_audi': '총 관객 수 (명)',
        'genre_clean': '장르'
    }
)

fig2.update_traces(marker=dict(size=10, opacity=0.7))
fig2.update_layout(margin=dict(t=30, b=30, l=10, r=10))

st.plotly_chart(fig2, use_container_width=True)

# 그래프 설명 구역
st.info("💡 **이 그래프로 알 수 있는 것:** 초기 배급력(개봉일 스크린 수)이 흥행 성공(총 관객 수)과 강력한 양의 상관관계를 가짐을 확인할 수 있습니다.")

st.divider()

# ==========================================
# 그래프 3: 10위권 유지 일수 vs 총 관객수 (관계 분석)
# ==========================================
st.subheader("3. 10위권 유지 일수(상위권 유지 기간)와 총 관객 수의 관계")

fig3 = px.scatter(
    df,
    x='days_in_top10',
    y='total_audi',
    size='first_week_audi',
    color='genre_clean',
    hover_name='movieNm',
    hover_data={'days_in_top10': True, 'total_audi': ':,', 'first_week_audi': ':,'},
    labels={
        'days_in_top10': '10위권에 머문 날수 (일)',
        'total_audi': '총 관객 수 (명)',
        'first_week_audi': '개봉 첫 주 관객 수',
        'genre_clean': '장르'
    }
)

fig3.update_layout(margin=dict(t=30, b=30, l=10, r=10))

st.plotly_chart(fig3, use_container_width=True)

# 그래프 설명 구역
st.info("💡 **이 그래프로 알 수 있는 것:** 박스오피스 상위권(10위권)에 오랫동안 잔류한 영화일수록 누적 관객 수가 극대화되는 롱런 흥행 양상을 파악할 수 있습니다.")
