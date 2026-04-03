import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz

# --- 0. КОНФИГУРАЦИЯ СТРАНИЦЫ ---
st.set_page_config(
    page_title="CityPulse AI | Almaty",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомный CSS для профессионального вида
st.markdown("""
    <style>
    /* Главный фон и шрифт */
    .main { background-color: #0e1117; }
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
    }
    /* Стилизация метрик */
    [data-testid="stMetricValue"] {
        font-size: 24px !important;
        font-weight: 700;
        color: #00d4ff;
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    /* Контейнеры (карточки) */
    div.stButton > button {
        width: 100%;
        border-radius: 5px;
        border: 1px solid #4f4f4f;
        background-color: #1a1c24;
        color: white;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        border-color: #00d4ff;
        color: #00d4ff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. ВРЕМЯ И ДАННЫЕ (UTC+5) ---
tz_almaty = pytz.timezone('Asia/Almaty')
almaty_now = datetime.now(tz_almaty)
h = almaty_now.hour

# Коэффициент пробок (2ГИС стиль)
if 8 <= h <= 10 or 17 <= h <= 19:
    t_factor, mode = 1.8, "ПИКОВАЯ НАГРУЗКА"
elif 21 <= h or h <= 6:
    t_factor, mode = 0.4, "НОЧНОЙ РЕЖИМ"
else:
    t_factor, mode = 1.0, "СТАНДАРТ"

districts_db = {
    "Медеуский": {"lat": 43.245, "lon": 76.955, "routes": ["12", "28", "60"], "base": 7.2},
    "Бостандыкский": {"lat": 43.215, "lon": 76.915, "routes": ["38", "63", "127"], "base": 7.8},
    "Алмалинский": {"lat": 43.250, "lon": 76.925, "routes": ["92", "98", "79"], "base": 8.1},
    "Ауэзовский": {"lat": 43.225, "lon": 76.855, "routes": ["11", "103", "118"], "base": 6.8},
    "Жетысуский": {"lat": 43.290, "lon": 76.935, "routes": ["17", "50"], "base": 6.2},
    "Турксибский": {"lat": 43.340, "lon": 76.960, "routes": ["2", "74"], "base": 5.5},
    "Наурызбайский": {"lat": 43.200, "lon": 76.815, "routes": ["15", "22"], "base": 4.2},
    "Алатауский": {"lat": 43.285, "lon": 76.825, "routes": ["102", "14"], "base": 5.0}
}

@st.cache_data
def get_data(hour_val):
    data = []
    for name, info in districts_db.items():
        tr = np.clip(info["base"] * t_factor + np.random.uniform(-0.4, 0.4), 1, 10)
        data.append({
            "Район": name, "Пробки": tr, 
            "AQI": int(30 + tr*15), "ДТП": int(np.random.poisson(tr/3.5))
        })
    return pd.DataFrame(data)

df = get_data(h)

# --- 2. ИНТЕРФЕЙС ---
st.title("CITYPULSE | ALMATY AI")
st.caption(f"СИСТЕМА УПРАВЛЕНИЯ ГОРОДОМ • {almaty_now.strftime('%H:%M')} • {mode}")

selected = st.sidebar.selectbox("ВЫБОР ОБЪЕКТА", list(districts_db.keys()))
d_row = df[df["Район"] == selected].iloc[0]

# Метрики (одноразмерные)
col1, col2, col3, col4 = st.columns(4)
col1.metric("ТРАФИК", f"{d_row['Пробки']:.1f}/10")
col2.metric("ВОЗДУХ", f"{d_row['AQI']} AQI")
col3.metric("ИНЦИДЕНТЫ", f"{d_row['ДТП']} ЕД.")
col4.metric("СТАТУС", "АКТИВЕН" if d_row['Пробки'] < 8 else "КРИТИЧЕН")

st.markdown("---")

# --- 3. КАРТА И АНАЛИТИКА ---
c1, c2 = st.columns([2, 1])

with c1:
    # Тепловая карта (минимализм)
    pts = pd.DataFrame({
        'lat': [districts_db[selected]['lat'] + np.random.uniform(-0.01, 0.01) for _ in range(20)],
        'lon': [districts_db[selected]['lon'] + np.random.uniform(-0.01, 0.01) for _ in range(20)],
        'val': [d_row['Пробки']] * 20
    })
    fig = px.density_mapbox(pts, lat='lat', lon='lon', z='val', radius=30,
                            center=dict(lat=districts_db[selected]['lat'], lon=districts_db[selected]['lon']),
                            zoom=12, mapbox_style="carto-darkmatter")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.write("**АНАЛИЗ ПРОГНОЗА**")
    trend = -0.5 if h >= 20 else 0.3
    fut_v = [np.clip(d_row['Пробки'] + (i*trend), 1, 10) for i in range(4)]
    fut_t = [(almaty_now + timedelta(minutes=i*15)).strftime('%H:%M') for i in range(4)]
    
    fig_f = px.line(x=fut_t, y=fut_v, markers=True)
    fig_f.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), yaxis_range=[0,10], 
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_f, use_container_width=True)
    
    st.write("**РЕКОМЕНДАЦИЯ ИИ**")
    st.info(f"Оптимизировать маршруты: {', '.join(districts_db[selected]['routes'])}")

# --- 4. ОПЕРАЦИОННЫЙ БЛОК ---
st.markdown("### ОПЕРАТИВНЫЕ КОМАНДЫ")
b1, b2, b3 = st.columns(3)
if b1.button("СВЕТОФОРЫ"): st.toast("Синхронизация...")
if b2.button("ТРАНСПОРТ"): st.toast("Резерв выведен")
if b3.button("ОПОВЕЩЕНИЕ"): st.toast("SMS отправлены")

# --- 5. ЧАТ ---
st.markdown("---")
st.write("**ГЛОБАЛЬНЫЙ МОНИТОРИНГ (AI ЧАТ)**")
if "msg" not in st.session_state: st.session_state.msg = []

for m in st.session_state.msg:
    with st.chat_message(m["r"]): st.write(m["c"])

if p := st.chat_input("Запрос к системе..."):
    st.session_state.msg.append({"r": "user", "c": p})
    worst = df.loc[df['Пробки'].idxmax()]['Район']
    ans = f"Внимание: Максимальный затор в районе {worst}. В {selected}е ситуация стабильна."
    st.session_state.msg.append({"r": "assistant", "c": ans})
    st.rerun()
