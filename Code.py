import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x500")
        
        # Файл для хранения данных
        self.data_file = "trainings.json"
        self.trainings = []
        
        # Загрузка данных из JSON
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
    
    def create_widgets(self):
        # Рамка для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавление тренировки", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поле Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5)
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Поле Тип тренировки
        ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, sticky="w", padx=5)
        self.type_combobox = ttk.Combobox(input_frame, values=["Бег", "Плавание", "Велосипед", "Силовая", "Йога"], width=15)
        self.type_combobox.grid(row=0, column=3, padx=5, pady=5)
        self.type_combobox.set("Бег")
        
        # Поле Длительность
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, sticky="w", padx=5)
        self.duration_entry = ttk.Entry(input_frame, width=15)
        self.duration_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка добавления
        add_btn = ttk.Button(input_frame, text="Добавить тренировку", command=self.add_training)
        add_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # Рамка для фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Фильтр по типу:").grid(row=0, column=0, padx=5)
        self.filter_type = ttk.Combobox(filter_frame, values=["Все", "Бег", "Плавание", "Велосипед", "Силовая", "Йога"], width=15)
        self.filter_type.grid(row=0, column=1, padx=5)
        self.filter_type.set("Все")
        self.filter_type.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())
        
        ttk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5)
        self.filter_date = ttk.Entry(filter_frame, width=15)
        self.filter_date.grid(row=0, column=3, padx=5)
        self.filter_date.bind("<KeyRelease>", lambda e: self.refresh_table())
        
        clear_filter_btn = ttk.Button(filter_frame, text="Очистить фильтры", command=self.clear_filters)
        clear_filter_btn.grid(row=0, column=4, padx=10)
        
        # Таблица для отображения тренировок
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создание таблицы с прокруткой
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(table_frame, columns=("date", "type", "duration"), show="headings", yscrollcommand=scrollbar.set)
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")
        self.tree.column("date", width=150)
        self.tree.column("type", width=200)
        self.tree.column("duration", width=150)
        self.tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Кнопка удаления
        delete_btn = ttk.Button(self.root, text="Удалить выбранную тренировку", command=self.delete_training)
        delete_btn.pack(pady=5)
    
    def validate_date(self, date_str):
        """Проверка корректности даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def add_training(self):
        """Добавление новой тренировки"""
        date = self.date_entry.get().strip()
        training_type = self.type_combobox.get()
        duration = self.duration_entry.get().strip()
        
        # Валидация
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return
        
        try:
            duration_min = float(duration)
            if duration_min <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
            return
        
        # Добавление тренировки
        training = {
            "date": date,
            "type": training_type,
            "duration": duration_min
        }
        self.trainings.append(training)
        self.save_data()
        self.refresh_table()
        
        # Очистка поля длительности
        self.duration_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", "Тренировка добавлена!")
    
    def delete_training(self):
        """Удаление выбранной тренировки"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления")
            return
        
        # Получение индекса выбранной тренировки
        for item in selected:
            item_text = self.tree.item(item, "values")
            # Поиск и удаление из списка
            for i, training in enumerate(self.trainings):
                if (training["date"] == item_text[0] and 
                    training["type"] == item_text[1] and 
                    str(training["duration"]) == item_text[2]):
                    del self.trainings[i]
                    break
        
        self.save_data()
        self.refresh_table()
        messagebox.showinfo("Успех", "Тренировка удалена!")
    
    def refresh_table(self):
        """Обновление таблицы с учетом фильтров"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение фильтров
        filter_type = self.filter_type.get()
        filter_date = self.filter_date.get().strip()
        
        # Фильтрация данных
        filtered_trainings = self.trainings.copy()
        
        if filter_type != "Все":
            filtered_trainings = [t for t in filtered_trainings if t["type"] == filter_type]
        
        if filter_date:
            filtered_trainings = [t for t in filtered_trainings if t["date"] == filter_date]
        
        # Сортировка по дате
        filtered_trainings.sort(key=lambda x: x["date"])
        
        # Добавление в таблицу
        for training in filtered_trainings:
            self.tree.insert("", "end", values=(training["date"], training["type"], training["duration"]))
    
    def clear_filters(self):
        """Очистка фильтров"""
        self.filter_type.set("Все")
        self.filter_date.delete(0, tk.END)
        self.refresh_table()
    
    def load_data(self):
        """Загрузка данных из JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.trainings = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.trainings = []
    
    def save_data(self):
        """Сохранение данных в JSON"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.trainings, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()
