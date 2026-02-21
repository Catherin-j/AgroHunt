#scoring_engine.py
from typing import Dict
import math


class ScoringEngine:
    """
    Research-backed Multi-Criteria Decision Analysis (MCDA)
    Weighted Linear Combination (WLC) model.
    """

    def __init__(self, weights: Dict[str, float], threshold: float = 0.75):
        self.weights = weights
        self.threshold = threshold
        self._validate_weights()

    def _validate_weights(self):
        total = sum(self.weights.values())
        if not math.isclose(total, 1.0, rel_tol=1e-6):
            raise ValueError(
                f"Weights must sum to 1. Current sum = {total}"
            )

    def compute(self, scores: Dict[str, float]) -> Dict:
        """
        Computes final weighted score and breakdown.
        """

        final_score = 0.0
        contribution = {}

        for module, weight in self.weights.items():

            if module not in scores:
                raise ValueError(f"Missing score for {module}")

            value = scores[module]

            # Safety check
            if not (0 <= value <= 1):
                raise ValueError(
                    f"{module} score must be between 0 and 1"
                )

            module_contribution = weight * value
            contribution[module] = round(module_contribution, 4)
            final_score += module_contribution

        final_score = round(final_score, 4)

        decision = "PASS" if final_score >= self.threshold else "FAIL"

        return {
            "final_score": final_score,
            "decision": decision,
            "contribution_breakdown": contribution
        }