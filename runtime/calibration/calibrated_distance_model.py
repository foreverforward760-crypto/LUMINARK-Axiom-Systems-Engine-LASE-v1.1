"""
Learned metric space with calibration-aware distance function.
"""

import numpy as np

class CalibratedDistanceModel:
    def __init__(self, params):
        self.p = params

    def distance(self, x, centroid):
        diff = (x - centroid) / 10.0
        return np.sqrt(np.sum(self.p.weights * diff * diff))

    def all_distances(self, x):
        return np.array([
            self.distance(x, c) for c in self.p.centroids
        ])
