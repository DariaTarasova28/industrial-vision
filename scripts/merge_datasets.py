"""
Объединение ppe_ultra (11 классов) и ppe_raw (3 класса) в ppe_combined (4 класса).
Учитывает разную структуру папок у датасетов:
  ppe_ultra: images/train/  labels/train/  (images_first)
  ppe_raw:   train/images/  train/labels/  (split_first)
"""
import os
import shutil
from pathlib import Path

ROOT = Path("datasets")
ULTRA = ROOT / "ppe_ultra"
RAW = ROOT / "ppe_raw"
COMBINED = ROOT / "ppe_combined"

NEW_NAMES = {0: "helmet", 1: "vest", 2: "Person", 3: "no_helmet"}
NC = len(NEW_NAMES)

# Маппинг: старый class_id → новый class_id; None = пропустить
MAP_ULTRA = {0: 0, 2: 1, 6: 2, 7: 3, 1: None, 3: None, 4: None, 5: None, 8: None, 9: None, 10: None}
MAP_RAW = {0: 0, 1: 3, 2: 1}

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def get_dirs(dataset_root: Path, layout: str, split: str):
    """Возвращает (images_dir, labels_dir) в зависимости от layout."""
    if layout == "images_first":
        return dataset_root / "images" / split, dataset_root / "labels" / split
    else:  # split_first
        return dataset_root / split / "images", dataset_root / split / "labels"


def remap_label_file(src_label: Path, dst_label: Path, mapping: dict):
    if not src_label.exists():
        dst_label.write_text("")
        return 0
    lines_out = []
    for line in src_label.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if not parts:
            continue
        old_cls = int(parts[0])
        new_cls = mapping.get(old_cls, None)
        if new_cls is None:
            continue
        lines_out.append(" ".join([str(new_cls)] + parts[1:]))
    dst_label.write_text("\n".join(lines_out))
    return len(lines_out)


def merge_split(split: str):
    out_images = COMBINED / "images" / split
    out_labels = COMBINED / "labels" / split
    out_images.mkdir(parents=True, exist_ok=True)
    out_labels.mkdir(parents=True, exist_ok=True)

    total_img, total_lbl = 0, 0

    sources = [
        ("ultra", ULTRA, MAP_ULTRA, "images_first"),
        ("raw", RAW, MAP_RAW, "split_first"),
    ]

    for name, src, mapping, layout in sources:
        src_imgs, src_lbls = get_dirs(src, layout, split)
        if not src_imgs.exists():
            print(f"  [{name}/{split}] НЕТ папки {src_imgs}, пропускаю")
            continue

        cnt = 0
        for img in src_imgs.iterdir():
            if img.suffix.lower() not in IMAGE_EXTS:
                continue
            basename = img.stem
            new_name = f"{name}__{img.name}"
            new_basename = f"{name}__{basename}"
            dst_img = out_images / new_name
            dst_lbl = out_labels / (new_basename + ".txt")
            if dst_img.exists():
                continue
            shutil.copy(img, dst_img)
            remap_label_file(src_lbls / (basename + ".txt"), dst_lbl, mapping)
            cnt += 1
            total_img += 1
            total_lbl += 1
        print(f"  [{name}/{split}] скопировано {cnt} изображений из {src_imgs}")

    print(f"  Итого {split}: {total_img} images, {total_lbl} labels")


def main():
    if COMBINED.exists():
        print(f"{COMBINED} уже существует. Удаляю...")
        shutil.rmtree(COMBINED)

    for split in ["train", "val", "test"]:
        print(f"\nОбрабатываю {split}:")
        merge_split(split)

    yaml_path = COMBINED / "data.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(f"path: {COMBINED.resolve()}\n")
        f.write("train: images/train\n")
        f.write("val: images/val\n")
        f.write("test: images/test\n\n")
        f.write(f"nc: {NC}\n")
        f.write("names:\n")
        for i, name in NEW_NAMES.items():
            f.write(f"  {i}: {name}\n")
    print(f"\ndata.yaml создан: {yaml_path}")

    print("\n=== Проверка соответствия images/labels ===")
    for split in ["train", "val", "test"]:
        n_img = len(list((COMBINED / "images" / split).iterdir())) if (COMBINED / "images" / split).exists() else 0
        n_lbl = len(list((COMBINED / "labels" / split).iterdir())) if (COMBINED / "labels" / split).exists() else 0
        status = "OK" if n_img == n_lbl else "MISMATCH!"
        print(f"  {split}: images={n_img}, labels={n_lbl} — {status}")


if __name__ == "__main__":
    main()