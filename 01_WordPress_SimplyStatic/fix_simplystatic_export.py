import os
import shutil
import re

def fix_simplystatic_export(export_folder):
    """
    Исправляет структуру файлов, экспортированных SimplyStatic с некорректными разделителями.
    Преобразует файлы типа 'cataloghallsindex.html' в папку catalog/halls/index.html
    """
    
    # Символ-разделитель, который использует плагин (кодовый пункт U+F05C)
    bad_separator = '\uf05c'
    
    # Счетчики для отчета
    processed_files = 0
    created_dirs = 0
    
    print(f"Начинаю обработку папки: {export_folder}")
    print(f"Ищу файлы с разделителем: {repr(bad_separator)}")
    print("-" * 50)
    
    # Рекурсивно проходим по всем файлам
    for root, dirs, files in os.walk(export_folder):
        for filename in files:
            # Проверяем, содержит ли имя файла проблемный разделитель
            if bad_separator in filename:
                # Полный путь к исходному файлу
                old_path = os.path.join(root, filename)
                
                # Разбиваем имя файла по проблемному разделителю
                parts = filename.split(bad_separator)
                
                # Последняя часть - это имя файла (например, index.html)
                new_filename = parts[-1]
                
                # Все остальные части - это путь к папкам
                dir_parts = parts[:-1]
                
                # Создаем новую структуру папок
                new_relative_path = os.path.join(*dir_parts) if dir_parts else ''
                new_full_path = os.path.join(root, new_relative_path, new_filename)
                
                # Создаем папки, если их нет
                if dir_parts:
                    os.makedirs(os.path.join(root, *dir_parts), exist_ok=True)
                    created_dirs += 1
                
                # Перемещаем файл
                shutil.move(old_path, new_full_path)
                processed_files += 1
                
                print(f"✓ Исправлено: {filename}")
                print(f"  → {new_relative_path}/{new_filename}")
    
    print("-" * 50)
    print(f"Готово! Обработано файлов: {processed_files}")
    print(f"Создано папок: {created_dirs}")
    
    # Удаляем пустые папки, которые могли остаться
    if processed_files > 0:
        print("\nОчистка пустых папок...")
        cleanup_empty_folders(export_folder)

def cleanup_empty_folders(folder):
    """Рекурсивно удаляет пустые папки"""
    removed = 0
    for root, dirs, files in os.walk(folder, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):  # Если папка пуста
                    os.rmdir(dir_path)
                    removed += 1
                    print(f"  Удалена пустая папка: {dir_path}")
            except (OSError, PermissionError):
                pass  # Пропускаем папки, которые нельзя удалить
    if removed > 0:
        print(f"Удалено пустых папок: {removed}")

def batch_rename_directories(folder):
    """
    Дополнительная функция: переименовывает папки, если нужно
    заменить разделитель в уже созданных папках
    """
    bad_separator = '\uf05c'
    renamed = 0
    
    for root, dirs, files in os.walk(folder, topdown=False):
        for dir_name in dirs:
            if bad_separator in dir_name:
                old_path = os.path.join(root, dir_name)
                new_dir_name = dir_name.replace(bad_separator, '/')
                new_path = os.path.join(root, new_dir_name)
                
                # Создаем структуру папок с нормальными разделителями
                os.makedirs(new_path, exist_ok=True)
                
                # Перемещаем содержимое
                for item in os.listdir(old_path):
                    shutil.move(
                        os.path.join(old_path, item),
                        os.path.join(new_path, item)
                    )
                
                # Удаляем старую папку
                try:
                    os.rmdir(old_path)
                    renamed += 1
                    print(f"✓ Переименована папка: {dir_name} → {new_dir_name}")
                except OSError:
                    print(f"⚠ Не удалось удалить папку: {old_path}")
    
    return renamed

if __name__ == "__main__":
    # Укажите путь к папке с экспортированными файлами
    # Например: "C:/xampp/htdocs/mysite/wp-content/uploads/simply-static/"
    export_path = input("Введите путь к папке с экспортированными файлами: ").strip()
    
    # Удалите кавычки, если пользователь их ввел
    export_path = export_path.strip('"').strip("'")
    
    if os.path.exists(export_path):
        print(f"Папка найдена: {export_path}")
        
        # Спрашиваем, нужно ли также переименовывать уже созданные папки
        choice = input("\nХотите также переименовать существующие папки с некорректными разделителями? (y/n): ").lower()
        
        if choice == 'y':
            print("\nПереименование папок...")
            renamed = batch_rename_directories(export_path)
            print(f"Переименовано папок: {renamed}")
        
        print("\nИсправление структуры файлов...")
        fix_simplystatic_export(export_path)
        
        print("\n" + "=" * 50)
        print("✅ Обработка завершена успешно!")
        print("Теперь файлы имеют правильную структуру папок.")
        
        # Показываем примеры исправленных файлов
        print("\nПримеры исправленных путей:")
        print("  Было: cataloghallsindex.html")
        print("  Стало: catalog/halls/index.html")
        print("  Было: furnituretv-pedestalsimgphoto.jpg")
        print("  Стало: furniture/tv-pedestals/img/photo.jpg")
    else:
        print(f"❌ Ошибка: папка '{export_path}' не существует!")
        print("Проверьте путь и попробуйте снова.")