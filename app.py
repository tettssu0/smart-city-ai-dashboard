
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Almaty AI City Management", layout="wide")

# --- 1. БАЗА ДАННЫХ ПО РАЙОНАМ (РЕАЛЬНЫЕ КООРДИНАТЫ И МАРШРУТЫ) ---
districts_db = {
    "Медеуский": {
        "lat": 43.245, "lon": 76.955, "routes": ["12", "28", "141", "60", "114"],
        "base_traffic": 7.5, "problem": "Затор на пр. Достык / пр. Аль-Фараби"
    },
    "Бостандыкский": {
        "lat": 43.215, "lon": 76.915, "routes": ["38", "63", "86", "127", "212"],
        "base_traffic": 8.2, "problem": "Скопление транспорта по ул. Розыбакиева"
    },
    "Алмалинский": {
        "lat": 43.250, "lon": 76.925, "routes": ["92", "98", "99", "119", "79"],
        "base_traffic": 8.5, "problem": "Затор на ул. Толе би / ул. Байтурсынова"
    },
    "Ауэзовский": {
        "lat": 43.225, "lon": 76.855, "routes": ["11", "37", "45", "103", "118"],
        "base_traffic": 7.0, "problem": "Высокая нагрузка по пр. Абая"
    },
    "Жетысуский": {
        "lat": 43.290, "lon": 76.935, "routes": ["7", "17", "29", "47", "50"],
        "base_traffic": 6.5, "problem": "Затруднение в районе барахолки / ш. Северное кольцо"
    },
    "Турксибский": {
        "lat": 43.340, "lon": 76.960, "routes": ["2", "48", "59", "71", "74"],
        "base_traffic": 5.8, "problem": "Нагрузка на ул. Майлина (район Аэропорта)"
    },
    "Наурызбайский": {
        "lat": 43.200, "lon": 76.815, "routes": ["15", "44", "137", "22", "115"],
        "base_traffic": 4.5, "problem": "Замедление на ул. Шаляпина"
    },
    "Алатауский": {
        "lat": 43.285, "lon": 76.825, "routes": ["102", "124", "125", "135", "14"],
        "base_traffic": 5.2, "problem": "Нагрузка в районе Almaty Arena"
    }
}

# --- 2. ЛОГИКА ВЫБОРА И ГЕНЕРАЦИЯ ДАННЫХ ---
st.title("🏙️ Центр интеллектуального управления г. Алматы")

selected_district = st.sidebar.selectbox("🎯 Выберите район:", list(districts_db.keys()))
d_info = districts_db[selected_district]

# Генерируем уникальные метрики для выбранного района
current_traffic = np.clip(d_info["base_traffic"] + np.random.uniform(-0.5, 1.5), 0, 10)
current_aqi = np.random.randint(60, 220)
current_incidents = np.random.randint(0, 5)

# --- 3. ИНТЕРФЕЙС: МЕТРИКИ ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Трафик района", f"{current_traffic:.1f} баллов")
m2.metric("Качество воздуха", f"{current_aqi} AQI")
m3.metric("ДТП / Инциденты", f"{current_incidents} ед.")
m4.metric("Шум в районе", f"{np.random.randint(65, 85)} дБ")

st.divider()

# --- 4. ТЕПЛОВАЯ КАРТА (ТОЛЬКО ДЛЯ ВЫБРАННОГО РАЙОНА) ---
st.subheader(f"📍 Локальная тепловая карта: {selected_district}")

# Создаем точки только вокруг центра выбранного района для эффекта локальности
map_data = pd.DataFrame({
    'lat': [d_info['lat'] + np.random.uniform(-0.01, 0.01) for _ in range(10)],
    'lon': [d_info['lon'] + np.random.uniform(-0.01, 0.01) for _ in range(10)],
    'intensity': [current_traffic] * 10
})

fig_map = px.density_mapbox(map_data, lat='lat', lon='lon', z='intensity',
                        radius=60, center=dict(lat=d_info['lat'], lon=d_info['lon']),
                        zoom=12, mapbox_style="carto-positron",
                        color_continuous_scale="Reds")
st.plotly_chart(fig_map, use_container_width=True)

# --- 5. УНИКАЛЬНЫЙ ПРОГНОЗ И ИИ-АНАЛИЗ ---
c_left, c_right = st.columns(2)

with c_left:
    st.subheader("📉 Прогноз нагрузки на 60 мин")
    # Прогноз зависит от текущего трафика (растет или падает случайно)
    trend = np.random.choice([0.2, -0.1, 0.4]) 
    future_times = [datetime.now() + timedelta(minutes=i*15) for i in range(5)]
    future_vals = [current_traffic + (i * trend) for i in range(5)]
    
    fig_forecast = go.Figure(go.Scatter(x=future_times, y=future_vals, mode='lines+markers', line=dict(color='red')))
    fig_forecast.update_layout(height=300)
    st.plotly_chart(fig_forecast, use_container_width=True)

with c_right:
    st.subheader("🤖 Модуль объяснимого ИИ")
    st.info(f"**Анализ ситуации в {selected_district}:**\n\n"
            f"Обнаружена проблема: {d_info['problem']}. "
            f"Уровень критичности: {'ВЫСОКИЙ' if current_traffic > 7
