import streamlit as st
import swisseph as swe
import pytz
import pandas as pd
import math
import itertools
import matplotlib.pyplot as plt
from datetime import datetime
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Астро Процессор", page_icon="✨", layout="wide")
st.title("✨ Астро-Процессор (Быстрый ввод цифрами)")

# --- ИНТЕРФЕЙС ВВОДА ---
st.markdown("### Данные рождения")

# Блок Даты
st.write("**Дата (ДД / ММ / ГГГГ)**")
col_d, col_m, col_y = st.columns([1, 1, 2])
with col_d:
    day = st.text_input("День", value="07", max_chars=2, key="d")
with col_m:
    month = st.text_input("Месяц", value="06", max_chars=2, key="m")
with col_y:
    year = st.text_input("Год", value="1979", max_chars=4, key="y")

# Блок Времени
st.write("**Время (ЧЧ : ММ)**")
col_h, col_min = st.columns([1, 1])
with col_h:
    hour = st.text_input("Часы", value="23", max_chars=2, key="h")
with col_min:
    minute = st.text_input("Минуты", value="20", max_chars=2, key="min")

# Город и Пояс
city_input = st.text_input("Город (латиница, например: Izberbash)", value="Izberbash")
tz_list = sorted(pytz.all_timezones)
b_tz = st.selectbox("Часовой пояс", tz_list, index=tz_list.index("Europe/Moscow"))

# --- ОБРАБОТКА ДАННЫХ ---
if st.button("Рассчитать карту", type="primary"):
    try:
        # Собираем дату и время из кусочков
        date_str = f"{day.zfill(2)}.{month.zfill(2)}.{year}"
        time_str = f"{hour.zfill(2)}:{minute.zfill(2)}"
        
        birth_date = datetime.strptime(date_str, "%d.%m.%Y")
        birth_time = datetime.strptime(time_str, "%H:%M").time()

        # Геолокация
        geolocator = Nominatim(user_agent="astro_fast_app")
        location = geolocator.geocode(city_input)
        if not location:
            st.error("❌ Город не найден. Напишите по-английски.")
            st.stop()
        
        lat, lon = location.latitude, location.longitude
        st.success(f"📍 {location.address}")

        # Астрологический расчет
        local_tz = pytz.timezone(b_tz)
        local_dt = local_tz.localize(datetime.combine(birth_date, birth_time))
        utc_dt = local_dt.astimezone(pytz.UTC)
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)

        # Дома и планеты
        houses_cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        zodiac = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]
        planets_map = {"Солнце": 0, "Луна": 1, "Меркурий": 2, "Венера": 3, "Марс": 4, "Юпитер": 5, "Сатурн": 6}
        
        p_results = []
        planet_pos = {}
        for name, p_id in planets_map.items():
            res, _ = swe.calc_ut(jd, p_id)
            lon_p = res[0]
            planet_pos[name] = lon_p
            p_results.append({"Планета": name, "Знак": zodiac[int(lon_p/30)], "Градус": f"{int(lon_p%30)}°"})

        # Отрисовка
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_aspect('equal')
        ax.add_patch(plt.Circle((0, 0), 10, fill=False))
        for i in range(12):
            ang = math.radians(i * 30)
            ax.plot([7*math.cos(ang), 10*math.cos(ang)], [7*math.sin(ang), 10*math.sin(ang)], color='gray')
        
        for name, lon_p in planet_pos.items():
            ang = math.radians(lon_p)
            ax.text(6*math.cos(ang), 6*math.sin(ang), name[:3], ha='center')

        st.pyplot(fig)
        st.table(pd.DataFrame(p_results))

    except Exception as e:
        st.error(f"Проверьте правильность цифр! Ошибка: {e}")
