import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Файл для хранения избранных
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()
        
        # Переменные
        self.search_var = tk.StringVar()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Привязка клавиши Enter к поиску
        self.root.bind('<Return>', lambda event: self.search_users())
    
    def create_widgets(self):
        # Верхняя панель с поиском
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Поиск пользователя GitHub:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        self.search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=40, font=("Arial", 10))
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.search_btn = ttk.Button(top_frame, text="🔍 Найти", command=self.search_users)
        self.search_btn.pack(side=tk.LEFT, padx=5)
        
        self.fav_btn = ttk.Button(top_frame, text="⭐ Избранное", command=self.show_favorites)
        self.fav_btn.pack(side=tk.LEFT, padx=5)
        
        # Основной контент
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Панель с результатами
        results_frame = ttk.LabelFrame(main_frame, text="Результаты поиска", padding="5")
        results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Список результатов с прокруткой
        self.results_listbox = tk.Listbox(results_frame, height=20, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_listbox.yview)
        self.results_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязка клика для показа деталей
        self.results_listbox.bind('<<ListboxSelect>>', self.on_result_select)
        
        # Панель деталей
        details_frame = ttk.LabelFrame(main_frame, text="Детали пользователя", padding="10")
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.details_text = tk.Text(details_frame, height=20, wrap=tk.WORD, font=("Arial", 10))
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
        # Кнопки действий
        actions_frame = ttk.Frame(details_frame)
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.add_fav_btn = ttk.Button(actions_frame, text="❤️ Добавить в избранное", command=self.add_to_favorites)
        self.add_fav_btn.pack(side=tk.LEFT, padx=5)
        
        self.remove_fav_btn = ttk.Button(actions_frame, text="💔 Удалить из избранного", command=self.remove_from_favorites)
        self.remove_fav_btn.pack(side=tk.LEFT, padx=5)
        
        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Хранилище результатов поиска
        self.search_results = []
        self.selected_user = None
    
    def validate_input(self):
        """Проверка корректности ввода"""
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Ошибка ввода", "Поле поиска не может быть пустым!")
            return None
        return query
    
    def search_users(self):
        """Поиск пользователей через GitHub API"""
        query = self.validate_input()
        if not query:
            return
        
        self.status_var.set("Поиск...")
        self.search_btn.config(state=tk.DISABLED)
        self.root.update()
        
        try:
            # GitHub API поиск пользователей
            url = f"https://api.github.com/search/users?q={query}&per_page=20"
            headers = {"Accept": "application/vnd.github.v3+json"}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.search_results = data.get("items", [])
                
                # Очистка списка
                self.results_listbox.delete(0, tk.END)
                
                if self.search_results:
                    for user in self.search_results:
                        login = user.get("login", "Unknown")
                        self.results_listbox.insert(tk.END, f"@{login}")
                    
                    self.status_var.set(f"Найдено пользователей: {len(self.search_results)}")
                else:
                    self.status_var.set("Пользователи не найдены")
                    messagebox.showinfo("Результат", "Пользователи не найдены")
            else:
                error_msg = f"Ошибка API: {response.status_code}"
                self.status_var.set(error_msg)
                messagebox.showerror("Ошибка", error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Ошибка соединения: {str(e)}"
            self.status_var.set(error_msg)
            messagebox.showerror("Ошибка", error_msg)
        finally:
            self.search_btn.config(state=tk.NORMAL)
    
    def on_result_select(self, event):
        """Обработка выбора пользователя из списка"""
        selection = self.results_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index < len(self.search_results):
            user_data = self.search_results[index]
            self.selected_user = user_data
            self.show_user_details(user_data.get("login"))
    
    def show_user_details(self, username):
        """Показ детальной информации о пользователе"""
        self.status_var.set(f"Загрузка данных о {username}...")
        self.details_text.delete(1.0, tk.END)
        
        try:
            url = f"https://api.github.com/users/{username}"
            headers = {"Accept": "application/vnd.github.v3+json"}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                user = response.json()
                
                # Форматирование информации
                details = f"""
╔══════════════════════════════════════════════════════════╗
║                  ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ               ║
╠══════════════════════════════════════════════════════════╣
║ Логин: {user.get('login', 'N/A')}
║ Имя: {user.get('name', 'N/A')}
║ Компания: {user.get('company', 'N/A')}
║ Email: {user.get('email', 'N/A')}
║ Местоположение: {user.get('location', 'N/A')}
║ Репозитории: {user.get('public_repos', 0)}
║ Подписчики: {user.get('followers', 0)}
║ Подписки: {user.get('following', 0)}
║ Создан: {user.get('created_at', 'N/A')[:10]}
║ Обновлён: {user.get('updated_at', 'N/A')[:10]}
║ Сайт: {user.get('blog', 'N/A')}
╠══════════════════════════════════════════════════════════╣
║ Профиль: {user.get('html_url', 'N/A')}
╚══════════════════════════════════════════════════════════╝
"""
                self.details_text.insert(1.0, details)
                self.status_var.set(f"Информация о {username} загружена")
                
                # Обновляем состояние кнопок избранного
                self.update_favorite_buttons(username)
            else:
                self.details_text.insert(1.0, f"Ошибка загрузки: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.details_text.insert(1.0, f"Ошибка соединения: {str(e)}")
            self.status_var.set("Ошибка соединения")
    
    def load_favorites(self):
        """Загрузка избранных из JSON файла"""
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_favorites(self):
        """Сохранение избранных в JSON файл"""
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)
    
    def is_favorite(self, username):
        """Проверка, находится ли пользователь в избранном"""
        return any(fav.get("login") == username for fav in self.favorites)
    
    def update_favorite_buttons(self, username):
        """Обновление состояния кнопок избранного"""
        if self.is_favorite(username):
            self.add_fav_btn.config(state=tk.DISABLED)
            self.remove_fav_btn.config(state=tk.NORMAL)
        else:
            self.add_fav_btn.config(state=tk.NORMAL)
            self.remove_fav_btn.config(state=tk.DISABLED)
    
    def add_to_favorites(self):
        """Добавление пользователя в избранное"""
        if not self.selected_user:
            messagebox.showwarning("Предупреждение", "Сначала выберите пользователя")
            return
        
        username = self.selected_user.get("login")
        
        if self.is_favorite(username):
            messagebox.showinfo("Информация", f"Пользователь @{username} уже в избранном")
            return
        
        # Сохраняем основную информацию о пользователе
        favorite_data = {
            "login": username,
            "name": self.selected_user.get("name", "N/A"),
            "avatar_url": self.selected_user.get("avatar_url", ""),
            "html_url": self.selected_user.get("html_url", ""),
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.favorites.append(favorite_data)
        self.save_favorites()
        
        self.status_var.set(f"@{username} добавлен в избранное")
        messagebox.showinfo("Успех", f"Пользователь @{username} добавлен в избранное")
        self.update_favorite_buttons(username)
    
    def remove_from_favorites(self):
        """Удаление пользователя из избранного"""
        if not self.selected_user:
            messagebox.showwarning("Предупреждение", "Сначала выберите пользователя")
            return
        
        username = self.selected_user.get("login")
        
        if not self.is_favorite(username):
            messagebox.showinfo("Информация", f"Пользователь @{username} не в избранном")
            return
        
        self.favorites = [fav for fav in self.favorites if fav.get("login") != username]
        self.save_favorites()
        
        self.status_var.set(f"@{username} удалён из избранного")
        messagebox.showinfo("Успех", f"Пользователь @{username} удалён из избранного")
        self.update_favorite_buttons(username)
    
    def show_favorites(self):
        """Показать окно с избранными пользователями"""
        fav_window = tk.Toplevel(self.root)
        fav_window.title("Избранные пользователи")
        fav_window.geometry("500x400")
        
        if not self.favorites:
            ttk.Label(fav_window, text="Нет избранных пользователей", font=("Arial", 12)).pack(expand=True)
            return
        
        # Создаём фрейм со списком
        list_frame = ttk.Frame(fav_window, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Список избранных
        fav_listbox = tk.Listbox(list_frame, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=fav_listbox.yview)
        fav_listbox.configure(yscrollcommand=scrollbar.set)
        
        for fav in self.favorites:
            fav_listbox.insert(tk.END, f"@{fav.get('login')} - {fav.get('added_at')}")
        
        fav_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка закрытия
        ttk.Button(fav_window, text="Закрыть", command=fav_window.destroy).pack(pady=10)

def main():
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()

if __name__ == "__main__":
    main()