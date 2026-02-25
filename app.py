import streamlit as st
import swisseph as swe
import pytz
import pandas as pd
import math
import matplotlib.pyplot as plt
from datetime import datetime
from geopy.geocoders import Nominatim

# Попробуем импортировать маску, если не выйдет - используем обычный ввод с подсказкой
try:
    from streamlit_masked_text_input import masked_text_input
    HAS_MASK = True
except:
    HAS_MASK = False

st.set_page_config(page_title="Астро Процессор", layout="wide")
st.title("✨ Профессиональный Астро-Ввод")

st.markdown("### Введите данные (только цифры)")

col1, col2, col3 = st.columns(3)

with col1:
    if HAS_MASK:
        date_str = masked_text_input("Дата рождения", mask="11.11.1111", value="01.01.1990")
    else:
        date_str = st.text_input("Дата (ДД.ММ.ГГГГ)", "01.01.1990")

with col2:
    if HAS_MASK:
        time_str = masked_text_input("Время рождения", mask="11:11", value="12:00")
    else:
        time_str = st.text_input("Время (ЧЧ:ММ)", "12:00")

with col3:
    city_input = st.text_input("Город (лат.)", "Moscow")

# Список популярных поясов (чтобы не мотать весь мир)
common_tz = ["Europe/Moscow", "Europe/London", "Asia/Baku", "Asia/Tbilisi", "UTC"]
b_tz = st.selectbox("Часовой пояс", common_tz)

if st.button("Рассчитать", type="primary"):
    try:
        # Очистка данных на случай лишних пробелов
        d_clean = date_str.strip()
        t_clean = time_str.strip()
        
        b_date = datetime.strptime(d_clean, "%d.%m.%Y")
        b_time = datetime.strptime(t_clean, "%H:%M").time()

        # Геолокация
        geolocator = Nominatim(user_agent="astro_final")
        loc = geolocator.geocode(city_input)
        if not loc:
            st.error("Город не найден!")
            st.stop()

        # Расчет
        local_tz = pytz.timezone(b_tz)
        dt = local_tz.localize(datetime.combine(b_date, b_time))
        utc_dt = dt.astimezone(pytz.UTC)
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour + utc_dt.minute/60.0)

        # Вывод результата (упрощенно для примера)
        res, _ = swe.calc_ut(jd, swe.SUN)
        st.success(f"Солнце в момент рождения находилось в {int(res[0]%30)}° знака номер {int(res[0]/30)+1}")
        
    except Exception as e:
        st.error(f"Ошибка! Убедитесь, что ввели дату как 01.01.1990 и время как 12:00. Текст ошибки: {e}")
