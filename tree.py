import os
from pathlib import Path

def draw_tree(directory, prefix="", max_depth=None, current_depth=0):
    """
    Рисует красивое дерево файлов
    
    Args:
        directory: путь к директории
        prefix: префикс для отступов
        max_depth: максимальная глубина (None = без ограничений)
        current_depth: текущая глубина
    """
    if max_depth is not None and current_depth >= max_depth:
        return
    
    try:
        # Получаем список файлов и папок
        items = list(Path(directory).iterdir())
        # Сортируем: сначала папки, потом файлы
        items.sort(key=lambda x: (x.is_file(), x.name.lower()))
        
        for i, item in enumerate(items):
            # Определяем, последний ли это элемент
            is_last = i == len(items) - 1
            
            # Выбираем символы для рисования
            if is_last:
                branch = "└── "
                extension = "    "
            else:
                branch = "├── "
                extension = "│   "
            
            # Получаем иконку
            if item.is_dir():
                icon = "📁"
                name = item.name + "/"
            else:
                icon = get_file_icon(item.name)
                name = item.name
            
            # Выводим строку
            print(f"{prefix}{branch}{icon} {name}")
            
            # Если это папка, рекурсивно обходим её
            if item.is_dir():
                draw_tree(item, prefix + extension, max_depth, current_depth + 1)
                
    except PermissionError:
        print(f"{prefix}├── ❌ [Нет доступа]")
    except Exception as e:
        print(f"{prefix}├── ❌ [Ошибка: {e}]")

def get_file_icon(filename):
    """Возвращает иконку для файла по расширению"""
    ext = Path(filename).suffix.lower()
    
    icons = {
        '.py': '🐍',
        '.js': '🟨',
        '.html': '🌐',
        '.css': '🎨',
        '.json': '⚙️',
        '.txt': '📝',
        '.md': '📖',
        '.pdf': '📕',
        '.jpg': '🖼️',
        '.png': '🖼️',
        '.gif': '🎞️',
        '.zip': '📦',
        '.exe': '⚙️',
        '.bat': '⚙️',
        '.sh': '⚙️',
    }
    
    return icons.get(ext, '📄')

def print_tree(path=".", max_depth=None, title=None):
    """
    Главная функция для печати дерева
    
    Args:
        path: путь к директории (по умолчанию текущая)
        max_depth: максимальная глубина
        title: заголовок для дерева
    """
    directory = Path(path)
    
    if not directory.exists():
        print(f"❌ Путь не найден: {path}")
        return
    
    if not directory.is_dir():
        print(f"❌ Это не директория: {path}")
        return
    
    # Печатаем заголовок
    if title:
        print(f"\n🌳 {title}")
        print("=" * (len(title) + 3))
    
    # Печатаем корневую папку
    print(f"📁 {directory.name}/")
    
    # Печатаем дерево
    draw_tree(directory, "", max_depth)

# Примеры использования
if __name__ == "__main__":
    # Базовое использование - текущая папка
    print_tree()
    
    print("\n" + "="*50 + "\n")
    
    # С ограничением глубины
    print_tree(".", max_depth=2, title="Дерево с глубиной 2")
    
    print("\n" + "="*50 + "\n")
    
    # Конкретная папка (если она существует)
    if Path("Documents").exists():
        print_tree("Documents", max_depth=3, title="Папка Documents")
    else:
        print_tree(".", max_depth=1, title="Текущая папка (1 уровень)")