"""
v5 Calibration Engine – learns structure from data
"""

import numpy as np
from collections import deque
from sap_learned_parameters import SAPLearnedParameters
from calibrated_distance_model import CalibratedDistanceModel


class SAPCalibrationEngine:
    def __init__(self, lr=0.01, stability_lambda=0.1):
        self.params = SAPLearnedParameters()
        self.model = CalibratedDistanceModel(self.params)

        self.lr = lr
        self.stability_lambda = stability_lambda

        self.buffer = deque(maxlen=1000)

    def predict_proba(self, x):
        d = self.model.all_distances(x)

        # softmin with learned temperature
        temp = self.params.temperature
        d = d - np.min(d)
        exp = np.exp(-d / temp)

        return exp / np.sum(exp)

    def expected_stage(self, p):
        return float(np.sum(np.arange(len(p)) * p))

    def entropy(self, p):
        return float(-np.sum(p * np.log(p + 1e-12)))

    def forward(self, x):
        x = np.array(x, dtype=float)

        p = self.predict_proba(x)
        y = self.expected_stage(p)

        return {
            "probs": p,
            "expected_stage": y,
            "entropy": self.entropy(p)
        }

    def update(self, x, true_stage):
        """
        Online learning step:
        - pulls centroid toward observed data
        - pushes away incorrect centroids
        - enforces stability constraint
        """

        x = np.array(x, dtype=float)
        p = self.predict_proba(x)

        # gradient-like update
        for i in range(len(self.params.centroids)):
            error = (p[i] - (1.0 if i == true_stage else 0.0))

            direction = (x - self.params.centroids[i])

            self.params.centroids[i] -= self.lr * error * direction

        # regularization: maintain structure
        self.apply_stability_penalty()

        self.params.project_constraints()

    def apply_stability_penalty(self):
        """
        Prevent collapse / divergence of representation manifold
        """

        for i in range(len(self.params.centroids) - 1):
            diff = self.params.centroids[i+1] - self.params.centroids[i]
            dist = np.linalg.norm(diff)

            if dist < 0.3:
                # push apart
                self.params.centroids[i+1] += 0.05 * diff
