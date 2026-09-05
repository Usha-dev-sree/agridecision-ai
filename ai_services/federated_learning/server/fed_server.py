"""
Federated Learning - Aggregation Server (FedAvg)
Implements the Federated Averaging (FedAvg) algorithm to aggregate local model updates from edge client devices
without raw data transfer, preserving data privacy for regional agricultural cooperatives.
"""
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from backend.common.logging import get_logger

logger = get_logger(__name__)


class FederatedAggregationServer:
    """Central server orchestrating privacy-preserving Federated Averaging (FedAvg)."""

    def __init__(self, model_name: str, num_rounds: int = 5) -> None:
        self.model_name = model_name
        self.num_rounds = num_rounds
        self.global_weights: Optional[List[np.ndarray]] = None

    def initialize_global_weights(self, layer_shapes: List[Tuple[int, ...]]) -> None:
        """Initialize global model weight tensors."""
        self.global_weights = [np.random.normal(0, 0.1, size=shape) for shape in layer_shapes]
        logger.info("Initialized federated global weights for %s", self.model_name)

    def aggregate_updates(self, client_updates: List[Dict[str, Any]]) -> List[np.ndarray]:
        """
        Aggregate weights using weighted FedAvg:
        $w_{global} = \\sum_{i=1}^K \\frac{n_i}{N} w_i$
        where $n_i$ is the number of local samples on client $i$, and $N = \\sum n_i$.
        """
        if not client_updates:
            raise ValueError("No client updates received for aggregation.")

        total_samples = sum(update["num_samples"] for update in client_updates)
        num_layers = len(client_updates[0]["weights"])

        aggregated_weights = [np.zeros_like(client_updates[0]["weights"][i]) for i in range(num_layers)]

        for update in client_updates:
            weight_factor = update["num_samples"] / total_samples
            client_weights = update["weights"]
            for layer_idx in range(num_layers):
                aggregated_weights[layer_idx] += weight_factor * client_weights[layer_idx]

        self.global_weights = aggregated_weights
        logger.info(
            "FedAvg aggregation complete",
            extra={"model_name": self.model_name, "num_clients": len(client_updates), "total_samples": total_samples}
        )
        return aggregated_weights

    def get_global_weights(self) -> List[np.ndarray]:
        """Return latest global model parameters."""
        if self.global_weights is None:
            raise ValueError("Global weights have not been initialized.")
        return self.global_weights
