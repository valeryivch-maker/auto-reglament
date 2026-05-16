import os
import json
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex

DATA_FILE = "car_service_data.json"

DEFAULT_DATA = {
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

class CarApp(App):
    def build(self):
        self.data = self.load_data()
        
        # Главный контейнер
        root = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Тексты пробега
        self.mileage_label = Label(text=f"Текущий пробег: {self.data['last_mileage']} км", font_size='20sp', bold=True, size_hint_y=None, height=40)
        self.date_label = Label(text=f"Обновлено: {self.data['last_mileage_date']}", font_size='14sp', color=get_color_from_hex("#aaaaaa"), size_hint_y=None, height=30)
        
        root.add_widget(self.mileage_label)
        root.add_widget(self.date_label)
        
        # Поле ввода и кнопка
        input_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        self.input_mileage = TextInput(hint_text="Новый пробег", input_filter='int', multiline=False, font_size='18sp')
        btn_save = Button(text="Сохранить", background_color=get_color_from_hex("#2196F3"), font_size='18sp')
        btn_save.bind(on_press=self.save_mileage)
        
        input_layout.add_widget(self.input_mileage)
        input_layout.add_widget(btn_save)
        root.add_widget(input_layout)
        
        root.add_widget(Label(text="Статус регламентных работ:", font_size='16sp', bold=True, size_hint_y=None, height=30, halign='left'))
        
        # Прокручиваемый список регламента
        scroll = ScrollView()
        self.reminders_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.reminders_container.bind(minimum_height=self.reminders_container.setter('height'))
        
        scroll.add_widget(self.reminders_container)
        root.add_widget(scroll)
        
        self.update_ui()
        return root

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return DEFAULT_DATA

    def update_ui(self):
        self.mileage_label.text = f"Текущий пробег: {self.data['last_mileage']} км"
        self.date_label.text = f"Обновлено: {self.data['last_mileage_date']}"
        self.reminders_container.clear_widgets()
        
        current_date = datetime.now()
        current_km = self.data["last_mileage"]
        avg_km = self.data["avg_daily_km"]
        
        for task, info in self.data["schedule"].items():
            remaining_days = None
            if info["target_km"]:
                km_left = info["target_km"] - current_km
                remaining_days = km_left / avg_km if km_left > 0 and avg_km > 0 else 0
            if info["target_date"]:
                days_by_date = (datetime.strptime(info["target_date"], "%Y-%m-%d") - current_date).days
                if remaining_days is None or days_by_date < remaining_days:
                    remaining_days = days_by_date

            # Цвет статуса
            bg_color = "#333333"
            prefix = "[ OK ] "
            if remaining_days <= 0:
                bg_color = "#8b0000"
                prefix = "[ СРОЧНО ] "
            elif remaining_days <= 14:
                bg_color = "#d97706"
                prefix = "[ ! ] "

            box = BoxLayout(orientation='vertical', padding=10, size_hint_y=None, height=70)
            btn_card = Button(text=f"{prefix}{task}\nОсталось: {int(remaining_days)} дн.", 
                              background_color=get_color_from_hex(bg_color),
                              background_normal='',
                              halign='center')
            box.add_widget(btn_card)
            self.reminders_container.add_widget(box)

    def save_mileage(self, instance):
        if not self.input_mileage.text: return
        new_val = int(self.input_mileage.text)
        if new_val >= self.data["last_mileage"]:
            last_date = datetime.strptime(self.data["last_mileage_date"], "%Y-%m-%d")
            days_passed = max(1, (datetime.now() - last_date).days)
            km_driven = new_val - self.data["last_mileage"]
            
            self.data["avg_daily_km"] = round((self.data["avg_daily_km"] + (km_driven / days_passed)) / 2, 2)
            self.data["last_mileage"] = new_val
            self.data["last_mileage_date"] = datetime.now().strftime("%Y-%m-%d")
            
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
                
            self.input_mileage.text = ""
            self.update_ui()

if __name__ == '__main__':
    CarApp().run()
