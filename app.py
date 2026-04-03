import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Настройка страницы
st.set_page_config(page_title="CityPulse AI - Almaty", layout="wide")

# --- 1. ТОЧНАЯ ЛОГИКА ВРЕМЕНИ (АЛМАТЫ) ---
current_time_dt = datetime.now()
current_hour = current_time_dt.hour

if 8 <= current_hour <= 10:
    time_factor = 1.6  # Утренний час пик
    time_desc = "🌅 УТРЕННИЙ ПИК"
elif 17 <= current_hour <= 19:
    time_factor = 1.9  # Вечерний час пик (самый сложный)
    time_desc = "🌇 ВЕЧЕРНИЙ ПИК"
elif 20 <= current_hour <= 23:
    time_factor = 0.5  # ПОЗДНИЙ ВЕЧЕР (пробки уменьшаются)
    time_desc = "🌙 ВЕЧЕРНИЙ СПАД"
elif 0 <= current_hour <= 6:
    time_factor = 0.2  # НОЧЬ (пустые дороги)
    time_desc = "🌑 НОЧНОЙ РЕЖИМ"
else:
    time_factor = 1.0  # ДЕНЬ (стандартный трафик)
    time_desc = "☀️ ДНЕВНОЙ ТРАФИК"

# Изменяем также прогноз: если сейчас вечерний пик, то через час станет ЛУЧШЕ
if 18 <= current_hour <= 19:
    prediction_trend = -0.5 # Скоро пробки рассосутся
elif 7 <= current_hour <= 8 or 16 <= current_hour <= 17:
    prediction_trend = 0.6 # Пробки будут расти
else:
    prediction_trend = 0.1

# --- 2. БАЗА ДАННЫХ ---
districts_db = {
    "Медеуский": {"lat": 43.245, "lon": 76.955, "routes": ["12", "28", "141"], "base_traffic": 5.0, "lights": [[43.242, 76.958], [43.248, 76.950]], "problem": "Затор на пр. Достык"},
    "Бостандыкский": {"lat": 43.215, "lon": 76.915, "routes": ["38", "63", "86"], "base_traffic": 5.2, "lights": [[43.210, 76.910], [43.220, 76.920]], "problem": "Нагрузка по ул. Розыбакиева"},
    "Алмалинский": {"lat": 43.250, "lon": 76.925, "routes": ["92", "98", "99"], "base_traffic": 5.5, "lights": [[43.252, 76.928]], "problem": "Затор на Толе би"},
    "Ауэзовский": {"lat": 43.225, "lon": 76.855, "routes": ["11", "37", "118"], "base_traffic": 4.8, "lights": [[43.228, 76.850]], "problem": "Плотный поток по Абая"},
    "Жетысуский": {"lat": 43.290, "lon": 76.935, "routes": ["17", "29", "50"], "base_traffic": 4.2, "lights": [[43.295, 76.930]], "problem": "Район барахолки"},
    "Турксибский": {"lat": 43.340, "lon": 76.960, "routes": ["2", "48", "74"], "base_traffic": 3.8, "lights": [[43.345, 76.965]], "problem": "Кольцо ВАЗ / Аэропорт"},
    "Наурызбайский": {"lat": 43.200, "lon": 76.815, "routes": ["15", "44", "22"], "base_traffic": 3.0, "lights": [[43.205, 76.820]], "problem": "Узкие участки Шаляпина"},
    "Алатауский": {"lat": 43.285, "lon": 76.825, "routes": ["102", "124", "14"], "base_traffic": 3.5, "lights": [[43.280, 76.820]], "problem": "Район Almaty Arena"}
}

# Генерация данных города
rows = []
for name, info in districts_db.items():
    traffic = np.clip(info["base_traffic"] * time_factor + np.random.uniform(-0.3, 0.3), 1, 10)
    aqi = np.clip(100 * (traffic / 5) + np.random.randint(-15, 15), 50, 300)
    incidents = int(np.random.poisson(traffic / 3))
    rows.append({"Район": name, "Пробки": traffic, "AQI": aqi, "Инциденты": incidents, "lat": info["lat"], "lon": info["lon"], "lights": info["lights"]})
df = pd.DataFrame(rows)

# --- 3. ИНТЕРФЕЙС ---
st.title("🏙️ CityPulse: Ситуационный центр Алматы")
st.write(f"📊 Данные на {current_time_dt.strftime('%H:%M')} | Режим: {'🔥 ЧАС ПИК' if time_factor > 1.5 else '✅ ШТАТНЫЙ'}")

selected_district = st.sidebar.selectbox("🎯 Район управления:", list(districts_db.keys()))
d_data = df[df["Район"] == selected_district].iloc[0]
d_info = districts_db[selected_district]

# Метрики
m1, m2, m3, m4 = st.columns(4)
m1.metric("Трафик", f"{d_data['Пробки']:.1f} баллов")
m2.metric("Воздух", f"{int(d_data['AQI'])} AQI")
m3.metric("ДТП / События", f"{d_data['Инциденты']} ед.")
m4.metric("Светофоры (Smart)", f"{len(d_info['lights'])} шт.")

st.divider()

# --- 4. КАРТА СО СВЕТОФОРАМИ ---
st.subheader("📍 Тепловая карта и умные светофоры")
map_points = pd.DataFrame({
    'lat': [d_data['lat'] + np.random.uniform(-0.01, 0.01) for _ in range(20)],
    'lon': [d_data['lon'] + np.random.uniform(-0.01, 0.01) for _ in range(20)],
    'intensity': [d_data['Пробки']] * 20
})
fig_map = px.density_mapbox(map_points, lat='lat', lon='lon', z='intensity', radius=40, center=dict(lat=d_data['lat'], lon=d_data['lon']), zoom=12, mapbox_style="carto-positron", color_continuous_scale="Reds", range_color=[0, 10])

# Синие точки светофоров
l_lat = [l[0] for l in d_info['lights']]
l_lon = [l[1] for l in d_info['lights']]
fig_map.add_trace(go.Scattermapbox(lat=l_lat, lon=l_lon, mode='markers', marker=dict(size=15, color='blue'), text="🚦 Требует оптимизации"))
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, showlegend=False)
st.plotly_chart(fig_map, use_container_width=True)

# --- 5. ПРОГНОЗ И ПРЕДУПРЕЖДЕНИЯ ---
c_left, c_right = st.columns(2)
with c_left:
    st.subheader("📉 Прогноз на 60 минут")
    step = 0.4 if time_factor > 1.5 else -0.2
    future_vals = [np.clip(d_data['Пробки'] + (i * step), 0, 10) for i in range(5)]
    future_times = [(current_time_dt + timedelta(minutes=i*15)).strftime('%H:%M') for i in range(5)]
    fig_prog = px.line(x=future_times, y=future_vals, markers=True, labels={'x':'Время', 'y':'Баллы'})
    fig_prog.update_traces(line_color='firebrick')
    st.plotly_chart(fig_prog, use_container_width=True)

with c_right:
    st.subheader("⚠️ Оперативный статус")
    st.warning(f"**Проблема:** {d_info['problem']}")
    st.info(f"**Рекомендация ИИ:** Усилить частоту маршрутов: {', '.join(d_info['routes'])}")
    if st.button("📢 Оповестить жителей района"):
        st.success("Push-уведомления и SMS отправлены пользователям 2GIS/Waze!")

# --- 6. ИИ ЧАТ-БОТ (УМНЫЙ АНАЛИТИК) ---
st.divider()
st.header("💬 Глобальный ИИ-аналитик")
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Я анализирую все районы. Спросите меня о ситуации в городе!"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.write(msg["content"])

if prompt := st.chat_input("Напишите вопрос..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)
    
    with st.chat_message("assistant"):
        worst_t = df.loc[df['Пробки'].idxmax()]['Район']
        if "отчет" in prompt.lower() or "все" in prompt.lower():
            res = f"В Алматы сейчас {'пиковая нагрузка' if time_factor > 1.5 else 'спокойно'}. Хуже всего в районе {worst_t} ({df['Пробки'].max():.1f} балла). В {selected_district} зафиксировано {d_data['Инциденты']} ДТП."
        elif "пробк" in prompt.lower():
            res = f"Средний балл по городу: {df['Пробки'].mean():.1f}. В вашем районе — {d_data['Пробки']:.1f}."
        else:
            res = f"Я вижу, что в {selected_district}е сейчас {d_data['Пробки']:.1f} балла. Советую обратить внимание на светофоры."
        st.write(res)
        st.session_state.messages.append({"role": "assistant", "content": res})

# Кнопка оптимизации
if st.button("🚦 Оптимизировать светофоры"):
    st.balloons()
    st.success("Сигналы светофоров перенастроены. Пропускная способность увеличена!")
