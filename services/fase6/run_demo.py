"""Train and evaluate the local Fase 6 classifier on the bundled demo images."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.fase6.cnn_model import NumpyCNNClassifier
from services.fase6.dataset_loader import load_dataset_splits


def main() -> int:
    dataset = load_dataset_splits(image_size=(32, 32))
    model = NumpyCNNClassifier(
        input_shape=(32, 32, 3),
        num_classes=len(dataset.classes),
        random_state=42,
    )
    history = model.fit(
        dataset.x_train,
        dataset.y_train,
        dataset.x_val,
        dataset.y_val,
        epochs=30,
        lr=0.1,
    )
    metrics = model.evaluate(dataset.x_test, dataset.y_test)
    summary = {
        "dataset": str(dataset.dataset_path),
        "is_synthetic_demo": dataset.is_demo,
        "classes": list(dataset.classes),
        "train_images": len(dataset.x_train),
        "test_images": len(dataset.x_test),
        "epochs": len(history.epochs),
        "accuracy": metrics.accuracy,
        "precision": metrics.precision,
        "recall": metrics.recall,
        "f1": metrics.f1,
        "inference_latency_ms_per_image": metrics.inference_latency_ms,
        "confusion_matrix": metrics.confusion_matrix.tolist(),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
