import os
import re
from collections import defaultdict
import frontmatter
from tqdm import tqdm

# ====================== НАСТРОЙКИ ======================
MAX_LINKS = 3                  # Макс. 3 ссылки на файл
MIN_SIMILARITY = 6             # Высокий порог сходства
BLACKLIST_FOLDERS = [          #
]

# ====================== ФУНКЦИИ ======================
def is_blacklisted(path):
    """Проверяет, нужно ли игнорировать файл."""
    return any(folder in path for folder in BLACKLIST_FOLDERS)

def extract_keywords(text):
    """Упрощенный сбор ключевых слов (только важные)."""
    words = re.findall(r'\b\w{4,}\b', text.lower())  # Слова от 4 букв
    stop_words = {"это", "как", "что", "который", "если"}
    return {word for word in words if word not in stop_words}

def process_notes(vault_path):
    """Анализирует заметки и возвращает топ-3 связи для каждой."""
    notes = {}
    for root, _, files in os.walk(vault_path):
        for file in tqdm(files, desc="Анализ заметок"):
            if not file.endswith(".md") or is_blacklisted(root):
                continue
                
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                notes[path] = extract_keywords(content)
    return notes

def find_best_links(notes):
    """Находит лучшие связи для каждой заметки."""
    links = defaultdict(list)
    paths = list(notes.keys())
    
    for i in tqdm(range(len(paths)), desc="Поиск связей"):
        for j in range(i+1, len(paths)):
            path1, path2 = paths[i], paths[j]
            common = notes[path1] & notes[path2]
            if len(common) >= MIN_SIMILARITY:
                links[path1].append((path2, len(common)))
                links[path2].append((path1, len(common)))
    
    # Сортируем и оставляем топ-3
    return {
        path: sorted(links[path], key=lambda x: -x[1])[:MAX_LINKS]
        for path in links
    }

def add_links(vault_path):
    """Добавляет ссылки в заметки."""
    notes = process_notes(vault_path)
    best_links = find_best_links(notes)
    
    for path, links in tqdm(best_links.items(), desc="Добавление ссылок"):
        with open(path, 'r+', encoding='utf-8') as f:
            content = f.read()
            if "## Автоматические связи" in content:
                continue  # Пропускаем уже обработанные
            
            if links:
                links_section = "\n\n## Автоматические связи\n" + "\n".join(
                    f"- [[{os.path.splitext(os.path.basename(link[0]))[0]}]]"
                    for link in links
                )
                f.seek(0, os.SEEK_END)
                f.write(links_section)

if __name__ == "__main__":
    vault_path = input("Введи путь к хранилищу Obsidian: ").strip('"')
    add_links(vault_path)
    print("Готово! Проверь раздел 'Автоматические связи' в заметках.")  