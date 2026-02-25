import streamlit as st
import swisseph as swe
import pytz
import pandas as pd
import math
import itertools
import matplotlib.pyplot as plt
from datetime import datetime
from geopy.geocoders import Nominatim

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Астро-Процессор 2.0", layout="wide")
st.title("✨ Профессиональный Астро-Процессор")

# --- БАЗЫ ДАННЫХ ---
dignities = {
    "Солнце": {"Лев": ("Обитель", 5), "Овен": ("Экзальтация", 4), "Водолей": ("Изгнание", -5), "Весы": ("Падение", -4)},
    "Луна": {"Рак": ("Обитель", 5), "Телец": ("Экзальтация", 4), "Козерог": ("Изгнание", -5), "Скорпион": ("Падение", -4)},
    "Меркурий": {"Близнецы": ("Обитель", 5), "Дева": ("Обитель/Экзальт.", 5), "Стрелец": ("Изгнание", -5), "Рыбы": ("Изгн./Паден.", -5)},
    "Венера": {"Телец": ("Обитель", 5), "Весы": ("Обитель", 5), "Рыбы": ("Экзальтация", 4), "Скорпион": ("Изгнание", -5), "Овен": ("Изгнание", -5), "Дева": ("Падение", -4)},
    "Марс": {"Овен": ("Обитель", 5), "Скорпион": ("Обитель", 5), "Козерог": ("Экзальтация", 4), "Весы": ("Изгнание", -5), "Телец": ("Изгнание", -5), "Рак": ("Падение", -4)},
    "Юпитер": {"Стрелец": ("Обитель", 5), "Рыбы": ("Обитель", 5), "Рак": ("Экзальтация", 4), "Близнецы": ("Изгнание", -5), "Дева": ("Изгнание", -5), "Козерог": ("Падение", -4)},
    "Сатурн": {"Козерог": ("Обитель", 5), "Водолей": ("Обитель", 5), "Весы": ("Экзальтация", 4), "Рак": ("Изгнание", -5), "Лев": ("Изгнание", -5), "Овен": ("Падение", -4)}
}

zodiac_signs = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", 
                "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]
roman_nums = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]

planets_map = {
    "Солнце": swe.SUN, "Луна": swe.MOON, "Меркурий": swe.MERCURY, 
    "Венера": swe.VENUS, "Марс": swe.MARS, "Юпитер": swe.JUPITER, "Сатурн": swe.SATURN
}

aspects_rules = {
    0: {"name": "Соединение", "color": "orange", "orb": 8},
    60: {"name": "Секстиль", "color": "green", "orb": 6},
    90: {"name": "Квадратура", "color": "red", "orb": 8},
    120: {"name": "Трин", "color": "blue", "orb": 8},
    180: {"name": "Оппозиция", "color": "red", "orb": 8}
}

# --- ИНТЕРФЕЙС ВВОДА ---
with st.sidebar:
    st.header("📍 Данные рождения")
    birth_date = st.date_input("Дата", value=datetime(1900, 1, 1))
    birth_time = st.time_input("Время", value=datetime.strptime("23:20", "%H:%M").time())
    city = st.text_input("Город (на латинице)", "Moscow")
    tz_choice = st.selectbox("Часовой пояс", ["Europe/Moscow", "UTC", "Europe/London", "America/New_York"])

if st.button("🔮 Рассчитать натальную карту"):
    try:
        # 1. ГЕОПОЗИЦИЯ
        geolocator = Nominatim(user_agent="astro_app_v2")
        location = geolocator.geocode(city)
        lat, lon = (location.latitude, location.longitude) if location else (55.75, 37.61)
        
        # 2. ВРЕМЯ
        local_tz = pytz.timezone(tz_choice)
        local_dt = local_tz.localize(datetime.combine(birth_date, birth_time))
        utc_dt = local_dt.astimezone(pytz.UTC)
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)
        
        # 3. ДОМА И ПЛАНЕТЫ
        houses_cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        
        results = []
        planet_positions = {}
        for name, p_id in planets_map.items():
            res, _ = swe.calc_ut(jd, p_id)
            long = res[0]
            planet_positions[name] = long
            sign_idx = int(long / 30)
            deg_in_sign = long % 30
            status, power = "Перегрин", 0
            if name in dignities and zodiac_signs[sign_idx] in dignities[name]:
                status, power = dignities[name][zodiac_signs[sign_idx]]
            
            results.append({
                "Планета": name, "Знак": zodiac_signs[sign_idx], 
                "Градус": f"{int(deg_in_sign)}° {int((deg_in_sign % 1) * 60)}'", 
                "Статус": status, "Баллы": power
            })

        # 4. ОТРИСОВКА (Matplotlib)
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Зодиакальный круг
        ax.add_patch(plt.Circle((0, 0), 10, color='darkblue', fill=False, linewidth=2))
        for i in range(12):
            angle = math.radians(i * 30)
            ax.plot([8 * math.cos(angle), 10 * math.cos(angle)], [8 * math.sin(angle), 10 * math.sin(angle)], color='gray', alpha=0.3)
            ax.text(9 * math.cos(math.radians(i*30+15)), 9 * math.sin(math.radians(i*30+15)), zodiac_signs[i][:3], ha='center', va='center', fontsize=8)

        # Дома
        for i in range(12):
            c_angle = math.radians(houses_cusps[i])
            ax.plot([4 * math.cos(c_angle), 10 * math.cos(c_angle)], [4 * math.sin(c_angle), 10 * math.sin(c_angle)], 'k--', lw=0.5)

        # Аспекты
        for (p1, lon1), (p2, lon2) in itertools.combinations(planet_positions.items(), 2):
            diff = abs(lon1 - lon2)
            if diff > 180: diff = 360 - diff
            for target, props in aspects_rules.items():
                if abs(diff - target) <= props["orb"]:
                    a1, a2 = math.radians(lon1), math.radians(lon2)
                    ax.plot([7 * math.cos(a1), 7 * math.cos(a2)], [7 * math.sin(a1), 7 * math.sin(a2)], color=props["color"], alpha=0.4)

        # Планеты
        for name, lon in planet_positions.items():
            ang = math.radians(lon)
            ax.plot(7.5 * math.cos(ang), 7.5 * math.sin(ang), 'ro')
            ax.text(6.5 * math.cos(ang), 6.5 * math.sin(ang), name, fontsize=9, ha='center')

        st.pyplot(fig)

        # 5. ТАБЛИЦЫ
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🪐 Планеты")
            st.table(pd.DataFrame(results))
        with col2:
            st.subheader("🏠 Дома")
            h_list = [{"Дом": roman_nums[i+1], "Знак": zodiac_signs[int(houses_cusps[i]/30)]} for i in range(12)]
            st.table(pd.DataFrame(h_list))

    except Exception as e:
        st.error(f"Ошибка: {e}")
