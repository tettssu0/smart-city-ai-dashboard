import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Almaty AI Command Center", layout="wide")

# --- ИМИТАЦИЯ ДАННЫХ ---
districts = ["Медеуский", "Бостандыкский", "Алмалинский", "Ауэзовский", "Жетысуский", "Турксибский", "Наурызбайский", "Алатауский"]

def get_data():
    df = pd.DataFrame({
        "Район": districts,
        "Пробки": np.random.uniform(3, 9.8, len(districts)),
        "AQI": np.random.randint(50, 200, len(districts)),
        "Инциденты": np.random.randint(0, 6, len(districts)),
        "Шум": np.random.randint(60, 90, len(districts)),
        "Светофоры_задержка": np.random.randint(10, 150, len(districts)),
        "lat": [43.238, 43.210, 43.250, 43.220, 43.270, 43.340, 43.200, 43.280], # Координаты Алматы
        "lon": [76.945, 76.920, 76.910, 76.850, 76.930, 76.950, 76.800, 76.820]
    })
    return df

df = get_data()

# --- ВЕРХНЯЯ ПАНЕЛЬ ---
st.title("🛡️ Almaty Smart City: Система оперативного реагирования ИИ")
st.sidebar.header("Параметры системы")
selected_district = st.sidebar.selectbox("Выберите район управления:", districts)
d_data = df[df["Район"] == selected_district].iloc[0]

# --- 1. ТЕПЛОВАЯ КАРТА ГОРОДА ---
st.subheader("📍 Тепловая карта загруженности Алматы")
fig_map = px.density_mapbox(df, lat='lat', lon='lon', z='Пробки', radius=30,
                        center=dict(lat=43.238, lon=76.91), zoom=10,
                        mapbox_style="carto-positron", title="Концентрация трафика")
st.plotly_chart(fig_map, use_container_width=True)

# --- 2. ПРОГНОЗ НА ЧАС ---
st.subheader("⏳ Прогноз загруженности на ближайшие 60 минут")
time_steps = [datetime.now() + timedelta(minutes=i*10) for i in range(7)]
forecast_values = [d_data['Пробки'] + (np.sin(i)*0.5) for i in range(7)]
fig_forecast = go.Figure()
fig_forecast.add_trace(go.Scatter(x=time_steps, y=forecast_values, mode='lines+markers', line=dict(color='orange', width=4)))
fig_forecast.update_layout(yaxis_title="Баллы пробок", xaxis_title="Время")
st.plotly_chart(fig_forecast, use_container_width=True)

# --- 3. ИИ МОДУЛЬ ОБЪЯСНЕНИЯ (AI INSIGHTS) ---
st.divider()
st.header("🤖 ИИ-Аналитик: Что произошло?")

crit_level = "КРИТИЧЕСКИЙ" if d_data['Пробки'] > 8 else "СРЕДНИЙ"
color = "red" if crit_level == "КРИТИЧЕСКИЙ" else "orange"

st.markdown(f"### Уровень угрозы: <span style='color:{color}'>{crit_level}</span>", unsafe_allow_html=True)

col_ai1, col_ai2 = st.columns(2)
with col_ai1:
    st.info("📝 **Анализ ситуации**\n\n"
            f"В районе {selected_district} зафиксировано аномальное замедление потока до {int(d_data['Пробки']*5)} км/ч. "
            f"Причина: Высокая плотность транспорта + выявленный дорожный инцидент. Экологический фон (AQI: {d_data['AQI']}) "
            "превышает норму из-за скопления выхлопных газов.")
with col_ai2:
    st.success("🔮 **Прогноз развития**\n\n"
               "Без вмешательства через 30 минут пробка распространится на соседние магистрали. "
               "При активации предложенных мер ситуация стабилизируется в течение 15 минут.")

# --- 4. РЕКОМЕНДАЦИИ И ФОРСИРОВАНИЕ В СЛУЖБЫ ---
st.divider()
st.header("🚀 Оперативные решения и команды")

c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("🚦 Светофоры и Линии")
    st.write("🔹 **Перенастройка циклов:** Режим 'Зеленая волна' + 40 сек.")
    st.write("🔹 **Реверс:** Открыть доп. полосу на встречном направлении.")
    if st.button("Применить циклы"):
        st.toast("Светофоры перенастроены!")

with c2:
    st.subheader("🚌 Транспорт и Навигация")
    st.write(f"🔹 **Автобусы:** Частота маршрутов увеличена на 30%.")
    st.write("🔹 **Уведомление:** Разослана инфо в 2GIS/Yandex: 'Объезд через Саина'.")
    if st.button("Оповестить водителей"):
        st.toast("Навигационные данные обновлены!")

with c3:
    st.subheader("📞 Городские службы")
    st.warning("⚠️ Заявки отправлены:")
    st.write("- 🚓 Дорожная полиция (Патруль)")
    st.write("- 🛠️ Служба спасения (Эвакуация)")
    st.write("- 🌬️ Эко-мониторинг (Замер)")
    if st.button("Форсировать повторно"):
        st.write("Заявки подтверждены в Ситуационном центре г. Алматы")

st.divider()
st.caption("Almaty AI Command Center v2.0 | Данные синтезированы для демонстрации")
