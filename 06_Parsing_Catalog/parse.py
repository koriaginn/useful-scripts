import os
import io
import fitz  # PyMuPDF
from PIL import Image, ImageEnhance
import numpy as np

def extract_images_from_pdf(pdf_path, output_folder):
    """
    Улучшенная версия с исправлением ошибок обработки PNG
    """
    os.makedirs(output_folder, exist_ok=True)
    pdf_document = fitz.open(pdf_path)
    
    # Статистика
    success_count = 0
    error_count = 0
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        images = page.get_images(full=True)
        
        if not images:
            continue
            
        page_folder = os.path.join(output_folder, f"page_{page_num + 1}")
        os.makedirs(page_folder, exist_ok=True)
        
        for img_index, img in enumerate(images, start=1):
            xref = img[0]
            try:
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                ext = base_image["ext"].lower()
                
                # Нормализация расширений
                if ext == "jpeg":
                    ext = "jpg"
                elif ext not in ["png", "jpg", "jpeg"]:
                    ext = "png"  # Для неизвестных форматов
                
                image_path = os.path.join(page_folder, f"image_{img_index}.{ext}")
                
                # Простая запись файла без сложной обработки
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                
                # Только базовая проверка PNG
                if ext == "png":
                    try:
                        with Image.open(image_path) as img_pil:
                            if img_pil.mode not in ['RGBA', 'LA']:
                                # Конвертируем в RGBA если нет альфа-канала
                                img_pil.convert('RGBA').save(image_path)
                    except Exception as e:
                        print(f"⚠️ Минорная ошибка PNG (страница {page_num+1}): {str(e)}")
                        error_count += 1
                        continue
                
                success_count += 1
                print(f"✅ Успешно сохранено: {image_path}")
                
            except Exception as e:
                error_count += 1
                print(f"❌ Ошибка при обработке изображения {img_index} на странице {page_num+1}: {str(e)}")
                continue
    
    pdf_document.close()
    
    print(f"\nОтчёт:\nУспешно обработано: {success_count}\nОшибок: {error_count}")
    print(f"Результаты сохранены в: {os.path.abspath(output_folder)}")

# Ваши параметры
pdf_path = r"D:\~ Творчество\Программы\Готовые программы\Скрипты\Парсинг каталога\catalog.pdf"
output_folder = "pdf_images_extracted"

# Запуск
extract_images_from_pdf(pdf_path, output_folder)