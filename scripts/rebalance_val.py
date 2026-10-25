"""
Перекидывает ~900 изображений из train в val для объединённого датасета.
Использует random seed для воспроизводимости.
"""
import random
import shutil
from pathlib import Path

COMBINED = Path("datasets/ppe_combined")
N_TO_MOVE = 900
SEED = 42

train_images = COMBINED / "images" / "train"
train_labels = COMBINED / "labels" / "train"
val_images = COMBINED / "images" / "val"
val_labels = COMBINED / "labels" / "val"

val_images.mkdir(parents=True, exist_ok=True)
val_labels.mkdir(parents=True, exist_ok=True)

# Все изображения из train
all_imgs = [p for p in train_images.iterdir()
            if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}]
print(f"В train сейчас: {len(all_imgs)} изображений")

# Случайная выборка
random.seed(SEED)
to_move = random.sample(all_imgs, N_TO_MOVE)
print(f"Перемещаю {len(to_move)} изображений в val...")

moved_ok, moved_no_label = 0, 0
for img in to_move:
    # перемещаем изображение
    dst_img = val_images / img.name
    shutil.move(str(img), str(dst_img))

    # перемещаем метку
    src_lbl = train_labels / (img.stem + ".txt")
    dst_lbl = val_labels / (img.stem + ".txt")
    if src_lbl.exists():
        shutil.move(str(src_lbl), str(dst_lbl))
        moved_ok += 1
    else:
        moved_no_label += 1

print(f"Перемещено: {moved_ok} (с меткой), {moved_no_label} (без метки — hard negatives)")

print("\n=== Итог ===")
for split in ["train", "val", "test"]:
    n_img = len(list((COMBINED / "images" / split).iterdir()))
    n_lbl = len(list((COMBINED / "labels" / split).iterdir()))
    status = "OK" if n_img == n_lbl else "MISMATCH!"
    print(f"  {split}: images={n_img}, labels={n_lbl} — {status}")