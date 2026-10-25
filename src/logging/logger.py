import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(log_file="logs/application.log", level=logging.INFO):
    os.makedirs("logs", exist_ok=True)
    
    # Формат логов: время | уровень | имя логгера | сообщение
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
    
    # Файловый обработчик с ротацией (5 МБ, храним 3 файла)
    handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(formatter)
    
    # Консольный обработчик (чтобы видеть логи и в терминале)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Очищаем старые хендлеры, чтобы не дублировать при повторном вызове
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.addHandler(handler)
    root_logger.addHandler(console_handler)