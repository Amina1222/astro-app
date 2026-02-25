import streamlit as st
import swisseph as swe
import pytz
import pandas as pd
import math
import itertools
import matplotlib.pyplot as plt
from datetime import datetime
from geopy.geocoders import Nominatim

# Настройка страницы
st.set_page_config(page_title="Астро Процессор", page_icon="✨", layout="wide")
st.title("✨ Профессиональный Астро-Процессор")

# --- БАЗЫ ДАННЫХ И ПРАВИЛА ---
dignities = {
    "Солнце": {"Лев": ("Обитель", 5), "Овен": ("Экзальтация", 4), "Водолей": ("Изгнание", -5), "Весы": ("Падение", -4)},
    "Луна": {"Рак": ("Обитель", 5), "Телец": ("Экзальтация", 4), "Козерог": ("Изгнание", -5), "Скорпион": ("Падение", -4)},
    "Меркурий": {"Близнецы": ("Обитель", 5), "Дева": ("Обитель/Экзальт.", 5), "Стрелец": ("Изгнание", -5), "Рыбы": ("Изгн./Паден.", -5)},
    "Венера": {"Телец": ("Обитель", 5), "Весы": ("Обитель", 5), "Рыбы": ("Экзальтация", 4), "Скорпион": ("Изгнание", -5), "Овен": ("Изгнание", -5), "Дева": ("Падение", -4)},
    "Марс": {"Овен": ("Обитель", 5), "Скорпион": ("Обитель", 5), "Козерог": ("Экзальтация", 4), "Весы": ("Изгнание", -5), "Телец": ("Изгнание", -5), "Рак": ("Падение", -4)},
    "Юпитер": {"Стрелец": ("Обитель", 5), "Рыбы": ("Обитель", 5), "Рак": ("Экзальтация", 4), "Близнецы": ("Изгнание", -5), "Дева": ("Изгнание", -5), "Козерог": ("Падение", -4)},
    "Сатурн": {"Козерог": ("Обитель", 5), "Водолей": ("Обитель", 5), "Весы": ("Экзальтация", 4), "Рак": ("Изгнание", -5), "Лев": ("Изгнание", -5), "Овен": ("Падение", -4)}
}

zodiac_signs = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]
roman_nums = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
planets = {"Солнце": swe.SUN, "Луна": swe.MOON, "Меркурий": swe.MERCURY, "Венера": swe.VENUS, "Марс": swe.MARS, "Юпитер": swe.JUPITER, "Сатурн": swe.SATURN}
aspects_rules = {60: {"color": "green", "orb": 6}, 90: {"color": "red", "orb": 8}, 120: {"color": "blue", "orb": 8}, 180: {"color": "red", "orb": 8}}

# --- ИНТЕРФЕЙС ВВОДА ---
st.info("Введите данные рождения для расчета натальной карты")
col1, col2, col3 = st.columns(3)
with col1:
    b_date = st.date_input("Дата рождения", value=datetime(1990, 1, 1))
with col2:
    b_time = st.time_input("Время рождения", value=datetime.strptime("12:00", "%H:%M").time())
with col3:
    city_input = st.text_input("Город рождения", value="", placeholder="Например: Moscow")

tz_list = ["Europe/Moscow", "Europe/Minsk", "Asia/Yekaterinburg", "Europe/London", "America/New_York", "UTC"]
b_tz = st.selectbox("Выберите часовой пояс", tz_list, index=0)

if st.button("Рассчитать карту", type="primary"):
    if not city_input:
        st.warning("Пожалуйста, введите название города.")
    else:
        try:
            # Локация
            geolocator = Nominatim(user_agent="astro_app_v2")
            location = geolocator.geocode(city_input)
            if not location:
                st.error("Город не найден! Попробуйте написать на английском.")
                st.stop()
                
            lat, lon = location.latitude, location.longitude
            st.success(f"📍 Локация определена: {location.address}")

            # Расчет времени UTC
            local_tz = pytz.timezone(b_tz)
            local_dt = local_tz.localize(datetime.combine(b_date, b_time))
            utc_dt = local_dt.astimezone(pytz.UTC)
            jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)

            # Вычисления Домов и Планет
            houses_cusps, ascmc = swe.houses(jd, lat, lon, b'P')
            
            results = []
            planet_positions = {}
            for name, p_id in planets.items():
                res, _ = swe.calc_ut(jd, p_id)
                lon_p = res[0]
                planet_positions[name] = lon_p
                sign_index = int(lon_p / 30)
                degree_in_sign = lon_p % 30
                current_sign = zodiac_signs[sign_index]
                status, power = dignities.get(name, {}).get(current_sign, ("Перегрин", 0))
                results.append({"Планета": name, "Знак": current_sign, "Градус": f"{int(degree_in_sign)}° {int((degree_in_sign % 1) * 60)}'", "Статус": status, "Баллы": power})

            houses_data = []
            for i in range(12):
                cusp_deg = houses_cusps[i]
                sign_idx = int(cusp_deg / 30)
                deg_in_sign = cusp_deg % 30
                houses_data.append({"Дом": f"Дом {roman_nums[i+1]}", "Знак": zodiac_signs[sign_idx], "Градус": f"{int(deg_in_sign)}° {int((deg_in_sign % 1) * 60)}'"})

            # --- ОТРИСОВКА КАРТЫ ---
            fig, ax = plt.subplots(figsize=(8, 8), facecolor='#f0f2f6')
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Круги
            ax.add_patch(plt.Circle((0, 0), 10, color='navy', fill=False, linewidth=2))
            ax.add_patch(plt.Circle((0, 0), 7, color='navy', fill=False, linewidth=1))
            
            # Знаки зодиака
            for i in range(12):
                angle = math.radians(i * 30)
                ax.plot([7 * math.cos(angle), 10 * math.cos(angle)], [7 * math.sin(angle), 10 * math.sin(angle)], color='gray', alpha=0.3)
                a_text = math.radians(i * 30 + 15)
                ax.text(8.5 * math.cos(a_text), 8.5 * math.sin(a_text), zodiac_signs[i][:3], ha='center', va='center', fontsize=10, fontweight='bold')

            # Сетки домов
            for i in range(12):
                cusp_angle = math.radians(houses_cusps[i])
                ax.plot([3.5 * math.cos(cusp_angle), 10 * math.cos(cusp_angle)], [3.5 * math.sin(cusp_angle), 10 * math.sin(cusp_angle)], color='black', linewidth=1, linestyle='--')
                l_angle = math.radians(houses_cusps[i] + 3)
                ax.text(4 * math.cos(l_angle), 4 * math.sin(l_angle), roman_nums[i+1], fontsize=9, fontweight='bold')

            # Линии ASC/MC
            asc_angle = math.radians(ascmc[0])
            ax.plot([0, 10 * math.cos(asc_angle)], [0, 10 * math.sin(asc_angle)], color='red', linewidth=2.5, label='ASC')
            
            # Аспекты
            for (p1, lon1), (p2, lon2) in itertools.combinations(planet_positions.items(), 2):
                diff = abs(lon1 - lon2)
                if diff > 180: diff = 360 - diff
                for t_angle, props in aspects_rules.items():
                    if abs(diff - t_angle) <= props["orb"]:
                        a1, a2 = math.radians(lon1), math.radians(lon2)
                        ax.plot([6.5 * math.cos(a1), 6.5 * math.cos(a2)], [6.5 * math.sin(a1), 6.5 * math.sin(a2)], color=props["color"], alpha=0.4)

            # Планеты на круге
            for name, lon_p in planet_positions.items():
                angle = math.radians(lon_p)
                ax.plot(6.5 * math.cos(angle), 6.5 * math.sin(angle), 'o', color='crimson', markersize=8)
                ax.text(5.5 * math.cos(angle), 5.5 * math.sin(angle), name[:3], ha='center', fontsize=8, fontweight='bold')

            # Вывод таблиц
            col_img, col_tables = st.columns([1.5, 1])
            with col_img:
                st.pyplot(fig)
            with col_tables:
                st.subheader("Планеты")
                st.dataframe(pd.DataFrame(results), hide_index=True)
                st.subheader("Дома")
                st.dataframe(pd.DataFrame(houses_data), hide_index=True)

        except Exception as e:
            st.error(f"Произошла ошибка: {e}")
