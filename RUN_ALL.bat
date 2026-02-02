@echo off
chcp 65001 >nul
color 0A
title 🚀 Меню запуска скриптов

:menu
cls
echo ========================================
echo        ВЫБЕРИТЕ СКРИПТ ДЛЯ ЗАПУСКА
echo ========================================
echo.
echo  1. 🛠️  Исправить экспорт WordPress
echo  2. 🎨  Организовать рендеры 3Ds Max
echo  3. 🔗  Найти связи в Obsidian
echo  4. 📄  Проанализировать markdown-файлы
echo  5. 📱  Обновить Telegram-канал
echo  6. 📊  Парсить каталог
echo  7. ℹ️  Показать справку по всем скриптам
echo  8. ❌  Выход
echo.
set /p choice="Выберите номер [1-8]: "

if "%choice%"=="1" (
    cd "01_WordPress_SimplyStatic"
    python repair_wordpress_export.py
    pause
    cd..
    goto menu
)

if "%choice%"=="2" (
    cd "02_3DsMax_Render_Organizer"
    call render_folders.bat
    cd..
    goto menu
)

if "%choice%"=="3" (
    cd "03_Obsidian_Linker"
    python find_obsidian_connections.py
    pause
    cd..
    goto menu
)

if "%choice%"=="4" (
    cd "04_Custom_Folder_Analyzer"
    python analyze_markdown_connections.py
    pause
    cd..
    goto menu
)

if "%choice%"=="5" (
    cd "05_Telegram_Channel_Updater"
    echo Запуск скриптов для Telegram...
    pause
    cd..
    goto menu
)

if "%choice%"=="6" (
    cd "06_Parsing_Catalog"
    echo Запуск парсеров каталога...
    pause
    cd..
    goto menu
)

if "%choice%"=="7" (
    start SCRIPTS_README.md
    goto menu
)

if "%choice%"=="8" exit

goto menu