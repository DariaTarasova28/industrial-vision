from huggingface_hub import snapshot_download

print("Скачиваю только train/labels...")
snapshot_download(
    repo_id="jhboyo/ppe-dataset",
    repo_type="dataset",
    local_dir="datasets/ppe_raw",
    allow_patterns=["train/labels/*"],
    max_workers=4,
)
print("Готово. Проверьте: datasets/ppe_raw/train/labels")