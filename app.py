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
st.set_page_config(page_title="Astro Processor", layout="centered")

# --- 1. СПРАВОЧНИКИ ---
ZODIAC_SIGNS = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", 
                "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]
ROMAN_NUMS = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]

PLANETS_MAP = {
    "Солнце": swe.SUN, "Луна": swe.MOON, "Меркурий": swe.MERCURY, 
    "Венера": swe.VENUS, "Марс": swe.MARS, "Юпитер": swe.JUPITER, 
    "Сатурн": swe.SATURN, "Уран": swe.URANUS, "Нептун": swe.NEPTUNE, "Плутон": swe.PLUTO
}

DIGNITIES = {
    "Солнце": {"Лев": ("Обитель", 5), "Овен": ("Экзальтация", 4), "Водолей": ("Изгнание", -5), "Весы": ("Падение", -4)},
    "Луна": {"Рак": ("Обитель", 5), "Телец": ("Экзальтация", 4), "Козерог": ("Изгнание", -5), "Скорпион": ("Падение", -4)},
    "Меркурий": {"Близнецы": ("Обитель", 5), "Дева": ("Обитель/Экзальт.", 5), "Стрелец": ("Изгнание", -5), "Рыбы": ("Изгн./Паден.", -5)},
    "Венера": {"Телец": ("Обитель", 5), "Весы": ("Обитель", 5), "Рыбы": ("Экзальтация", 4), "Скорпион": ("Изгнание", -5), "Овен": ("Изгнание", -5), "Дева": ("Падение", -4)},
    "Марс": {"Овен": ("Обитель", 5), "Скорпион": ("Обитель", 5), "Козерог": ("Экзальтация", 4), "Весы": ("Изгнание", -5), "Телец": ("Изгнание", -5), "Рак": ("Падение", -4)},
    "Юпитер": {"Стрелец": ("Обитель", 5), "Рыбы": ("Обитель", 5), "Рак": ("Экзальтация", 4), "Близнецы": ("Изгнание", -5), "Дева": ("Изгнание", -5), "Козерог": ("Падение", -4)},
    "Сатурн": {"Козерог": ("Обитель", 5), "Водолей": ("Обитель", 5), "Весы": ("Экзальтация", 4), "Рак": ("Изгнание", -5), "Лев": ("Изгнание", -5), "Овен": ("Падение", -4)}
}

ASPECTS = {
    60: {"name": "Секстиль", "color": "green", "orb": 6},
    90: {"name": "Квадратура", "color": "red", "orb": 8},
    120: {"name": "Трин", "color": "blue", "orb": 8},
    180: {"name": "Оппозиция", "color": "red", "orb": 8},
    0: {"name": "Соединение", "color": "orange", "orb": 8}
}

# --- 2. ИНТЕРФЕЙС ---
st.title("✨ Astro-Processor v2.0")
st.subheader("Натальная карта (Septener + Outer)")

with st.expander("Ввод данных", expanded=True):
    col1, col2 = st.columns(2)
    input_date = col1.text_input("Дата (ДД.ММ.ГГГГ)", placeholder="01.01.2000")
    input_time = col2.text_input("Время (ЧЧ:ММ)", placeholder="12:00")
    
    city = st.text_input("Город (лат. или кир.)", placeholder="Moscow")
    tz_choice = st.selectbox("Часовой пояс", pytz.all_timezones, index=pytz.all_timezones.index("Europe/Moscow"))

if st.button("Рассчитать карту"):
    try:
        # Валидация даты и времени
        dt_str = f"{input_date} {input_time}"
        naive_dt = datetime.strptime(dt_str, "%d.%m.%Y %H:%M")
        
        # Геолокация
        geolocator = Nominatim(user_agent="my_astro_app")
        location = geolocator.geocode(city)
        if not location:
            st.error("Город не найден. Проверьте написание.")
            st.stop()
        
        lat, lon = location.latitude, location.longitude
        st.info(f"Координаты: {lat:.2f}, {lon:.2f}")

        # Работа со временем
        local_tz = pytz.timezone(tz_choice)
        local_dt = local_tz.localize(naive_dt)
        utc_dt = local_dt.astimezone(pytz.UTC)
        
        # Расчет Юлианского дня
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)

        # Дома (Плацидус)
        houses_cusps, ascmc = swe.houses(jd, lat, lon, b'P')

        # Планеты
        planet_data = []
        planet_positions = {}
        for name, p_id in PLANETS_MAP.items():
            res, _ = swe.calc_ut(jd, p_id)
            lon_deg = res[0]
            planet_positions[name] = lon_deg
            
            sign_idx = int(lon_deg / 30)
            deg_in_sign = lon_deg % 30
            sign_name = ZODIAC_SIGNS[sign_idx]
            
            status, score = "Перегрин", 0
            if name in DIGNITIES and sign_name in DIGNITIES[name]:
                status, score = DIGNITIES[name][sign_name]
                
            planet_data.append({
                "Планета": name, 
                "Знак": sign_name, 
                "Градус": f"{int(deg_in_sign)}° {int((deg_in_sign % 1) * 60)}'", 
                "Статус": status, 
                "Баллы": score
            })

        # --- 3. ВИЗУАЛИЗАЦИЯ (Matplotlib) ---
        fig, ax = plt.subplots(figsize=(8, 8), facecolor='white')
        ax.set_aspect('equal')
        ax.axis('off')

        # Зодиакальный круг
        ax.add_patch(plt.Circle((0, 0), 10, color='black', fill=False, linewidth=1.5))
        ax.add_patch(plt.Circle((0, 0), 7, color='black', fill=False, linewidth=0.8))

        # Сектора знаков
        for i in range(12):
            angle = math.radians(i * 30)
            ax.plot([7 * math.cos(angle), 10 * math.cos(angle)], [7 * math.sin(angle), 10 * math.sin(angle)], color='gray', lw=0.5)
            # Текст знаков
            txt_angle = math.radians(i * 30 + 15)
            ax.text(8.5 * math.cos(txt_angle), 8.5 * math.sin(txt_angle), ZODIAC_SIGNS[i][:3], 
                    ha='center', va='center', fontsize=8, fontweight='bold')

        # Сетки домов
        for i in range(12):
            c_angle = math.radians(houses_cusps[i])
            ax.plot([4 * math.cos(c_angle), 10 * math.cos(c_angle)], [4 * math.sin(c_angle), 10 * math.sin(c_angle)], 
                    color='blue', lw=0.7, ls='--')
            ax.text(3.5 * math.cos(c_angle), 3.5 * math.sin(c_angle), ROMAN_NUMS[i+1], color='blue', fontsize=7)

        # Аспекты
        for (p1, l1), (p2, l2) in itertools.combinations(planet_positions.items(), 2):
            diff = abs(l1 - l2)
            if diff > 180: diff = 360 - diff
            for target, props in ASPECTS.items():
                if abs(diff - target) <= props["orb"]:
                    r = 6.5
                    ax.plot([r * math.cos(math.radians(l1)), r * math.cos(math.radians(l2))],
                            [r * math.sin(math.radians(l1)), r * math.sin(math.radians(l2))],
                            color=props["color"], alpha=0.4, lw=1)

        # Планеты на карте
        for name, l in planet_positions.items():
            rad = math.radians(l)
            ax.plot(6.8 * math.cos(rad), 6.8 * math.sin(rad), 'o', color='darkred', markersize=6)
            ax.text(5.5 * math.cos(rad), 5.5 * math.sin(rad), name[:3], fontsize=8, ha='center')

        st.pyplot(fig)

        # --- 4. ТАБЛИЦЫ ---
        col_tab1, col_tab2 = st.columns(2)
        
        with col_tab1:
            st.write("**🪐 Планеты**")
            st.dataframe(pd.DataFrame(planet_data), hide_index=True)
            
        with col_tab2:
            st.write("**🏠 Дома (Placidus)**")
            houses_list = []
            for i in range(12):
                c = houses_cusps[i]
                houses_list.append({
                    "Дом": ROMAN_NUMS[i+1], 
                    "Знак": ZODIAC_SIGNS[int(c/30)], 
                    "Градус": f"{int(c%30)}°"
                })
            st.dataframe(pd.DataFrame(houses_list), hide_index=True)

    except ValueError:
        st.error("Ошибка формата! Введите дату как ДД.ММ.ГГГГ и время как ЧЧ:ММ")
    except Exception as e:
        st.error(f"Ошибка: {e}")
