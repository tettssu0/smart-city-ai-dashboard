import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Настройка страницы
st.set_page_config(page_title="Almaty AI City Management", layout="wide")

# --- 1. БАЗА ДАННЫХ ПО РАЙОНАМ ---
districts_db = {
    "Медеуский": {"lat": 43.245, "lon": 76.955, "routes": ["12", "28", "141", "60", "114"], "base_traffic": 7.5, "problem": "Затор на пр. Достык / пр. Аль-Фараби"},
    "Бостандыкский": {"lat": 43.215, "lon": 76.915, "routes": ["38", "63", "86", "127", "212"], "base_traffic": 8.2, "problem": "Скопление по ул. Розыбакиева"},
    "Алмалинский": {"lat": 43.250, "lon": 76.925, "routes": ["92", "98", "99", "119", "79"], "base_traffic": 8.5, "problem": "Затор на ул. Толе би / ул. Байтурсынова"},
    "Ауэзовский": {"lat": 43.225, "lon": 76.855, "routes": ["11", "37", "45", "103", "118"], "base_traffic": 7.0, "problem": "Высокая нагрузка по пр. Абая"},
    "Жетысуский": {"lat": 43.290, "lon": 76.935, "routes": ["7", "17", "29", "47", "50"], "base_traffic": 6.5, "problem": "Затруднение в районе барахолки"},
    "Турксибский": {"lat": 43.340, "lon": 76.960, "routes": ["2", "48", "59", "71", "74"], "base_traffic": 5.8, "problem": "Нагрузка в районе Аэропорта"},
    "Наурызбайский": {"lat": 43.200, "lon": 76.815, "routes": ["15", "44", "137", "22", "115"], "base_traffic": 4.5, "problem": "Замедление на ул. Шаляпина"},
    "Алатауский": {"lat": 43.285, "lon": 76.825, "routes": ["102", "124", "125", "135", "14"], "base_traffic": 5.2, "problem": "Нагрузка в районе Almaty Arena"}
}

# --- 2. ГЕНЕРАЦИЯ ОБЩЕЙ ТАБЛИЦЫ (ЧТОБЫ ИИ ВИДЕЛ ВЕСЬ ГОРОД) ---
@st.cache_data # Чтобы данные не прыгали при каждом клике
def create_city_df():
    rows = []
    for name, info in districts_db.items():
        rows.append({
            "Район": name,
            "Пробки": np.clip(info["base_traffic"] + np.random.uniform(-0.5, 1.5), 0, 10),
            "AQI": np.random.randint(60, 220),
            "Инциденты": np.random.randint(0, 5),
            "Шум": np.random.randint(65, 85),
            "lat": info["lat"],
            "lon": info["lon"]
        })
    return pd.DataFrame(rows)

df = create_city_df()

# --- 3. ВЫБОР РАЙОНА И ИНТЕРФЕЙС ---
st.title("🏙️ Центр интеллектуального управления г. Алматы")
selected_district = st.sidebar.selectbox("🎯 Выберите район управления:", list(districts_db.keys()))

# Данные конкретно для выбранного района
d_data = df[df["Район"] == selected_district].iloc[0]
d_info = districts_db[selected_district]

# Метрики
m1, m2, m3, m4 = st.columns(4)
m1.metric("Трафик района", f"{d_data['Пробки']:.1f} баллов")
m2.metric("Качество воздуха", f"{int(d_data['AQI'])} AQI")
m3.metric("ДТП / Инциденты", f"{int(d_data['Инциденты'])} ед.")
m4.metric("Шум в районе", f"{d_data['Шум']} дБ")

st.divider()

# --- 4. ТЕПЛОВАЯ КАРТА ---
st.subheader(f"📍 Оперативная обстановка: {selected_district}")
map_points = pd.DataFrame({
    'lat': [d_info['lat'] + np.random.uniform(-0.015, 0.015) for _ in range(30)],
    'lon': [d_info['lon'] + np.random.uniform(-0.015, 0.015) for _ in range(30)],
    'intensity': [d_data['Пробки']] * 30
})
fig_map = px.density_mapbox(map_points, lat='lat', lon='lon', z='intensity',
                        radius=40, center=dict(lat=d_info['lat'], lon=d_info['lon']),
                        zoom=12, mapbox_style="carto-positron", color_continuous_scale="Reds", range_color=[0, 10])
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, coloraxis_showscale=False)
st.plotly_chart(fig_map, use_container_width=True)

# --- 5. ПРОГНОЗ И АНАЛИЗ ---
c_left, c_right = st.columns(2)
with c_left:
    st.subheader("📉 Прогноз на 60 мин")
    trend = 0.3 # Можно сделать динамичным
    future_times = [datetime.now() + timedelta(minutes=i*15) for i in range(5)]
    future_vals = [np.clip(d_data['Пробки'] + (i * trend), 0, 10) for i in range(5)]
    fig_forecast = go.Figure(go.Scatter(x=future_times, y=future_vals, mode='lines+markers', line=dict(color='firebrick')))
    st.plotly_chart(fig_forecast, use_container_width=True)

with c_right:
    st.subheader("🤖 Модуль объяснимого ИИ")
    status_text = "ВЫСОКИЙ" if d_data['Пробки'] > 7.0 else "СРЕДНИЙ"
    st.info(f"**Анализ ситуации в {selected_district}:**\n\n**Проблема:** {d_info['problem']}. \n\n**Критичность:** {status_text}.")

# --- 6. КОМАНДЫ РЕАГИРОВАНИЯ ---
st.divider()
st.header("📲 Оперативные решения")
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🚦 Светофоры: Оптимизировать"): st.toast("Циклы изменены!")
with c2:
    if st.button("🚌 Автобусы: Усилить маршруты"): st.success(f"Доп. транспорт: {', '.join(d_info['routes'])}")
with c3:
    if st.button("📢 Оповестить жителей"): st.write("✅ Уведомления отправлены")

# --- 7. ГЛОБАЛЬНЫЙ ИИ-АНАЛИТИК ---
st.divider()
st.header("🧠 Глобальный ИИ-аналитик Алматы")
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Я анализирую все 8 районов. Спросите меня о ситуации в городе!"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]): st.markdown(message["content"])

if prompt := st.chat_input("Например: 'Общий отчет'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        user_query = prompt.lower()
        # ТЕПЕРЬ df ДОСТУПЕН ВЕЗДЕ!
        worst_traffic_district = df.loc[df['Пробки'].idxmax()]['Район']
        max_traffic_val = df['Пробки'].max()
        worst_air_district = df.loc[df['AQI'].idxmax()]['Район']
        
        if "отчет" in user_query or "все" in user_query:
            response = f"**Отчет по Алматы:** Хуже всего с пробками в районе **{worst_traffic_district}** ({max_traffic_val:.1f} балла). Самый высокий AQI в районе **{worst_air_district}**."
        elif "пробк" in user_query:
            response = f"В городе средняя загруженность {df['Пробки'].mean():.1f} балла. Лидер по заторам — {worst_traffic_district}."
        else:
            response = f"Я вижу данные по всем районам. В {selected_district}е сейчас {d_data['Пробки']:.1f} балла. Где еще проверить?"
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
