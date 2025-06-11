import streamlit as st
import pandas as pd
import datetime as dt
from datetime import timedelta
import pytz

# CSV 불러오기 및 전처리
csv_path = 'timetable3.csv'
df = pd.read_csv(csv_path)
df = df[~df['시간'].str.match(r'^0[0-3]:\d{2}$')]

route_directions = {}
for route in df['노선명'].unique():
    directions = df[df['노선명'] == route]['방면'].unique().tolist()
    route_directions[route] = directions

def get_now_kst():
    return dt.datetime.now(pytz.timezone('Asia/Seoul'))

def combine_datetime(time_obj, now=None):
    if now is None:
        now = dt.datetime.now()

    base_date = now.date()
    combined = dt.datetime.combine(base_date, time_obj)
    if combined <= now:
        combined += timedelta(days=1)

    return combined


def parse_time_str(time_str):
    return dt.datetime.strptime(time_str, '%H:%M').time()

def find_next_bus(route, direction, now_dt):
    times_str = df[(df['노선명'] == route) & (df['방면'] == direction)]['시간'].tolist()
    times = [parse_time_str(t) for t in times_str]
    times.sort()
    for t in times:
        bus_dt = combine_datetime(t, now=now_dt)
        if bus_dt > now_dt:
            return bus_dt
    return None

st.title("버스 알람 서비스")

tab1, tab2 = st.tabs(["현재 시간 기준 버스 찾기", "특정 시간대 버스 알람 설정"])

with tab1:
    st.header("1. 현재 시간 기준 가장 가까운 버스 찾기")
    route = st.selectbox("노선명 선택", sorted(df['노선명'].unique()))
    directions = route_directions.get(route, [])
    direction = st.selectbox("방면 선택", directions)
    if st.button("가까운 버스 찾기"):
        now_dt = get_now_kst()
        next_bus = find_next_bus(route, direction, now_dt)
        if next_bus is None:
            st.warning(f"{route} - {direction} 방향의 남은 버스가 없습니다.")
        else:
            st.success(f"가장 가까운 버스 도착시간: {next_bus.strftime('%Y-%m-%d %H:%M')}")
            alarm = st.radio("알람을 받으시겠습니까?", ("예", "아니요"))
            if alarm == "예":
                alarm_notify_dt = next_bus - timedelta(minutes=10)
                st.info(f"알람이 설정되었습니다. 알람 시간: {alarm_notify_dt.strftime('%Y-%m-%d %H:%M')} (10분 전 알림)")
                # 실제 알람 기능 추가 가능

with tab2:
    st.header("2. 특정 시간대 버스 알람 설정")
    route2 = st.selectbox("노선명 선택", sorted(df['노선명'].unique()), key="route2")
    directions2 = route_directions.get(route2, [])
    direction2 = st.selectbox("방면 선택", directions2, key="direction2")

    times2 = df[(df['노선명'] == route2) & (df['방면'] == direction2)]['시간'].tolist()
    times2_sorted = sorted(times2)
    time2 = st.selectbox("시간 선택", times2_sorted, key="time2")

    minutes_before = st.number_input("몇 분 전", min_value=0, max_value=60, value=10, step=1)

    if st.button("알람 설정"):
        if None in [route2, direction2, time2]:
            st.warning("노선, 방면, 시간을 모두 선택해주세요.")
        else:
            alarm_time = parse_time_str(time2)
            now = dt.datetime.now()
            alarm_dt = combine_datetime(alarm_time, now=now)
            alarm_notify_dt = alarm_dt - timedelta(minutes=minutes_before)
            st.success(f"{route2} - {direction2} 방향 {time2} 버스 알람을 {minutes_before}분 전에 설정했습니다.")
            st.info(f"알람 시간: {alarm_notify_dt.strftime('%Y-%m-%d %H:%M')}")


