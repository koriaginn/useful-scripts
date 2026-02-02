import os
import re
import yaml
from collections import defaultdict
from tqdm import tqdm
import frontmatter

# ====================== НАСТРОЙКИ ======================
TARGET_FOLDER = ""  # Укажите полный путь к папке для анализа
MAX_LINKS = 5       # Макс. рекомендуемых ссылок на заметку
MIN_KEYWORD_LEN = 3 # Минимальная длина ключевого слова
TAG_WEIGHT = 3      # Вес тегов (выше = важнее)
TITLE_WEIGHT = 2    # Вес слов из названия файла

# ====================== ФУНКЦИИ ======================
def extract_keywords(text, note_name, tags=None):
    """Глубокий анализ текста с приоритетом тегов и заголовков."""
    if tags is None:
        tags = set()
    
    # Собираем ключевые слова с весами
    keywords = defaultdict(int)
    
    # 1. Теги (максимальный вес)
    for tag in tags:
        clean_tag = re.sub(r'[^\w]', '', str(tag).lower())
        if len(clean_tag) >= MIN_KEYWORD_LEN:
            keywords[clean_tag] += TAG_WEIGHT
    
    # 2. Слова из названия файла
    title_words = re.findall(r'\b\w{%d,}\b' % MIN_KEYWORD_LEN, note_name.lower())
    for word in title_words:
        keywords[word] += TITLE_WEIGHT
    
    # 3. Контент (обычный вес)
    words = re.findall(r'\b\w{%d,}\b' % MIN_KEYWORD_LEN, text.lower())
    for word in words:
        keywords[word] += 1
    
    return dict(keywords)

def scan_notes(folder_path):
    """Сканирует все заметки в целевой папке и подпапках."""
    notes = {}
    for root, _, files in os.walk(folder_path):
        for file in tqdm(files, desc=f"Сканирование {os.path.basename(root)}"):
            if not file.endswith('.md'):
                continue
                
            path = os.path.join(root, file)
            try:
                post = frontmatter.load(path)
                note_name = os.path.splitext(file)[0]
                tags = set(post.get('tags', []))
                
                notes[path] = {
                    'name': note_name,
                    'keywords': extract_keywords(post.content, note_name, tags),
                    'folder': os.path.relpath(root, folder_path)
                }
            except Exception as e:
                print(f"Ошибка в {file}: {e}")
    return notes

def find_similar_notes(notes):
    """Находит похожие заметки с продвинутым сравнением."""
    similarities = defaultdict(list)
    note_paths = list(notes.keys())
    
    for i in tqdm(range(len(note_paths)), desc="Поиск связей"):
        path1 = note_paths[i]
        data1 = notes[path1]
        
        for j in range(i+1, len(note_paths)):
            path2 = note_paths[j]
            data2 = notes[path2]
            
            # Сравниваем ключевые слова
            common_words = set(data1['keywords'].keys()) & set(data2['keywords'].keys())
            if not common_words:
                continue
                
            # Вычисляем взвешенную схожесть
            similarity = sum(
                data1['keywords'][word] + data2['keywords'][word]
                for word in common_words
            )
            
            # Бонус для файлов в одной подпапке
            if data1['folder'] == data2['folder']:
                similarity *= 1.2
                
            if similarity > 0:
                similarities[path1].append((path2, similarity))
                similarities[path2].append((path1, similarity))
    
    # Сортируем по убыванию схожести
    return {
        path: sorted(links, key=lambda x: -x[1])[:MAX_LINKS]
        for path, links in similarities.items()
    }

def add_recommendations(notes, similarities):
    """Добавляет рекомендации в заметки."""
    for path, links in tqdm(similarities.items(), desc="Обновление заметок"):
        if not links:
            continue
            
        with open(path, 'r+', encoding='utf-8') as f:
            content = f.read()
            
            # Удаляем старые рекомендации (если есть)
            content = re.sub(r'\n## Рекомендации\b.*?(?=\n## |\Z)', '', content, flags=re.DOTALL)
            
            # Формируем новые рекомендации
            recommendations = "\n\n## Рекомендации\n" + "\n".join(
                f"- [[{notes[link[0]]['name']}]] (сходство: {link[1]:.1f})"
                for link in links
            )
            
            # Записываем в конец файла
            f.seek(0, os.SEEK_END)
            f.write(recommendations)

if __name__ == "__main__":
    if not TARGET_FOLDER:
        TARGET_FOLDER = input("Введите путь к папке для анализа: ").strip('"')
    
    print(f"\n🔍 Анализ папки: {TARGET_FOLDER}")
    notes_data = scan_notes(TARGET_FOLDER)
    similar_notes = find_similar_notes(notes_data)
    add_recommendations(notes_data, similar_notes)
    
    print("\n✅ Готово! Проверьте раздел '## Рекомендации' в заметках.")