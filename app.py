import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Настройка страницы
st.set_page_config(page_title="CityPulse AI - Almaty", layout="wide")

# --- 1. ЛОГИКА ВРЕМЕНИ (ЧАС ПИК) ---
current_hour = datetime.now().hour

# Коэффициент трафика: пик утром (8-9) и вечером (17-19)
if 8 <= current_hour <= 10 or 17 <= current_hour <= 20:
    time_factor = 1.8  # Час пик
elif 22 <= current_hour or current_hour <= 6:
    time_factor = 0.3  # Ночь
else:
    time_factor = 1.0  # Обычное время

# --- 2. БАЗА ДАННЫХ ПО РАЙОНАМ ---
districts_db = {
    "Медеуский": {"lat": 43.245, "lon": 76.955, "routes": ["12", "28", "60"], "base_traffic": 5.0, "traffic_lights": [[43.242, 76.958], [43.248, 76.950]]},
    "Бостандыкский": {"lat": 43.215, "lon": 76.915, "routes": ["38", "63", "127"], "base_traffic": 5.2, "traffic_lights": [[43.210, 76.910], [43.220, 76.920]]},
    "Алмалинский": {"lat": 43.250, "lon": 76.925, "routes": ["92", "98", "79"], "base_traffic": 5.5, "traffic_lights": [[43.252, 76.928], [43.248, 76.922]]},
    "Ауэзовский": {"lat": 43.225, "lon": 76.855, "routes": ["11", "37", "118"], "base_traffic": 4.8, "traffic_lights": [[43.228, 76.850]]},
    "Жетысуский": {"lat": 43.290, "lon": 76.935, "routes": ["17", "29", "50"], "base_traffic": 4.2, "traffic_lights": [[43.295, 76.930]]},
    "Турксибский": {"lat": 43.340, "lon": 76.960, "routes": ["2", "48", "74"], "base_traffic": 3.8, "traffic_lights": [[43.345, 76.965]]},
    "Наурызбайский": {"lat": 43.200, "lon": 76.815, "routes": ["15", "44", "22"], "base_traffic": 3.0, "traffic_lights": [[43.205, 76.820]]},
    "Алатауский": {"lat": 43.285, "lon": 76.825, "routes": ["102", "124", "14"], "base_traffic": 3.5, "traffic_lights": [[43.280, 76.820]]}
}

# --- 3. ГЕНЕРАЦИЯ ДИНАМИЧЕСКИХ ДАННЫХ ---
rows = []
for name, info in districts_db.items():
    traffic = np.clip(info["base_traffic"] * time_factor + np.random.uniform(-0.5, 0.5), 1, 10)
    aqi = np.clip(100 * (traffic / 5) + np.random.randint(-20, 20), 50, 300)
    # ДТП зависят от трафика: чем больше пробки, тем выше шанс аварии
    incidents = int(np.random.poisson(traffic / 3)) 
    rows.append({
        "Район": name, "Пробки": traffic, "AQI": aqi, "Инциденты": incidents,
        "lat": info["lat"], "lon": info["lon"], "lights": info["traffic_lights"]
    })
df = pd.DataFrame(rows)

# --- 4. ИНТЕРФЕЙС ---
st.title("🏙️ CityPulse: Интеллектуальное управление Алматы")
st.subheader(f"Текущее время: {datetime.now().strftime('%H:%M')} | {'ЧАС ПИК' if time_factor > 1.5 else 'Штатный режим'}")

selected_district = st.sidebar.selectbox("🎯 Выберите район:", list(districts_db.keys()))
d_data = df[df["Район"] == selected_district].iloc[0]

# Метрики
m1, m2, m3, m4 = st.columns(4)
m1.metric("Трафик", f"{d_data['Пробки']:.1f} баллов", delta="Пиковая нагрузка" if time_factor > 1.5 else None)
m2.metric("Воздух", f"{int(d_data['AQI'])} AQI", delta="Загрязнение" if d_data['AQI'] > 150 else None, delta_color="inverse")
m3.metric("ДТП (сейчас)", f"{d_data['Инциденты']} ед.")
m4.metric("Активных светофоров", f"{len(d_data['lights'])} узлов")

st.divider()

# --- 5. ТЕПЛОВАЯ КАРТА СО СВЕТОФОРАМИ ---
st.subheader(f"📍 Карта инцидентов и светофоров: {selected_district}")

# Точки пробок
map_points = pd.DataFrame({
    'lat': [d_data['lat'] + np.random.uniform(-0.01, 0.01) for _ in range(20)],
    'lon': [d_data['lon'] + np.random.uniform(-0.01, 0.01) for _ in range(20)],
    'intensity': [d_data['Пробки']] * 20
})

fig_map = px.density_mapbox(map_points, lat='lat', lon='lon', z='intensity',
                        radius=40, center=dict(lat=d_data['lat'], lon=d_data['lon']),
                        zoom=12.5, mapbox_style="carto-positron", color_continuous_scale="Reds", range_color=[0, 10])

# Добавляем точки светофоров для оптимизации
lights_lat = [l[0] for l in d_data['lights']]
lights_lon = [l[1] for l in d_data['lights']]

fig_map.add_trace(go.Scattermapbox(
    lat=lights_lat, lon=lights_lon,
    mode='markers+text',
    marker=go.scattermapbox.Marker(size=14, color='blue', symbol='circle'),
    text=["🚦 Оптимизация" for _ in lights_lat],
    textposition="bottom center",
    name="Светофоры"
))

fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, showlegend=False)
st.plotly_chart(fig_map, use_container_width=True)

# --- 6. ЧАТ-БОТ АНАЛИТИК ---
st.divider()
st.header("🧠 Аналитический отчет ИИ")

with st.chat_message("assistant"):
    # ИИ анализирует время и данные
    time_comment = "В городе наблюдается вечерний час пик." if time_factor > 1.5 else "Трафик соответствует норме для данного времени суток."
    worst_district = df.loc[df['Пробки'].idxmax()]['Район']
    
    st.write(f"**Сводка на {datetime.now().strftime('%H:%M')}:**")
    st.write(f"- {time_comment}")
    st.write(f"- В районе {selected_district} зафиксировано {d_data['Инциденты']} ДТП. Это влияет на рост AQI до {int(d_data['AQI'])}.")
    st.write(f"- **Рекомендация:** Требуется ручная корректировка фаз на {len(d_data['lights'])} светофорах (отмечены синим на карте).")
    st.write(f"- Самый загруженный район города сейчас: **{worst_district}**.")

# Кнопка действия
if st.button(f"⚡ Оптимизировать светофоры в {selected_district}"):
    st.balloons()
    st.success("Команда передана в Центр управления трафиком. Время ожидания сокращено на 15%!")
