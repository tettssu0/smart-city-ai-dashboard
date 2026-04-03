import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Настройка страницы
st.set_page_config(page_title="Smart City Dashboard", layout="wide")

# Имитация данных с датчиков города
def load_data():
    now = datetime.now()
    times = [now - timedelta(hours=i) for i in range(12, 0, -1)]
    data = pd.DataFrame({
        "Время": times,
        "Пробки": [np.random.uniform(2, 9) for _ in range(12)],
        "Экология": [np.random.randint(40, 160) for _ in range(12)]
    })
    return data

df = load_data()
last_traffic = round(df["Пробки"].iloc[-1], 1)
last_eco = int(df["Eкология"].iloc[-1])

# --- ИНТЕРФЕЙС ---
st.title("🏙️ Smart City: Панель управления городом")
st.write(f"Обновлено: {datetime.now().strftime('%H:%M:%S')}")

# Метрики
col1, col2, col3 = st.columns(3)
col1.metric("Трафик (0-10)", f"{last_traffic}", delta="Затор" if last_traffic > 7 else "Норма")
col2.metric("Воздух (PM2.5)", f"{last_eco}", delta="Опасно" if last_eco > 120 else "Чисто")
col3.metric("Статус ИИ", "Активен")

st.divider()

# Графики
c1, c2 = st.columns(2)
with c1:
    st.subheader("🚦 Пробки в реальном времени")
    st.plotly_chart(px.area(df, x="Время", y="Пробки"), use_container_width=True)
with c2:
    st.subheader("🍃 Уровень загрязнения")
    st.plotly_chart(px.line(df, x="Время", y="Экология"), use_container_width=True)

# ИИ Аналитика для кейса
st.divider()
st.header("🤖 Рекомендации ИИ")
if last_traffic > 7 or last_eco > 120:
    st.error("### ⚠️ ВНИМАНИЕ: Критическая ситуация!")
    st.write("**Анализ:** Зафиксировано превышение норм трафика и загрязнения.")
    st.write("**Решение:** Перенаправить поток машин через объездную дорогу и активировать систему очистки воздуха.")
else:
    st.success("✅ Город в порядке. Вмешательство ИИ не требуется.")

# Боковая панель
st.sidebar.title("Настройки")
st.sidebar.info("MVP Dashboard для конкурса Smart City")
