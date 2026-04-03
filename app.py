import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Almaty AI Control", layout="wide")

# --- 1. ТОЧНЫЕ ДАННЫЕ ПО РАЙОНАМ АЛМАТЫ ---
# Координаты центров районов для корректной карты
district_info = {
    "Медеуский": {"lat": 43.245, "lon": 76.955, "base_traffic": 6, "base_aqi": 140},
    "Бостандыкский": {"lat": 43.215, "lon": 76.915, "base_traffic": 7, "base_aqi": 110},
    "Алмалинский": {"lat": 43.250, "lon": 76.925, "base_traffic": 8, "base_aqi": 130},
    "Ауэзовский": {"lat": 43.225, "lon": 76.855, "base_traffic": 7, "base_aqi": 90},
    "Жетысуский": {"lat": 43.290, "lon": 76.935, "base_traffic": 5, "base_aqi": 150},
    "Турксибский": {"lat": 43.340, "lon": 76.960, "base_traffic": 4, "base_aqi": 160},
    "Наурызбайский": {"lat": 43.200, "lon": 76.815, "base_traffic": 3, "base_aqi": 70},
    "Алатауский": {"lat": 43.285, "lon": 76.825, "base_traffic": 4, "base_aqi": 100}
}

districts = list(district_info.keys())

# Генерация динамических данных
def get_current_metrics():
    rows = []
    for name, info in district_info.items():
        rows.append({
            "Район": name,
            "lat": info["lat"],
            "lon": info["lon"],
            "Пробки": np.clip(info["base_traffic"] + np.random.uniform(-1.5, 2.0), 0, 10),
            "AQI": np.clip(info["base_aqi"] + np.random.randint(-20, 40), 20, 300),
            "Шум": np.random.randint(60, 85),
            "Инциденты": np.random.randint(0, 4),
            "Светофоры_задержка": np.random.randint(30, 90)
        })
    return pd.DataFrame(rows)

df = get_current_metrics()

# --- 2. ИНТЕРФЕЙС ---
st.title("🛡️ Ситуационный центр Алматы: AI Мониторинг")

# Сайдбар с выбором
selected_district = st.sidebar.selectbox("🎯 Выберите район для управления:", districts)
d_data = df[df["Район"] == selected_district].iloc[0]

# Главные метрики (теперь они привязаны к выбранному району)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Загруженность", f"{d_data['Пробки']:.1f} / 10", delta_color="inverse")
m2.metric("Воздух (AQI)", f"{int(d_data['AQI'])}", delta="Не ок" if d_data['AQI'] > 100 else "Ок")
m3.metric("Инциденты", f"{int(d_data['Инциденты'])} ед.")
m4.metric("Шум", f"{d_data['Шум']} дБ")

st.divider()

# --- 3. ТЕПЛОВАЯ КАРТА (ИСПРАВЛЕННАЯ) ---
st.subheader(f"🗺️ Карта инцидентов: {selected_district}")
# Центрируем карту на выбранном районе
fig_map = px.density_mapbox(df, lat='lat', lon='lon', z='Пробки', 
                        radius=50, zoom=11,
                        center=dict(lat=d_data['lat'], lon=d_data['lon']),
                        mapbox_style="carto-positron", 
                        color_continuous_scale="YlOrRd",
                        title="Тепловая карта плотности трафика")
st.plotly_chart(fig_map, use_container_width=True)

# --- 4. ИИ АНАЛИТИКА И ПРОГНОЗ ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("🤖 Модуль объяснимого ИИ (XAI)")
    reason = "Критический затор" if d_data['Пробки'] > 7.5 else "Плановая нагрузка"
    st.warning(f"**Анализ по району {selected_district}:** {reason}")
    st.write(f"**Что произошло:** Наблюдается эффект 'бутылочного горлышка'. Высокий AQI ({int(d_data['AQI'])}) подтверждает застой воздушных масс из-за медленного трафика.")
    st.write("**Развитие:** Если не перенастроить светофоры, через 20 минут затор парализует выезды из района.")

with col_right:
    st.subheader("📈 Прогноз на 60 минут")
    steps = [datetime.now() + timedelta(minutes=i*15) for i in range(5)]
    # Имитация прогноза: если пробки высокие, они будут расти без мер
    vals = [d_data['Пробки'] + (i * 0.3) for i in range(5)]
    fig_prog = go.Figure(data=go.Scatter(x=steps, y=vals, mode='lines+markers', name='Прогноз'))
    fig_prog.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_prog, use_container_width=True)

# --- 5. КОМАНДЫ УПРАВЛЕНИЯ ---
st.divider()
st.header("📲 Команды оперативного реагирования")
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("🚦 Оптимизировать светофоры"):
        st.success(f"Циклы в {selected_district} изменены: +45с к зеленой фазе")
with c2:
    if st.button("🚌 Добавить автобусы"):
        st.info("На линии выведен резервный состав (маршруты: 92, 121, 32)")
with c3:
    if st.button("📢 Оповестить жителей"):
        st.write("Push-уведомления отправлены пользователям в радиусе 2км")

st.sidebar.markdown(f"**Координаты центра:** \nLat: {d_data['lat']}  \nLon: {d_data['lon']}")
