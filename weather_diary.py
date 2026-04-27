
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
from datetime import datetime

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Дневник погоды")
        self.root.geometry("850x650")

        self.data_file = "weather_data.json"
        self.records = self.load_data()

        # --- Фреймы ---
        input_frame = ttk.LabelFrame(root, text="Добавить запись", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        filter_frame = ttk.LabelFrame(root, text="Фильтрация", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tree_frame = ttk.Frame(root, padding=10)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # --- Поля ввода ---
        ttk.Label(input_frame, text="Дата:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = DateEntry(input_frame, width=12, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.temp_entry = ttk.Entry(input_frame, width=8)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Описание:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.desc_entry = ttk.Entry(input_frame, width=30)
        self.desc_entry.grid(row=0, column=5, padx=5, pady=5)

        self.precipitation_var = tk.StringVar(value="Нет")
        ttk.Label(input_frame, text="Осадки:").grid(row=0, column=6, padx=5, pady=5, sticky="w")
        prec_menu = ttk.Combobox(input_frame, textvariable=self.precipitation_var, values=["Нет", "Да"], width=5, state="readonly")
        prec_menu.grid(row=0, column=7, padx=5, pady=5)
        
        add_button = ttk.Button(input_frame, text="Добавить", command=self.add_record)
        add_button.grid(row=0, column=8, padx=10, pady=5)

        # --- Фильтры ---
        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=0, padx=5, pady=5)
        self.date_filter = DateEntry(filter_frame, width=12, date_pattern='yyyy-mm-dd')
        self.date_filter.grid(row=0, column=1, padx=5)
        self.date_filter.set_date(None) # По умолчанию пусто

        ttk.Label(filter_frame, text="Температура выше (°C):").grid(row=0, column=2, padx=5, pady=5)
        self.temp_filter_entry = ttk.Entry(filter_frame, width=8)
        self.temp_filter_entry.grid(row=0, column=3, padx=5)

        filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_button.grid(row=0, column=4, padx=10, pady=5)

        reset_button = ttk.Button(filter_frame, text="Сбросить все", command=self.reset_filters)
        reset_button.grid(row=0, column=5, padx=5, pady=5)

        # --- Таблица ---
        self.tree = ttk.Treeview(tree_frame, columns=("date", "temp", "desc", "prec"), show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура (°C)")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("prec", text="Осадки")

        self.tree.column("date", width=100, anchor=tk.CENTER)
        self.tree.column("temp", width=120, anchor=tk.CENTER)
        self.tree.column("desc", width=300)
        self.tree.column("prec", width=80, anchor=tk.CENTER)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.populate_table(self.records)

    def add_record(self):
        date = self.date_entry.get()
        temp_str = self.temp_entry.get()
        desc = self.desc_entry.get().strip()
        precipitation = self.precipitation_var.get()

        if not desc:
            messagebox.showerror("Ошибка ввода", "Описание погоды не может быть пустым.")
            return
        try:
            temp = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Температура должна быть числом.")
            return
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Неверный формат даты.")
            return

        new_record = {"date": date, "temp": temp, "desc": desc, "precipitation": precipitation}
        self.records.append(new_record)
        self.save_data()
        self.apply_filter()

        # Очистка полей
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)

    def populate_table(self, records_to_show):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        sorted_records = sorted(records_to_show, key=lambda x: x['date'], reverse=True)
        for record in sorted_records:
            self.tree.insert("", tk.END, values=(record["date"], f"{record['temp']:.1f}", record["desc"], record["precipitation"]))

    def apply_filter(self):
        date_str = self.date_filter.get()
        temp_limit_str = self.temp_filter_entry.get()

        filtered_data = self.records

        if date_str:
            try:
                filter_date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
                filtered_data = [r for r in filtered_data if r['date'] == filter_date]
            except ValueError:
                messagebox.showwarning("Фильтр", "Некорректный формат даты для фильтра. Фильтр по дате не применен.")

        if temp_limit_str:
            try:
                temp_limit = float(temp_limit_str)
                filtered_data = [r for r in filtered_data if r['temp'] > temp_limit]
            except ValueError:
                messagebox.showwarning("Фильтр", "Температура для фильтра должна быть числом. Фильтр по температуре не применен.")

        self.populate_table(filtered_data)

    def reset_filters(self):
        self.date_filter.set_date(None)
        self.temp_filter_entry.delete(0, tk.END)
        self.populate_table(self.records)

    def load_data(self):
        if not os.path.exists(self.data_file):
            return []
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.records, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
