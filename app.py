# --- УЛУЧШЕННАЯ ОТРИСОВКА КАРТЫ ---
def draw_premium_chart(planet_pos, houses_cusps, zodiac_signs):
    # Угол поворота: чтобы ASC (1-й дом) всегда был слева (180 градусов на круге)
    asc_angle = houses_cusps[0]
    def normalize(angle):
        return (angle - asc_angle + 180) % 360

    fig, ax = plt.subplots(figsize=(10, 10), facecolor='#f0f2f6')
    ax.set_aspect('equal')
    ax.axis('off')

    # Внешний круг (Зодиак)
    ax.add_patch(plt.Circle((0, 0), 10, color='#2c3e50', fill=False, lw=2))
    
    # Сектора знаков (вращаем их вместе с картой)
    for i in range(12):
        start_angle = normalize(i * 30)
        end_angle = normalize((i + 1) * 30)
        
        # Линии раздела знаков
        rad = math.radians(start_angle)
        ax.plot([8.5 * math.cos(rad), 10 * math.cos(rad)], [8.5 * math.sin(rad), 10 * math.sin(rad)], color='#bdc3c7', lw=1)
        
        # Текст знаков (по центру сектора)
        mid_rad = math.radians(normalize(i * 30 + 15))
        ax.text(9.2 * math.cos(mid_rad), 9.2 * math.sin(mid_rad), zodiac_signs[i][:3], 
                ha='center', va='center', fontsize=9, fontweight='bold', color='#34495e', rotation=math.degrees(mid_rad)-90 if abs(math.degrees(mid_rad))>90 else math.degrees(mid_rad)+90)

    # Отрисовка домов
    for i in range(12):
        house_angle = normalize(houses_cusps[i])
        rad = math.radians(house_angle)
        # Куспиды домов
        line_style = '-' if i in [0, 3, 6, 9] else '--' # Углы карты — сплошные
        line_width = 2 if i in [0, 3, 6, 9] else 0.7
        ax.plot([0, 8.5 * math.cos(rad)], [0, 8.5 * math.sin(rad)], color='#3498db', lw=line_width, ls=line_style, alpha=0.6)
        
        # Номера домов
        txt_rad = math.radians(house_angle + 2) # чуть смещаем номер от линии
        ax.text(4.0 * math.cos(txt_rad), 4.0 * math.sin(txt_rad), ROMAN_NUMS[i+1], color='#2980b9', fontsize=10, fontweight='bold')

    # Планеты (с защитой от наслоения)
    sorted_planets = sorted(planet_pos.items(), key=lambda x: x[1])
    for i, (name, lon) in enumerate(sorted_planets):
        angle = normalize(lon)
        rad = math.radians(angle)
        
        # Динамический радиус для близких планет (чтобы не слипались)
        r = 7.0 if i % 2 == 0 else 7.8 
        
        ax.plot(8.5 * math.cos(rad), 8.5 * math.sin(rad), 'o', color='#e74c3c', markersize=8)
        ax.text(r * math.cos(rad), r * math.sin(rad), name, ha='center', fontsize=9, fontweight='bold', 
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))

    plt.title("Натальная карта (Ориентация по ASC)", fontsize=15, pad=20)
    return fig

# В основном коде вызывай:
# fig = draw_premium_chart(planet_positions, houses_cusps, zodiac_signs)
# st.pyplot(fig)
