from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image, ImageDraw


DEFAULT_DATASET_DIR = Path(__file__).resolve().parent / "data" / "dataset"
CLASSES = ("healthy_crop", "weed_pest")

# Proporção oficial estrita exigida pelo enunciado da Fase 6:
# Treino: 32 por classe (64 total)
# Validação: 4 por classe (8 total)
# Teste: 4 por classe (8 total)
# Total geral: 40 por classe (80 total)
SPLIT_COUNTS = {
    "train": 32,
    "val": 4,
    "test": 4,
}


@dataclass(frozen=True)
class DatasetSplits:
    x_train: np.ndarray
    y_train: np.ndarray
    x_val: np.ndarray
    y_val: np.ndarray
    x_test: np.ndarray
    y_test: np.ndarray
    classes: Tuple[str, ...]
    dataset_path: Path
    is_demo: bool


def create_demo_crop_image(class_name: str, seed: int, size: Tuple[int, int] = (64, 64)) -> Image.Image:
    """Gera uma imagem sintética demonstrativa com padrões visuais diferenciados."""
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", size, color=(240, 245, 235))
    draw = ImageDraw.Draw(img)

    if class_name == "healthy_crop":
        # Fundo verde saudável com linhas representando nervuras de folhas limpas
        base_green = int(rng.integers(140, 195))
        draw.rectangle([0, 0, size[0], size[1]], fill=(30, base_green, 45))
        for _ in range(6):
            x1, y1 = int(rng.integers(5, size[0] - 5)), int(rng.integers(5, size[1] - 5))
            x2, y2 = int(rng.integers(5, size[0] - 5)), int(rng.integers(5, size[1] - 5))
            draw.line([(x1, y1), (x2, y2)], fill=(70, min(255, base_green + 40), 80), width=2)
    else:
        # Fundo com manchas amarronzadas/amareladas de pragas ou ervas invasoras
        base_brown = int(rng.integers(110, 160))
        draw.rectangle([0, 0, size[0], size[1]], fill=(base_brown, int(rng.integers(80, 120)), 35))
        # Padrões de manchas e pontuações irregulares
        for _ in range(12):
            rx, ry = int(rng.integers(4, size[0] - 8)), int(rng.integers(4, size[1] - 8))
            rw, rh = int(rng.integers(3, 10)), int(rng.integers(3, 10))
            draw.ellipse([rx, ry, rx + rw, ry + rh], fill=(220, 180, 40))

    return img


def ensure_demo_dataset(base_dir: Path | str = DEFAULT_DATASET_DIR) -> Tuple[Path, bool]:
    """Garante que a estrutura de diretórios e o dataset (com mínimo 80 imagens) existam."""
    target_dir = Path(base_dir)
    splits = ("train", "val", "test")

    # Verifica se já existe dataset com arquivos
    existing_images = list(target_dir.glob("*/*/*.png")) + list(target_dir.glob("*/*/*.jpg"))
    if len(existing_images) >= 80:
        demo_names = {
            f"img_{class_name}_{i + 1:03d}.png"
            for count in SPLIT_COUNTS.values()
            for class_name in CLASSES
            for i in range(count)
        }
        is_demo = all(path.name in demo_names for path in existing_images)
        return target_dir, is_demo

    # Cria estrutura conforme proporção da atividade
    seed_counter = 42
    for split, count in SPLIT_COUNTS.items():
        for class_name in CLASSES:
            folder = target_dir / split / class_name
            folder.mkdir(parents=True, exist_ok=True)
            for i in range(count):
                img_path = folder / f"img_{class_name}_{i + 1:03d}.png"
                if not img_path.exists():
                    img = create_demo_crop_image(class_name, seed=seed_counter)
                    img.save(img_path)
                seed_counter += 1

    return target_dir, True


def load_dataset_splits(
    base_dir: Path | str = DEFAULT_DATASET_DIR,
    image_size: Tuple[int, int] = (64, 64),
) -> DatasetSplits:
    """Carrega as imagens dos splits em matrizes normalizadas (N, H, W, C) float32 em [0, 1]."""
    dataset_path, is_demo = ensure_demo_dataset(base_dir)

    def _load_split(split_name: str) -> Tuple[np.ndarray, np.ndarray]:
        images: list[np.ndarray] = []
        labels: list[int] = []

        for class_idx, class_name in enumerate(CLASSES):
            folder = dataset_path / split_name / class_name
            for file_path in sorted(folder.glob("*.png")) + sorted(folder.glob("*.jpg")):
                with Image.open(file_path) as raw:
                    img = raw.convert("RGB").resize(image_size)
                    arr = np.asarray(img, dtype=np.float32) / 255.0
                    images.append(arr)
                    labels.append(class_idx)

        return np.array(images, dtype=np.float32), np.array(labels, dtype=np.int64)

    x_train, y_train = _load_split("train")
    x_val, y_val = _load_split("val")
    x_test, y_test = _load_split("test")

    return DatasetSplits(
        x_train=x_train,
        y_train=y_train,
        x_val=x_val,
        y_val=y_val,
        x_test=x_test,
        y_test=y_test,
        classes=CLASSES,
        dataset_path=dataset_path,
        is_demo=is_demo,
    )
