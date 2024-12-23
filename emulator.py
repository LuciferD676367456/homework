import csv
import zipfile
from datetime import datetime
import tkinter as tk

# Глобальные переменные
config = {}
current_dir = "/"

# Загрузка конфигурационного файла
def load_config():
    global config
    with open("config.csv", mode="r") as file:
        reader = csv.DictReader(file)
        config = next(reader)

# Логирование действий
def log_action(action):
    with open(config["log_file"], mode="a") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp},{config['username']},{action}\n")

# Вывод меню команд
def show_help():
    return (
        "Список доступных команд:\n"
        "1. ls - Показать содержимое текущей директории.\n"
        "2. cd <путь> - Перейти в указанную директорию.\n"
        "3. echo <текст> - Вывести текст.\n"
        "4. wc <путь к файлу> - Подсчитать строки, слова и символы в файле.\n"
        "5. exit - Выйти из эмулятора.\n"
        "6. help - Показать это меню.\n"
    )

# GUI для запуска эмулятора
def start_emulator():
    load_config()
    emulator_window = tk.Toplevel()
    emulator_window.title("Эмулятор Shell")
    
    output_text = tk.Text(emulator_window, height=20, width=80)
    output_text.pack()
    
    def run_command():
        global current_dir
        command = input_entry.get()
        output_text.insert(tk.END, f"{config['username']}@{config['computer_name']}:{current_dir}$ {command}\n")
        try:
            if command == "help":
                output_text.insert(tk.END, show_help())
                log_action("help")
            elif command.startswith("ls"):
                with zipfile.ZipFile(config["vfs_path"], "r") as zip_file:
                    files = [f for f in zip_file.namelist() if f.startswith(current_dir)]
                    if not files:
                        output_text.insert(tk.END, "Нет файлов в текущей директории.\n")
                    else:
                        output_text.insert(tk.END, "\n".join(files) + "\n")
                log_action(f"ls {current_dir}")
            elif command.startswith("cd"):
                path = command.split(" ")[1]
                current_dir = path
                output_text.insert(tk.END, f"Переход в {current_dir}\n")
                log_action(f"cd {path}")
            elif command.startswith("echo"):
                text = " ".join(command.split(" ")[1:])
                output_text.insert(tk.END, text + "\n")
                log_action(f"echo {text}")
            elif command.startswith("wc"):
                try:
                    file_path = command.split(" ")[1]
                    with zipfile.ZipFile(config["vfs_path"], "r") as zip_file:
                        if file_path not in zip_file.namelist():
                            output_text.insert(tk.END, f"Ошибка: файл '{file_path}' не найден.\n")
                            log_action(f"wc {file_path} (файл не найден)")
                            return
                        
                        with zip_file.open(file_path) as file:
                            content = file.read().decode("utf-8")
                            lines = content.splitlines()
                            words = sum(len(line.split()) for line in lines)
                            chars = len(content)
                            result = f"Lines: {len(lines)}, Words: {words}, Characters: {chars}\n"
                            output_text.insert(tk.END, result)
                            log_action(f"wc {file_path}")
                except IndexError:
                    output_text.insert(tk.END, "Ошибка: не указан путь к файлу.\n")
                    log_action("wc (ошибка: путь не указан)")
                except Exception as e:
                    output_text.insert(tk.END, f"Ошибка: {str(e)}\n")
                    log_action(f"wc {file_path} (ошибка: {str(e)})")
            elif command == "exit":
                log_action("exit")
                output_text.insert(tk.END, "Выход из эмулятора.\n")
                emulator_window.destroy()
            else:
                output_text.insert(tk.END, "Команда не найдена. Введите 'help' для списка доступных команд.\n")
        except Exception as e:
            output_text.insert(tk.END, f"Ошибка: {str(e)}\n")
        
        input_entry.delete(0, tk.END)

    input_entry = tk.Entry(emulator_window, width=50)
    input_entry.pack()

    run_button = tk.Button(emulator_window, text="Выполнить команду", command=run_command)
    run_button.pack()

# Главный GUI для запуска эмулятора
def gui():
    root = tk.Tk()
    root.title("Эмулятор Shell")

    label = tk.Label(root, text="Эмулятор оболочки ОС")
    label.pack()

    start_button = tk.Button(root, text="Запустить эмулятор", command=start_emulator)
    start_button.pack()

    root.mainloop()

if __name__ == "__main__":
    gui()
