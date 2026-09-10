import pandas as pd
import plotly.graph_objects as go

# 1. 날짜 전처리 및 속성 추출
df['date'] = pd.to_datetime(df['date'])
df['year_month'] = df['date'].dt.strftime('%Y-%m')
df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')

# 요일 추출 및 순서 지정 (월요일 ~ 일요일)
day_map = {0: '월', 1: '화', 2: '수', 3: '목', 4: '금', 5: '토', 6: '일'}
df['day_name'] = df['date'].dt.dayofweek.map(day_map)
day_order = ['월', '화', '수', '목', '금', '토', '일']
df['day_name'] = pd.Categorical(
    df['day_name'], categories=day_order, ordered=True
)

# 2. 피벗 테이블 생성 (관객수 합계 & 호버용 날짜 문자열)
pivot_audience = df.pivot_table(
    index='day_name',
    columns='year_month',
    values='audience',
    aggfunc='sum',
    observed=False,
)

pivot_dates = df.pivot_table(
    index='day_name',
    columns='year_month',
    values='date_str',
    aggfunc=lambda x: '<br>'.join(x),
    observed=False,
)

# 3. 캘린더 히트맵 생성
fig = go.Figure(
    data=go.Heatmap(
        z=pivot_audience.values,
        x=pivot_audience.columns,
        y=pivot_audience.index,
        text=pivot_dates.values,
        colorscale='YlGnBu',  # 관객수가 많을수록 진한 색상
        hovertemplate='<b>월/요일:</b> %{x} (%{y}요일)<br><b>총 관객수:</b> %{z:,.0f}명<br><b>해당 날짜:</b><br>%{text}<extra></extra>',
    )
)

fig.update_layout(
    title='월×요일별 관객 합계 히트맵',
    xaxis_title='월 (YYYY-MM)',
    yaxis_title='요일',
    yaxis=dict(autorange='reversed'),  # 월요일이 맨 위에 오도록 정렬
    template='plotly_white',
)

fig.show()
