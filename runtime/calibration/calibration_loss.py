"""
Calibration loss: cross-entropy + geometric regularization
"""

import numpy as np

def cross_entropy(p, y):
    return -np.log(p[y] + 1e-12)

def centroid_separation_penalty(centroids):
    penalty = 0.0
    for i in range(len(centroids) - 1):
        dist = np.linalg.norm(centroids[i+1] - centroids[i])
        penalty += 1.0 / (dist + 1e-6)
    return penalty

def total_loss(p, y, centroids, lambda_sep=0.1):
    return cross_entropy(p, y) + lambda_sep * centroid_separation_penalty(centroids)
