import streamlit as st
import swisseph as swe
import pytz
import pandas as pd
import math
import matplotlib.pyplot as plt
from datetime import datetime
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Астро Процессор", layout="wide")
st.title("✨ Профессиональный Астро-Ввод")

st.info("Просто введите цифры. Формат даты: ДД.ММ.ГГГГ, Формат времени: ЧЧ:ММ")

col1, col2, col3 = st.columns(3)

with col1:
    # Поле с примером, который исчезает при вводе
    date_str = st.text_input("Дата рождения", placeholder="01.01.1990", value="07.06.1979")

with col2:
    # Поле с примером времени
    time_str = st.text_input("Время рождения", placeholder="12:00", value="23:20")

with col3:
    city_input = st.text_input("Город (латиницей)", value="Izberbash")

# Авто-выбор пояса для удобства
common_tz = sorted(pytz.all_timezones)
try:
    idx = common_tz.index("Europe/Moscow")
except:
    idx = 0
b_tz = st.selectbox("Часовой пояс", common_tz, index=idx)

if st.button("Рассчитать карту", type="primary"):
    try:
        # Убираем возможные пробелы, которые могли вкрасться при копировании
        d_clean = date_str.replace(" ", "")
        t_clean = time_str.replace(" ", "")
        
        birth_date = datetime.strptime(d_clean, "%d.%m.%Y")
        birth_time = datetime.strptime(t_clean, "%H:%M").time()

        geolocator = Nominatim(user_agent="astro_final_v3")
        location = geolocator.geocode(city_input)
        
        if not location:
            st.error("❌ Город не найден! Попробуйте написать по-английски.")
            st.stop()
        
        lat, lon = location.latitude, location.longitude
        
        # Настройка времени
        local_tz = pytz.timezone(b_tz)
        dt = local_tz.localize(datetime.combine(birth_date, birth_time))
        utc_dt = dt.astimezone(pytz.UTC)
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)

        # Краткий расчет для проверки
        res, _ = swe.calc_ut(jd, swe.SUN)
        st.success(f"✅ Расчет готов для {location.address}")
        st.balloons() # Маленький праздник в честь успеха
        
        st.write(f"Ваше Солнце в {int(res[0]%30)}° знака {['Овен','Телец','Близнецы','Рак','Лев','Дева','Весы','Скорпион','Стрелец','Козерог','Водолей','Рыбы'][int(res[0]/30)]}")

    except ValueError:
        st.error("❌ Ошибка формата! Проверьте, что дата введена через точки (07.06.1979), а время через двоеточие (23:20).")
    except Exception as e:
        st.error(f"Произошла ошибка: {e}")
