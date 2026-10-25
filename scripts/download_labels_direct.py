import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Настройки
REPO_ID = "jhboyo/ppe-dataset"
REVISION = "main"  # или конкретный хеш коммита
LOCAL_DIR = "datasets/ppe_raw/train/labels"
BASE_URL = "https://huggingface.co"
# BASE_URL = "https://hf-mirror.com"  # если используете зеркало

# Диапазон номеров файлов (известно, что их около 9609)
# Можно уточнить, посмотрев на имена уже скачанных файлов
START_IDX = 0
END_IDX = 9609

os.makedirs(LOCAL_DIR, exist_ok=True)

# Настройка сессии requests с игнорированием системных прокси и повторными попытками
session = requests.Session()
session.trust_env = False  # игнорировать HTTP_PROXY, ALL_PROXY и т.д.
retries = Retry(total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

# Формируем имена файлов. Пример: ds1_hard_hat_workers0.txt
# В реальности имена могут быть разными (ds1_..., ds2_...), поэтому
# лучше сначала посмотреть на уже скачанные файлы.
# Для примера используем шаблон ds1_hard_hat_workers{idx}.txt
# Если имена другие, скрипт нужно будет адаптировать.

ok, fail = 0, 0
for i in range(START_IDX, END_IDX + 1):
    filename = f"ds1_hard_hat_workers{i}.txt"
    local_path = os.path.join(LOCAL_DIR, filename)
    if os.path.exists(local_path):
        continue  # уже скачан

    url = f"{BASE_URL}/datasets/{REPO_ID}/resolve/{REVISION}/train/labels/{filename}"
    for attempt in range(1, 4):
        try:
            resp = session.get(url, timeout=20)
            if resp.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(resp.content)
                ok += 1
                break
            elif resp.status_code == 404:
                # Файла с таким именем нет, пропускаем
                break
            else:
                time.sleep(2 * attempt)
        except Exception as e:
            if attempt == 3:
                fail += 1
                print(f"FAIL {filename}: {e}")
            else:
                time.sleep(2 * attempt)

    if i % 200 == 0:
        print(f"Проверено {i}, скачано {ok}, ошибок {fail}")

print(f"Готово. Скачано: {ok}, ошибок: {fail}")