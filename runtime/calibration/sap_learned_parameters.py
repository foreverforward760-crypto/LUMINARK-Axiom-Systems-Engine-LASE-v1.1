"""
SAP v5 – Learned Canonical Parameters
Replaces fixed centroids with trainable embeddings under stability constraints.
"""

import numpy as np

NUM_STAGES = 10
DIM = 5

class SAPLearnedParameters:
    def __init__(self, seed_centroids=None):
        if seed_centroids is not None:
            self.centroids = np.array(seed_centroids, dtype=float)
        else:
            # Initialize near v4 canonical structure
            self.centroids = np.array([
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [1.0, 8.0, 1.0, 1.0, 1.0],
                [2.0, 7.0, 2.0, 2.0, 2.0],
                [4.0, 7.0, 2.5, 3.0, 4.0],
                [3.5, 6.5, 3.0, 3.5, 5.0],
                [5.0, 4.0, 5.0, 5.0, 4.5],
                [6.0, 5.5, 4.0, 6.0, 6.5],
                [6.5, 3.0, 7.0, 7.0, 3.5],
                [7.5, 7.0, 8.0, 2.0, 2.0],
                [8.0, 2.0, 8.5, 1.5, 1.5],
            ], dtype=float)

        # Learnable weights (initialized from v4)
        self.weights = np.array([1.0, 1.5, 1.5, 1.0, 0.8], dtype=float)

        # Temperature (calibrated)
        self.temperature = 0.5

    def project_constraints(self):
        """
        Enforce stability constraints:
        - centroid values remain in [0, 10]
        - weights remain positive
        - centroid separation must be non-zero
        """
        self.centroids = np.clip(self.centroids, 0.0, 10.0)
        self.weights = np.clip(self.weights, 0.1, 5.0)

        # Prevent collapse (important stability constraint)
        for i in range(len(self.centroids) - 1):
            diff = np.linalg.norm(self.centroids[i+1] - self.centroids[i])
            if diff < 0.5:
                self.centroids[i+1] += np.random.normal(0, 0.1, size=5)
