import json
from datetime import datetime
import flet as ft

# Базовые данные приложения
data = {
    "last_mileage": 195789,
    "last_mileage_date": "2026-01-16",
    "avg_daily_km": 15.0,
    "schedule": {
        "Масло в двигателе": {"target_km": 198871, "target_date": None},
        "Ремень ГРМ, ролик, помпа": {"target_km": 220090, "target_date": None},
        "Тосол (Антифриз)": {"target_km": None, "target_date": "2026-10-01"},
        "Тормозная жидкость": {"target_km": None, "target_date": "2028-06-01"}
    }
}

def main(page: ft.Page):
    page.title = "Авто-Регламент"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    # Текстовые метки
    mileage_label = ft.Text(value=f"Текущий пробег: {data['last_mileage']} км", size=22, weight=ft.FontWeight.BOLD)
    date_label = ft.Text(value=f"Обновлено: {data['last_mileage_date']}", size=14, color=ft.Colors.GREY_500)
    
    input_mileage = ft.TextField(
        hint_text="Новый пробег", 
        keyboard_type=ft.KeyboardType.NUMBER, 
        expand=True
    )
    
    reminders_container = ft.Column(spacing=12, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    def update_ui():
        mileage_label.value = f"Текущий пробег: {data['last_mileage']} км"
        date_label.value = f"Обновлено: {data['last_mileage_date']}"
        reminders_container.controls.clear()
        
        current_date = datetime.now()
        current_km = data["last_mileage"]
        avg_km = data["avg_daily_km"]
        
        for task, info in data["schedule"].items():
            remaining_days = None
            
            if info["target_km"]:
                km_left = info["target_km"] - current_km
                remaining_days = km_left / avg_km if avg_km > 0 else 0
            
            if info["target_date"]:
                days_by_date = (datetime.strptime(info["target_date"], "%Y-%m-%d") - current_date).days
                if remaining_days is None or days_by_date < remaining_days:
                    remaining_days = days_by_date

            days_to_show = int(remaining_days)

            if days_to_show <= 0:
                bg_color = ft.Colors.RED_900
                prefix = "[ СРОЧНО ] "
            elif days_to_show <= 14:
                bg_color = ft.Colors.ORANGE_800
                prefix = "[ ! ] "
            else:
                bg_color = ft.Colors.BLUE_950
                prefix = "[ OK ] "

            reminders_container.controls.add(
                ft.Container(
                    content=ft.Text(
                        value=f"{prefix}{task}\nОсталось: {days_to_show} дн.", 
                        text_align=ft.TextAlign.CENTER, 
                        size=16
                    ),
                    bgcolor=bg_color,
                    padding=15,
                    border_radius=10,
                    alignment=ft.alignment.center
                )
            )
        page.update()

    def save_mileage(e):
        if not input_mileage.value: 
            return
        try:
            new_val = int(input_mileage.value)
        except ValueError:
            return
            
        if new_val >= data["last_mileage"]:
            last_date = datetime.strptime(data["last_mileage_date"], "%Y-%m-%d")
            days_passed = max(1, (datetime.now() - last_date).days)
            km_driven = new_val - data["last_mileage"]
            
            data["avg_daily_km"] = round((data["avg_daily_km"] + (km_driven / days_passed)) / 2, 2)
            if data["avg_daily_km"] <= 0:
                data["avg_daily_km"] = 1.0
                
            data["last_mileage"] = new_val
            data["last_mileage_date"] = datetime.now().strftime("%Y-%m-%d")
            
            input_mileage.value = ""
            update_ui()

    btn_save = ft.ElevatedButton(
        text="Сохранить",
        on_click=save_mileage,
        height=50
    )

    page.add(
        mileage_label,
        date_label,
        ft.Row([input_mileage, btn_save], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Text("Статус регламентных работ:", size=16, weight=ft.FontWeight.BOLD),
        reminders_container
    )
    
    update_ui()

# Запуск приложения в мобильном представлении
ft.app(target=main)
