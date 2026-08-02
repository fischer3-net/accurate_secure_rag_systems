"""Lab 4 – golden dataset, deterministic metrics, evaluation runner."""

from .dataset import GoldenRow, load_golden_dataset, validate_golden_dataset, load_fixture
from .metrics import score_row, aggregate, control_hit_rate, EvalReport
from .eval_runner import run_evaluation

__all__ = [
    "GoldenRow",
    "load_golden_dataset",
    "validate_golden_dataset",
    "load_fixture",
    "score_row",
    "aggregate",
    "control_hit_rate",
    "EvalReport",
    "run_evaluation",
]
