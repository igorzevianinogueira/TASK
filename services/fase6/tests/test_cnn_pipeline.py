from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

from services.fase6.benchmark import (
    build_comparison_dataframe,
    get_default_benchmarks,
)
from services.fase6.cnn_model import (
    EvaluationMetrics,
    NumpyCNNClassifier,
)
from services.fase6.dataset_loader import (
    CLASSES,
    SPLIT_COUNTS,
    load_dataset_splits,
)


class TestFarmTechCNNPipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = load_dataset_splits(image_size=(32, 32))  # tamanho menor para agilidade nos testes

    def test_dataset_splits_and_proportions(self) -> None:
        """Valida se as proporções oficiais (32 treino / 4 val / 4 test por classe) estão satisfeitas."""
        total_train = SPLIT_COUNTS["train"] * len(CLASSES)
        total_val = SPLIT_COUNTS["val"] * len(CLASSES)
        total_test = SPLIT_COUNTS["test"] * len(CLASSES)

        self.assertEqual(len(self.dataset.x_train), total_train)
        self.assertEqual(len(self.dataset.y_train), total_train)
        self.assertEqual(len(self.dataset.x_val), total_val)
        self.assertEqual(len(self.dataset.y_val), total_val)
        self.assertEqual(len(self.dataset.x_test), total_test)
        self.assertEqual(len(self.dataset.y_test), total_test)

        # Total geral mínimo de 80 imagens exigido pelo enunciado
        total_images = total_train + total_val + total_test
        self.assertEqual(total_images, 80)

    def test_cnn_forward_shapes_and_probabilities(self) -> None:
        """Valida que o forward pass gera probabilidades consistentes (soma 1 por amostra)."""
        cnn = NumpyCNNClassifier(input_shape=(32, 32, 3), num_classes=2, random_state=42)
        probs = cnn.forward(self.dataset.x_val)

        self.assertEqual(probs.shape, (len(self.dataset.x_val), 2))
        np.testing.assert_allclose(np.sum(probs, axis=1), 1.0, rtol=1e-5)

    def test_cnn_training_and_evaluation(self) -> None:
        """Valida que a CNN treina, registra histórico de épocas e gera métricas no teste."""
        cnn = NumpyCNNClassifier(input_shape=(32, 32, 3), num_classes=2, random_state=42)
        history = cnn.fit(
            self.dataset.x_train,
            self.dataset.y_train,
            self.dataset.x_val,
            self.dataset.y_val,
            epochs=5,
            lr=0.01,
        )

        self.assertEqual(len(history.epochs), 5)
        self.assertGreater(history.training_time_seconds, 0.0)

        metrics = cnn.evaluate(self.dataset.x_test, self.dataset.y_test)
        self.assertIsInstance(metrics, EvaluationMetrics)
        self.assertGreaterEqual(metrics.accuracy, 0.0)
        self.assertLessEqual(metrics.accuracy, 1.0)
        self.assertEqual(metrics.confusion_matrix.shape, (2, 2))
        self.assertGreater(metrics.inference_latency_ms, 0.0)

    def test_benchmark_dimensions_covered(self) -> None:
        """Valida que o benchmark cobre as 4 dimensões obrigatórias do barema da FIAP."""
        benchmarks = get_default_benchmarks(cnn_accuracy=0.875, cnn_latency_ms=8.5)
        df = build_comparison_dataframe(benchmarks)

        # Verifica presença das 3 abordagens
        self.assertEqual(len(df), 3)
        self.assertTrue(any("YOLO Customizada" in name for name in df["abordagem"]))
        self.assertTrue(any("YOLO Padrão" in name for name in df["abordagem"]))
        self.assertTrue(any("CNN do Zero" in name for name in df["abordagem"]))

        # Verifica as 4 dimensões obrigatórias do barema
        required_columns = [
            "facilidade_uso_integracao",
            "precisao_metrica_principal",
            "tempo_treinamento_estimado",
            "latencia_inferencia_ms",
        ]
        for col in required_columns:
            self.assertIn(col, df.columns)


if __name__ == "__main__":
    unittest.main()
