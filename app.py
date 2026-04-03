import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Настройка страницы
st.set_page_config(page_title="CityPulse AI - Almaty", layout="wide")

# --- 1. ЛОГИКА ВРЕМЕНИ (КАК В 2ГИС) ---
now = datetime.now()
current_hour = now.hour

# Определяем состояние города
if 8 <= current_hour <= 10:
    time_factor, mode_name = 1.7, "🌅 Утренний час пик"
elif 17 <= current_hour <= 19:
    time_factor, mode_name = 1.9, "🌆 Вечерний час пик"
elif 20 <= current_hour <= 23:
    time_factor, mode_name = 0.6, "🌙 Вечерний спад (Дороги разгружаются)"
elif 0 <= current_hour <= 6:
    time_factor, mode_name = 0.2, "🌑 Ночной режим (Свободно)"
else:
    time_factor, mode_name = 1.0, "☀️ Дневной стандарт"

# --- 2. БАЗА ДАННЫХ РАЙОНОВ ---
districts_db = {
    "Медеуский": {"lat": 43.245, "lon": 76.955, "routes": ["12", "28", "60"], "base_traffic": 5.0, "lights": [[43.242, 76.958]], "problem": "Пр. Достык / Аль-Фараби"},
    "Бостандыкский": {"lat": 43.215, "lon": 76.915, "routes": ["38", "63", "86"], "base_traffic": 5.2, "lights": [[43.210, 76.910]], "problem": "Ул. Тимирязева / Розыбакиева"},
    "Алмалинский": {"lat": 43.250, "lon": 76.925, "routes": ["92", "98", "99"], "base_traffic": 5.5, "lights": [[43.252, 76.928]], "problem": "Ул. Толе би / Сейфуллина"},
    "Ауэзовский": {"lat": 43.225, "lon": 76.855, "routes": ["11", "37", "118"], "base_traffic": 4.8, "lights": [[43.228, 76.850]], "problem": "Пр. Абая / Саина"},
    "Жетысуский": {"lat": 43.290, "lon": 76.935, "routes": ["17", "29", "50"], "base_traffic": 4.2, "lights": [[43.295, 76.930]], "problem": "Район Саяхата / Барахолки"},
    "Турксибский": {"lat": 43.340, "lon": 76.960, "routes": ["2", "48", "74"], "base_traffic": 3.8, "lights": [[43.345, 76.965]], "problem": "Кольцо ВАЗ / Майлина"},
    "Наурызбайский": {"lat": 43.200, "lon": 76.815, "routes": ["15", "44", "22"], "base_traffic": 3.0, "lights": [[43.205, 76.820]], "problem": "Ул. Жандосова / Шаляпина"},
    "Алатауский": {"lat": 43.285, "lon": 76.825, "routes": ["102", "124", "14"], "base_traffic": 3.5, "lights": [[43.280, 76.820]], "problem": "Район Almaty Arena"}
}

# Генерация данных с учетом времени
rows = []
for name, info in districts_db.items():
    # Трафик падает вечером
    traffic = np.clip(info["base_traffic"] * time_factor + np.random.uniform(-0.4, 0.4), 1, 10)
    aqi = np.clip(100 * (traffic / 5) + np.random.randint(-15, 15), 50, 300)
    incidents = int(np.random.poisson(traffic / 4))
    rows.append({"Район": name, "Пробки": traffic, "AQI": aqi, "Инциденты": incidents, "lat": info["lat"], "lon": info["lon"], "lights": info["lights"]})
df = pd.DataFrame(rows)

# --- 3. ИНТЕРФЕЙС ---
st.title("🏙️ CityPulse: Интеллектуальный мониторинг Алматы")
st.subheader(f"🕒 Время: {now.strftime('%H:%M')} | Режим: {mode_name}")

selected_district = st.sidebar.selectbox("🎯 Выберите район:", list(districts_db.keys()))
d_data = df[df["Район"] == selected_district].iloc[0]
d_info = districts_db[selected_district]

# Метрики
m1, m2, m3, m4 = st.columns(4)
m1.metric("Трафик", f"{d_data['Пробки']:.1f} балла")
m2.metric("Воздух", f"{int(d_data['AQI'])} AQI")
m3.metric("Инциденты", f"{d_data['Инциденты']} ДТП")
m4.metric("Светофоры", f"{len(d_info['lights'])} узла")

st.divider()

# --- 4. КАРТА И ПРОГНОЗ ---
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📍 Карта загруженности и светофоров")
    map_pts = pd.DataFrame({'lat': [d_data['lat'] + np.random.uniform(-0.01, 0.01) for _ in range(15)], 'lon': [d_data['lon'] + np.random.uniform(-0.01, 0.01) for _ in range(15)], 'intensity': [d_data['Пробки']] * 15})
    fig_map = px.density_mapbox(map_pts, lat='lat', lon='lon', z='intensity', radius=40, center=dict(lat=d_info['lat'], lon=d_info['lon']), zoom=12, mapbox_style="carto-positron", color_continuous_scale="Reds", range_color=[0, 10])
    # Синие точки светофоров
    fig_map.add_trace(go.Scattermapbox(lat=[l[0] for l in d_info['lights']], lon=[l[1] for l in d_info['lights']], mode='markers', marker=dict(size=15, color='blue'), name="Светофоры"))
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, showlegend=False)
    st.plotly_chart(fig_map, use_container_width=True)

with c2:
    st.subheader("📉 Прогноз на час")
    # Если вечер — прогноз идет ВНИЗ
    trend = -0.6 if current_hour >= 20 else (0.5 if time_factor > 1.5 else 0.1)
    future_vals = [np.clip(d_data['Пробки'] + (i * trend), 0, 10) for i in range(5)]
    future_times = [(now + timedelta(minutes=i*15)).strftime('%H:%M') for i in range(5)]
    st.line_chart(pd.DataFrame({"Баллы": future_vals}, index=future_times))
    
    st.info(f"**Анализ ИИ:** {d_info['problem']}. Рекомендуемые маршруты: {', '.join(d_info['routes'])}")
    if st.button("📢 Оповестить жителей"): st.success("Уведомления отправлены!")

# --- 5. ЧАТ-БОТ С "ЗРЕНИЕМ" ВРЕМЕНИ ---
st.divider()
st.header("💬 AI Аналитик (Режим: Реальное время)")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": f"Добрый вечер! Я вижу, что сейчас {now.strftime('%H:%M')}. Город затихает. Чем помочь?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.write(msg["content"])

if prompt := st.chat_input("Спросите ИИ о ситуации..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)
    
    with st.chat_message("assistant"):
        p = prompt.lower()
        if "почему" in p or "объясни" in p:
            res = f"Потому что сейчас время {mode_name}. В {selected_district}е пробки снизились до {d_data['Пробки']:.1f} баллов. Это естественный спад деловой активности."
        elif "прогноз" in p:
            res = f"По моим данным, через 60 минут трафик упадет еще сильнее, до {future_vals[-1]:.1f} баллов. Оптимизация светофоров уже не требуется."
        else:
            worst = df.loc[df['Пробки'].idxmax()]['Район']
            res = f"На {now.strftime('%H:%M')} ситуация стабильная. Самая высокая нагрузка остается в {worst}, но и там она идет на спад."
        st.write(res)
        st.session_state.messages.append({"role": "assistant", "content": res})

if st.button("🚦 Смарт-управление"): st.balloons()
