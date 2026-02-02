import os
import shutil
from pathlib import Path
from colorama import init, Fore, Back, Style

# Инициализация colorama для работы с цветами в консоли
init(autoreset=True)

# Словарь для соответствия ключевых слов в именах файлов и папок назначения
FOLDER_MAPPING = {
    "Direct": "Direct",
    "Reflect": "Reflect",
    "Refract": "Refract",
    "ZDepth": "ZDepth",
    "CTexmap": "Ambient Occlusion",
    "CMasking": "CMasking",
    "WireColor": "WireColor",
    "Alpha": "Alpha",
    "SourceColor": "SourceColor",
    "CESSENTIAL": "Essential",
    "CShading": "Shading"
}

def create_folders(base_folder):
    """Создает все необходимые подпапки в папке 'Слои'"""
    layers_folder = os.path.join(base_folder, "Слои")
    os.makedirs(layers_folder, exist_ok=True)
    
    for folder_name in FOLDER_MAPPING.values():
        folder_path = os.path.join(layers_folder, folder_name)
        os.makedirs(folder_path, exist_ok=True)
    
    return layers_folder

def get_target_folder(file_name, layers_folder):
    """Определяет в какую подпапку нужно переместить файл"""
    for keyword, folder_name in FOLDER_MAPPING.items():
        if f"_{keyword}_" in file_name or keyword in file_name:
            return os.path.join(layers_folder, folder_name)
    return None

def print_header():
    """Красивое оформление заголовка"""
    print(Fore.YELLOW + "=============================================")
    print(Fore.CYAN + "   Организатор файлов рендера из 3ds Max")
    print(Fore.YELLOW + "=============================================")
    print(Style.RESET_ALL)

def print_footer(moved_files):
    """Красивое оформление завершения работы"""
    print(Fore.YELLOW + "\n=============================================")
    if moved_files > 0:
        print(Fore.GREEN + f" Готово! Перемещено файлов: {moved_files}")
    else:
        print(Fore.BLUE + " Ничего не перемещено - все файлы уже на своих местах!")
    print(Fore.YELLOW + "=============================================")
    print(Style.RESET_ALL)

def organize_files(source_folder):
    """Основная функция для организации файлов"""
    layers_folder = create_folders(source_folder)
    moved_files = 0
    
    print(Fore.BLUE + f"\nОбрабатываю папку: {source_folder}")
    print(Fore.MAGENTA + f"Папка для слоев: {layers_folder}\n")
    
    for file_name in os.listdir(source_folder):
        file_path = os.path.join(source_folder, file_name)
        
        # Пропускаем папки и системные файлы
        if os.path.isdir(file_path) or file_name.startswith('.'):
            continue
            
        target_folder = get_target_folder(file_name, layers_folder)
        
        if target_folder:
            try:
                shutil.move(file_path, os.path.join(target_folder, file_name))
                moved_files += 1
                print(Fore.GREEN + f"Успех: " + Style.RESET_ALL + 
                      f"{file_name} -> {os.path.relpath(target_folder, source_folder)}")
            except Exception as e:
                print(Fore.RED + f"Ошибка при перемещении {file_name}: {e}")
    
    print_footer(moved_files)

def main():
    print_header()
    
    # Запрашиваем путь к папке
    while True:
        folder_path = input(Fore.CYAN + "Введите путь к папке с рендерами: " + Style.RESET_ALL).strip()
        
        if os.path.isdir(folder_path):
            break
        else:
            print(Fore.RED + "Ошибка: Папка не найдена. Пожалуйста, введите правильный путь.")
    
    organize_files(folder_path)

    # Пауза перед закрытием (актуально для Windows)
    if os.name == 'nt':
        input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()