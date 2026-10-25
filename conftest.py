import sys
import os

# Добавляем корневую директорию проекта в sys.path, чтобы pytest видел модули из src/
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))