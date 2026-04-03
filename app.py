import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Настройка страницы
st.set_page_config(page_title="Almaty AI City Management", layout="wide")

# --- 1. БАЗА ДАННЫХ ПО РАЙОНАМ (РЕАЛЬНЫЕ КООРДИНАТЫ И МАРШРУТЫ) ---
districts_db = {
    "Медеуский": {
        "lat": 43.245, "lon": 76.955, 
        "routes": ["12", "28", "141", "60", "114"],
        "base_traffic": 7.5, 
        "problem": "Затор на пр. Достык / пр. Аль-Фараби"
    },
    "Бостандыкский": {
        "lat": 43.215, "lon": 76.915, 
        "routes": ["38", "63", "86", "127", "212"],
        "base_traffic": 8.2, 
        "problem": "Скопление транспорта по ул. Розыбакиева"
    },
    "Алмалинский": {
        "lat": 43.250, "lon": 76.925, 
        "routes": ["92", "98", "99", "119", "79"],
        "base_traffic": 8.5, 
        "problem": "Затор на ул. Толе би / ул. Байтурсынова"
    },
    "Ауэзовский": {
        "lat": 43.225, "lon": 76.855, 
        "routes": ["11", "37", "45", "103", "118"],
        "base_traffic": 7.0, 
        "problem": "Высокая нагрузка по пр. Абая"
    },
    "Жетысуский": {
        "lat": 43.290, "lon": 76.935, 
        "routes": ["7", "17", "29", "47", "50"],
        "base_traffic": 6.5, 
        "problem": "Затруднение в районе барахолки / ш. Северное кольцо"
    },
    "Турксибский": {
        "lat": 43.340, "lon": 76.960, 
        "routes": ["2", "48", "59", "71", "74"],
        "base_traffic": 5.8, 
        "problem": "Нагрузка на ул. Майлина (район Аэропорта)"
    },
    "Наурызбайский": {
        "lat": 43.200, "lon": 76.815, 
        "routes": ["15", "44", "137", "22", "115"],
        "base_traffic": 4.5, 
        "problem": "Замедление на ул. Шаляпина"
    },
    "Алатауский": {
        "lat": 43.285, "lon": 76.825, 
        "routes": ["102", "124", "125", "135", "14"],
        "base_traffic": 5.2, 
        "problem": "Нагрузка в районе Almaty Arena"
    }
}

# --- 2. ЛОГИКА ВЫБОРА РАЙОНА ---
st.title("🏙️ Центр интеллектуального управления г. Алматы")

selected_district = st.sidebar.selectbox("🎯 Выберите район управления:", list(districts_db.keys()))
d_info = districts_db[selected_district]

# Генерация динамических метрик для выбранного района
current_traffic = np.clip(d_info["base_traffic"] + np.random.uniform(-0.5, 1.5), 0, 10)
current_aqi = np.random.randint(60, 220)
current_incidents = np.random.randint(0, 5)
current_noise = np.random.randint(65, 85)

# --- 3. ИНТЕРФЕЙС: ВЕРХНИЕ МЕТРИКИ ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Трафик района", f"{current_traffic:.1f} баллов")
m2.metric("Качество воздуха", f"{current_aqi} AQI")
m3.metric("ДТП / Инциденты", f"{current_incidents} ед.")
m4.metric("Шум в районе", f"{current_noise} дБ")

st.divider()

# --- 4. ТЕПЛОВАЯ КАРТА (ТОЛЬКО ВЫБРАННЫЙ РАЙОН) ---
st.subheader(f"📍 Локальная тепловая карта: {selected_district}")

map_points = pd.DataFrame({
    'lat': [d_info['lat'] + np.random.uniform(-0.008, 0.008) for _ in range(15)],
    'lon': [d_info['lon'] + np.random.uniform(-0.008, 0.008) for _ in range(15)],
    'intensity': [current_traffic] * 15
})

fig_map = px.density_mapbox(map_points, lat='lat', lon='lon', z='intensity',
                        radius=50, center=dict(lat=d_info['lat'], lon=d_info['lon']),
                        zoom=12.5, mapbox_style="carto-positron",
                        color_continuous_scale="Reds")
st.plotly_chart(fig_map, use_container_width=True)

# --- 5. УНИКАЛЬНЫЙ ПРОГНОЗ И ИИ-АНАЛИЗ ---
c_left, c_right = st.columns(2)

with c_left:
    st.subheader("📉 Прогноз нагрузки на 60 мин")
    trend = np.random.choice([0.3, -0.2, 0.5]) 
    future_times = [datetime.now() + timedelta(minutes=i*15) for i in range(5)]
    future_vals = [np.clip(current_traffic + (i * trend), 0, 10) for i in range(5)]
    
    fig_forecast = go.Figure(go.Scatter(x=future_times, y=future_vals, mode='lines+markers', line=dict(color='firebrick', width=3)))
    fig_forecast.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig_forecast, use_container_width=True)

with c_right:
    st.subheader("🤖 Модуль объяснимого ИИ")
    
    # Исправленная логика: выносим расчеты из f-строк
    status_text = "ВЫСОКИЙ" if current_traffic > 7.0 else "СРЕДНИЙ"
    delay_estimate = int(current_traffic * 2.5)
    
    st.info(f"**Анализ ситуации в {selected_district}:**\n\n"
            f"**Проблема:** {d_info['problem']}. \n\n"
            f"**Критичность:** {status_text}.\n\n"
            f"**ИИ Прогноз:** Рост времени в пути на {delay_estimate} мин. в ближайший час.")

# --- 6. КОМАНДЫ РЕАГИРОВАНИЯ ---
st.divider()
st.header("📲 Пакет оперативных решений")

col_cmd1, col_cmd2, col_cmd3 = st.columns(3)

with col_cmd1:
    st.markdown("**🚥 Светофоры и Дороги**")
    st.write("• Адаптивная фаза: +40 сек.")
    st.write("• Открытие дополнительной полосы")
    if st.button("Применить настройки"):
        st.toast("Сигналы светофоров перенастроены!")

with col_cmd2:
    st.markdown("**🚌 Общественный транспорт**")
    routes_list = ", ".join(d_info['routes'])
    st.write(f"• Увеличить частоту маршрутов: {routes_list}")
    if st.button("Вывести резервные автобусы"):
        st.success(f"Доп. транспорт запущен в {selected_district}е")

with col_cmd3:
    st.markdown("**📡 Уведомления и Службы**")
    st.write("• Рассылка в навигаторы 2GIS/Waze")
    st.write("• Передача тикета в гор. службы")
    if st.button("Запустить систему оповещения"):
        st.write("✅ Водители и экстренные службы уведомлены")

st.sidebar.markdown("---")
st.sidebar.caption(f"Координаты узла: {d_info['lat']}, {d_info['lon']}")
st.sidebar.caption("v3.0 Stable | Almaty Smart City AI")

# --- 7. ИНТЕЛЛЕКТУАЛЬНЫЙ ЧАТ-ПОМОЩНИК (ДАННЫЕ В РЕАЛЬНОМ ВРЕМЕНИ) ---
st.divider()
st.header("💬 AI Консультант: Анализ текущих графиков")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"Я проанализировал графики по району {selected_district}. Готов ответить на вопросы по пробкам ({current_traffic:.1f} балла) или экологии ({current_aqi} AQI)."}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Спросите ИИ о данных на графиках..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        user_query = prompt.lower()
        
        # ЛОГИКА АНАЛИЗА ГРАФИКОВ
        if "пробк" in user_query or "трафик" in user_query:
            if current_traffic > 7.5:
                response = f"**Анализ графика трафика:** Сейчас критический уровень ({current_traffic:.1f} балла). На тепловой карте видно красное смещение. Прогноз показывает рост, поэтому я уже предложил активировать маршруты {', '.join(d_info['routes'])}."
            else:
                response = f"**Анализ графика трафика:** Ситуация стабильная, {current_traffic:.1f} балла. На графике прогноза резких скачков не предвидится."

        elif "воздух" in user_query or "экология" in user_query or "aqi" in user_query:
            if current_aqi > 150:
                response = f"**Анализ датчиков воздуха:** Показатель {current_aqi} AQI (Опасно). Это коррелирует с пробками в {selected_district}е. Рекомендую ограничить движение на 20%."
            else:
                response = f"**Анализ датчиков воздуха:** Уровень {current_aqi} AQI в пределах нормы для города. Дополнительный мониторинг не требуется."

        elif "инцидент" in user_query or "дтп" in user_query:
            if current_incidents > 0:
                response = f"**Анализ дорожных событий:** На графике инцидентов зафиксировано {current_incidents} происшествий. Это основная причина задержки на светофорах ({d_info['problem']})."
            else:
                response = f"В районе {selected_district} ДТП на данный момент не зафиксировано. Движение идет в штатном режиме."

        elif "прогноз" in user_query or "через час" in user_query:
            # Берем последнее значение из нашего списка будущих значений (тренда)
            future_val = future_vals[-1] 
            diff = future_val - current_traffic
            trend_text = "ухудшение" if diff > 0 else "улучшение"
            response = f"**Анализ графика прогноза:** Через 60 минут ожидается {trend_text} до {future_val:.1f} баллов. Моя рекомендация: действовать на опережение прямо сейчас."
            
        else:
            response = f"Я вижу данные по району {selected_district}: Трафик {current_traffic:.1f}, Воздух {current_aqi}, Инциденты {current_incidents}. Спросите конкретнее об одном из этих графиков."

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
