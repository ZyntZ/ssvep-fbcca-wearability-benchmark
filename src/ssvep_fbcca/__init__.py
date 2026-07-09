from .cca import CCAClassifier
from .fbcca import FBCCAClassifier
from .metrics import accuracy, information_transfer_rate, summarize_subject_metrics

__all__ = [
    "CCAClassifier",
    "FBCCAClassifier",
    "accuracy",
    "information_transfer_rate",
    "summarize_subject_metrics",
]
