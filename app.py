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
st.title("✨ Астро-Процессор (Ручной ввод)")

# --- БАЗЫ ДАННЫХ ---
zodiac_signs = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]
roman_nums = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
planets_map = {"Солнце": swe.SUN, "Луна": swe.MOON, "Меркурий": swe.MERCURY, "Венера": swe.VENUS, "Марс": swe.MARS, "Юпитер": swe.JUPITER, "Сатурн": swe.SATURN}

# --- ИНТЕРФЕЙС ВВОДА ---
st.markdown("### Введите данные вручную")
col1, col2, col3 = st.columns(3)

with col1:
    date_str = st.text_input("Дата (ДД.ММ.ГГГГ)", value="01.01.1990", help="Например: 07.06.1979")
with col2:
    time_str = st.text_input("Время (ЧЧ:ММ)", value="12:00", help="Например: 23:20")
with col3:
    city_input = st.text_input("Город (латиница)", value="Moscow")

b_tz = st.selectbox("Часовой пояс", sorted(pytz.all_timezones), index=sorted(pytz.all_timezones).index("Europe/Moscow"))

if st.button("Рассчитать карту", type="primary"):
    try:
        # 1. Парсим дату и время
        try:
            birth_date = datetime.strptime(date_str, "%d.%m.%Y")
            birth_time = datetime.strptime(time_str, "%H:%M").time()
        except:
            st.error("❌ Неверный формат! Используйте ДД.ММ.ГГГГ для даты и ЧЧ:ММ для времени.")
            st.stop()

        # 2. Геолокация
        geolocator = Nominatim(user_agent="astro_manual_app")
        location = geolocator.geocode(city_input)
        if not location:
            st.error("❌ Город не найден. Попробуйте написать по-английски (например, Izberbash).")
            st.stop()
        
        lat, lon = location.latitude, location.longitude
        st.success(f"📍 {location.address}")

        # 3. Расчет UTC и Юлианского дня
        local_tz = pytz.timezone(b_tz)
        local_dt = local_tz.localize(datetime.combine(birth_date, birth_time))
        utc_dt = local_dt.astimezone(pytz.UTC)
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)

        # 4. Расчет домов и планет
        houses_cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        
        p_results = []
        planet_pos = {}
        for name, p_id in planets_map.items():
            res, _ = swe.calc_ut(jd, p_id)
            lon_p = res[0]
            planet_pos[name] = lon_p
            sign_idx = int(lon_p / 30)
            deg_in_sign = lon_p % 30
            p_results.append({"Планета": name, "Знак": zodiac_signs[sign_idx], "Градус": f"{int(deg_in_sign)}° {int((deg_in_sign%1)*60)}'"})

        h_results = []
        for i in range(12):
            c_deg = houses_cusps[i]
            h_results.append({"Дом": roman_nums[i+1], "Знак": zodiac_signs[int(c_deg/30)], "Градус": f"{int(c_deg%30)}° {int((c_deg%1)*60)}'"})

        # 5. Отрисовка
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.set_aspect('equal')
        ax.axis('off')
        ax.add_patch(plt.Circle((0, 0), 10, fill=False, linewidth=2))
        ax.add_patch(plt.Circle((0, 0), 7, fill=False))
        
        # Знаки
        for i in range(12):
            angle = math.radians(i * 30)
            ax.plot([7*math.cos(angle), 10*math.cos(angle)], [7*math.sin(angle), 10*math.sin(angle)], color='gray', alpha=0.3)
            ax.text(8.5*math.cos(angle+0.26), 8.5*math.sin(angle+0.26), zodiac_signs[i][:3], ha='center')

        # Дома (куспиды)
        for i in range(12):
            ang = math.radians(houses_cusps[i])
            ax.plot([4*math.cos(ang), 10*math.cos(ang)], [4*math.sin(ang), 10*math.sin(ang)], color='blue', linestyle='--')

        # Планеты
        for name, lon_p in planet_pos.items():
            ang = math.radians(lon_p)
            ax.text(6*math.cos(ang), 6*math.sin(ang), name[:3], fontweight='bold', ha='center')

        # Вывод
        c_left, c_right = st.columns([1, 1])
        with c_left: st.pyplot(fig)
        with c_right:
            st.write("**Планеты**")
            st.table(pd.DataFrame(p_results))
            st.write("**Дома**")
            st.table(pd.DataFrame(h_results))

    except Exception as e:
        st.error(f"Ошибка: {e}")
