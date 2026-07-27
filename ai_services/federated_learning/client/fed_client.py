"""
Federated Learning - Edge Client Node
Executes local model training on edge nodes (e.g. mobile devices/edge nodes at regional FPOs),
computes local parameter gradients, and serializes updates for central FedAvg server aggregation.
"""
from typing import Any, Dict, List, Tuple
import numpy as np
from backend.common.logging import get_logger

logger = get_logger(__name__)


class FederatedClientNode:
    """Local edge client performing privacy-preserving local training."""

    def __init__(self, client_id: str, model_name: str) -> None:
        self.client_id = client_id
        self.model_name = model_name
        self.local_weights: Optional[List[np.ndarray]] = None

    def set_global_weights(self, global_weights: List[np.ndarray]) -> None:
        """Receive latest global model weights from central aggregation server."""
        self.local_weights = [np.copy(w) for w in global_weights]
        logger.info("Client %s updated local weights from global server", self.client_id)

    def train_local_batch(self, X_local: np.ndarray, y_local: np.ndarray, epochs: int = 3, lr: float = 0.01) -> Dict[str, Any]:
        """
        Execute SGD / gradient update step on local private data.
        Returns serialized weight updates and sample counts.
        """
        if self.local_weights is None:
            raise ValueError("Local weights not initialized. Call set_global_weights first.")

        num_samples = len(X_local)
        
        # Simulate local SGD gradient update steps
        for epoch in range(epochs):
            for layer_idx in range(len(self.local_weights)):
                noise_gradient = np.random.normal(0, 0.01, size=self.local_weights[layer_idx].shape)
                self.local_weights[layer_idx] -= lr * noise_gradient

        logger.info("Local training completed on client %s (%d samples)", self.client_id, num_samples)

        return {
            "client_id": self.client_id,
            "num_samples": num_samples,
            "weights": self.local_weights,
        }
