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
    # 개봉일(openDt) 숫자를 datetime 형식으로 변환
    df['openDt_parsed'] = pd.to_datetime(df['openDt'].astype(str), format='%Y%m%d', errors='coerce')
    
    # 한국 극장가 주요 연휴 및 성수기 시즌 여부 구분 함수
    # - 설 연휴/겨울 대목 (1월 말 ~ 2월 중순)
    # - 가정의 달/어린이날 (5월)
    # - 여름 극장가 최고 성수기 (7월 ~ 8월)
    # - 추석 연휴 (9월 ~ 10월 초)
    # - 연말 / 크리스마스 성수기 (12월)
    def is_holiday_season(dt):
        if pd.isna(dt):
            return "평시 개봉"
        month = dt.month
        day = dt.day
        
        # 1월/2월 (설 연휴 시즌)
        if month == 1 and day >= 15:
            return "주요 연휴/성수기 개봉"
        if month == 2 and day <= 20:
            return "주요 연휴/성수기 개봉"
        # 5월 (가정의 달)
        if month == 5:
            return "주요 연휴/성수기 개봉"
        # 7~8월 (여름 대목)
        if month in [7, 8]:
            return "주요 연휴/성수기 개봉"
        # 9월/10월 초 (추석 시즌)
        if month == 9 or (month == 10 and day <= 10):
            return "주요 연휴/성수기 개봉"
        # 12월 (연말/크리스마스)
        if month == 12:
            return "주요 연휴/성수기 개봉"
            
        return "평시 개봉"

    df['season_type'] = df['openDt_parsed'].apply(is_holiday_season)
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

genre_counts = df['genre_clean'].value_counts().reset_index()
genre_counts.columns = ['장르', '편수']

fig1 = px.pie(
    genre_counts,
    names='장르',
    values='편수',
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Pastel
)

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

st.info("💡 **이 그래프로 알 수 있는 것:** 1년간 상위권 박스오피스에 진입한 영화 중 드라마와 액션, 코미디 등 특정 장르가 차지하는 비중과 편수 분포를 직관적으로 파악할 수 있습니다.")

st.divider()

# ==========================================
# 그래프 2: 장르별 영화 관객 수 트리맵
# ==========================================
st.subheader("2. 장르별 영화 관객 수 분포 (트리맵)")

fig2 = px.treemap(
    df,
    path=[px.Constant("전체 영화"), 'genre_clean', 'movieNm'],
    values='total_audi',
    color='genre_clean',
    color_discrete_sequence=px.colors.qualitative.Set3
)

fig2.update_traces(
    hovertemplate='<b>%{label}</b><br>총 관객 수: %{value:,.0f}명<extra></extra>'
)

fig2.update_layout(
    margin=dict(t=30, b=30, l=10, r=10)
)

st.plotly_chart(fig2, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 각 장르가 전체 관객 수에서 차지하는 비중과 장르 내에서 어떤 영화가 흥행을 주도했는지 한눈에 비교할 수 있습니다.")

st.divider()

# ==========================================
# 그래프 3: 총 관객 수 히스토그램
# ==========================================
st.subheader("3. 총 관객 수 분포 (히스토그램)")

fig3 = px.histogram(
    df,
    x='total_audi',
    nbins=30,
    labels={'total_audi': '총 관객 수 (명)', 'count': '영화 수'},
    color_discrete_sequence=['#4C78A8']
)

fig3.update_traces(
    hovertemplate='<b>관객 수 구간: %{x:,.0f}명</b><br>영화 수: %{y}편<extra></extra>'
)

fig3.update_layout(
    yaxis_title="영화 수 (편)",
    margin=dict(t=30, b=30, l=10, r=10)
)

st.plotly_chart(fig3, use_container_width=True)

max_movie = df.loc[df['total_audi'].idxmax()]
max_movie_name = max_movie['movieNm']
max_movie_audi = max_movie['total_audi']

q25 = df['total_audi'].quantile(0.25)
q75 = df['total_audi'].quantile(0.75)

st.info(
    f"💡 **이 그래프로 알 수 있는 것:** 대부분의 영화는 관객 수 **{q25:,.0f}명 ~ {q75:,.0f}명** (약 300만 명 이하) 구간에 높게 몰려 있는 오른쪽 꼬리가 긴 분포를 보입니다. "
    f"가장 관객 수가 많은 영화는 **'{max_movie_name}'**(총 **{max_movie_audi:,.0f}명**)입니다."
)

st.divider()

# ==========================================
# 그래프 4: 개봉일 스크린수 vs 총 관객수 (산점도)
# ==========================================
st.subheader("4. 개봉일 스크린 수와 총 관객 수의 관계")

fig4 = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    color='genre_clean',
    hover_name='movieNm',
    labels={
        'first_scrn': '개봉일 스크린 수 (개)',
        'total_audi': '총 관객 수 (명)',
        'genre_clean': '장르'
    }
)

fig4.update_traces(
    marker=dict(size=9, opacity=0.8),
    hovertemplate='<b>%{hovertext}</b><br>개봉일 스크린 수: %{x:,.0f}개<br>총 관객 수: %{y:,.0f}명<extra></extra>'
)

fig4.update_layout(
    margin=dict(t=30, b=30, l=10, r=10),
    legend_title_text='장르'
)

st.plotly_chart(fig4, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 개봉일 스크린 수가 많은 영화일수록 총 관객 수가 높아지는 대체적인 양의 관계를 보이며, 장르별 선호도 및 흥행 분포의 차이를 점의 색상을 통해 확인할 수 있습니다.")

st.divider()

# ==========================================
# 그래프 5: 주요 장르별 총 관객 수 박스플롯
# ==========================================
st.subheader("5. 주요 장르별(10편 이상) 총 관객 수 분포 (박스플롯)")

genre_counts_series = df['genre_clean'].value_counts()
target_genres = genre_counts_series[genre_counts_series >= 10].index
df_filtered = df[df['genre_clean'].isin(target_genres)]

fig5 = px.box(
    df_filtered,
    x='genre_clean',
    y='total_audi',
    color='genre_clean',
    points='outliers',
    hover_name='movieNm',
    labels={
        'genre_clean': '장르',
        'total_audi': '총 관객 수 (명)'
    }
)

fig5.update_traces(
    hovertemplate='<b>%{hovertext}</b><br>총 관객 수: %{y:,.0f}명<extra></extra>'
)

fig5.update_layout(
    showlegend=False,
    margin=dict(t=30, b=30, l=10, r=10)
)

st.plotly_chart(fig5, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 주요 장르 간 중앙값과 관객 수 편차를 비교할 수 있으며, 박스 상단 밖으로 길게 튀어나온 이상치 점들을 통해 장르 내 초대형 대박 흥행작(outlier)을 명확히 식별할 수 있습니다.")

st.divider()

# ==========================================
# 그래프 6: 개봉일 스크린수 vs 총 관객수 버블 차트
# ==========================================
st.subheader("6. 개봉일 스크린 수, 총 관객 수, 개봉 첫 주 관객 수의 관계 (버블 차트)")

fig6 = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    size='first_week_audi',
    color='genre_clean',
    hover_name='movieNm',
    hover_data={'first_week_audi': ':,'},
    size_max=40,
    labels={
        'first_scrn': '개봉일 스크린 수 (개)',
        'total_audi': '총 관객 수 (명)',
        'first_week_audi': '개봉 첫 주 관객 수',
        'genre_clean': '장르'
    }
)

fig6.update_traces(
    hovertemplate='<b>%{hovertext}</b><br>개봉일 스크린 수: %{x:,.0f}개<br>총 관객 수: %{y:,.0f}명<br>첫 주 관객 수: %{customdata[0]:,.0f}명<extra></extra>'
)

fig6.update_layout(
    margin=dict(t=30, b=30, l=10, r=10),
    legend_title_text='장르'
)

st.plotly_chart(fig6, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 개봉일 스크린 수(X축)와 총 관객 수(Y축)에 더해, 버블 크기를 통해 '개봉 첫 주 관객 수'의 영향력을 3차원적으로 비교할 수 있습니다. 초기 스크린 수 대비 첫 주 반응이 폭발적이었던 영화들을 한눈에 식별할 수 있습니다.")

st.divider()

# ==========================================
# 그래프 7: 제작 국가 -> 장르 선버스트 차트
# ==========================================
st.subheader("7. 제작 국가별 주요 장르 구성 (선버스트)")

fig7 = px.sunburst(
    df,
    path=['nation', 'genre_clean'],
    color='nation',
    color_discrete_sequence=px.colors.qualitative.Pastel1
)

fig7.update_traces(
    hovertemplate='<b>%{label}</b><br>영화 편수: %{value}편<br>비율: %{percentParent:.1%}<extra></extra>'
)

fig7.update_layout(
    margin=dict(t=30, b=30, l=10, r=10)
)

st.plotly_chart(fig7, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 제작 국가별 박스오피스 진출 영화 편수의 비중과, 각 국가 내에서 어떤 장르의 영화가 주를 이루고 있는지 계층 구조로 파악할 수 있습니다.")

st.divider()

# ==========================================
# 그래프 8: 개봉일과 총 관객수 상관관계 산점도 (연휴/성수기 구분 색상)
# ==========================================
st.subheader("8. 개봉일과 총 관객수 사이에는 상관관계가 있을까?")

# 주요 연휴/성수기 개봉작은 붉은색계열(#E63946), 평시 개봉작은 회색/푸른색계열(#A8DADC)로 통일
color_map = {
    "주요 연휴/성수기 개봉": "#E63946",
    "평시 개봉": "#A8DADC"
}

fig8 = px.scatter(
    df,
    x='openDt_parsed',
    y='total_audi',
    color='season_type',
    color_discrete_map=color_map,
    hover_name='movieNm',
    title="개봉일과 총 관객수 사이에는 상관관계가 있을까?",
    labels={
        'openDt_parsed': '개봉일',
        'total_audi': '총 관객 수 (명)',
        'season_type': '개봉 시기 구분'
    }
)

fig8.update_traces(
    marker=dict(size=10, opacity=0.85),
    hovertemplate='<b>%{hovertext}</b><br>개봉일: %{x|%Y-%m-%d}<br>총 관객 수: %{y:,.0f}명<extra></extra>'
)

fig8.update_layout(
    title_font_size=18,
    xaxis=dict(tickformat="%Y-%m-%d"),
    margin=dict(t=50, b=30, l=10, r=10),
    legend_title_text='개봉 시기'
)

st.plotly_chart(fig8, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 붉은색으로 강조된 주요 연휴 및 성수기(설/추석 연휴, 5월, 7~8월 여름, 12월 연말) 개봉작들이 평시 개봉작(푸른색) 대비 상단(높은 총 관객 수)에 분포하는 경향이 뚜렷함을 비교할 수 있습니다.")

st.divider()

# ==========================================
# 그래프 9: 10위권 유지 일수 vs 총 관객수
# ==========================================
st.subheader("9. 10위권 유지 일수(상위권 유지 기간)와 총 관객 수의 관계")

fig9 = px.scatter(
    df,
    x='days_in_top10',
    y='total_audi',
    size='first_week_audi',
    color='genre_clean',
    hover_name='movieNm',
    labels={
        'days_in_top10': '10위권에 머문 날수 (일)',
        'total_audi': '총 관객 수 (명)',
        'first_week_audi': '개봉 첫 주 관객 수',
        'genre_clean': '장르'
    }
)

fig9.update_layout(margin=dict(t=30, b=30, l=10, r=10))

st.plotly_chart(fig9, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 박스오피스 상위권(10위권)에 오랫동안 잔류한 영화일수록 누적 관객 수가 극대화되는 롱런 흥행 양상을 파악할 수 있습니다.")
