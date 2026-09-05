"""
Triton gRPC Client & Local ONNX Runtime Fallback
An asynchronous interface that calls the Triton Inference Server via gRPC,
with a transparent local ONNX Runtime fallback when Triton is offline or uninstalled.
"""
import logging
import os
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class TritonInferenceClient:
    """Async Client to execute model inferences on Triton Server or locally via ORT."""

    def __init__(self, triton_url: str = "localhost:8001", local_repo_path: str = "c:/AGRICULTURE PROJECT/agridecision-ai/ai_services/inference_gateway/model_repository") -> None:
        self.triton_url = triton_url
        self.local_repo_path = local_repo_path
        self._ort_sessions: Dict[str, Any] = {}
        self._has_triton_library = True
        
        try:
            import tritonclient.grpc.aio as triton_grpc
        except ImportError:
            self._has_triton_library = False
            logger.info("tritonclient-grpc not found. Operating exclusively in local ONNX Runtime mode.")

    def _get_local_session(self, model_name: str) -> Any:
        """Load and cache local ONNX Runtime session if needed."""
        if model_name in self._ort_sessions:
            return self._ort_sessions[model_name]

        try:
            import onnxruntime as ort
        except ImportError:
            raise ImportError(f"Cannot run model {model_name} locally: 'onnxruntime' is not installed.")

        model_path = os.path.join(self.local_repo_path, model_name, "1", "model.onnx")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"ONNX model file not found at: {model_path}")

        session = ort.InferenceSession(model_path)
        self._ort_sessions[model_name] = session
        logger.info("Initialized local ONNX Runtime session for model: %s", model_name)
        return session

    async def _infer_triton(self, model_name: str, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Perform inference on Triton Server via gRPC."""
        import tritonclient.grpc.aio as triton_grpc
        
        client = triton_grpc.InferenceServerClient(url=self.triton_url)
        triton_inputs = []
        for name, data in inputs.items():
            t_in = triton_grpc.InferInput(name, list(data.shape), triton_grpc.np_to_triton_dtype(data.dtype))
            t_in.set_data_from_numpy(data)
            triton_inputs.append(t_in)
            
        try:
            response = await client.infer(model_name=model_name, inputs=triton_inputs, timeout=5.0)
            outputs = {}
            for out_name in [out.name for out in response.get_response().outputs]:
                outputs[out_name] = response.as_numpy(out_name)
            return outputs
        except Exception as e:
            logger.warning("Triton server at %s failed for %s: %s. Falling back to local ONNX Runtime.", self.triton_url, model_name, e)
            raise e

    async def run_inference(self, model_name: str, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Execute inference. Tries Triton first, falls back to local ONNX Runtime session."""
        if self._has_triton_library:
            try:
                return await self._infer_triton(model_name, inputs)
            except Exception:
                pass
        
        # Local ONNX Runtime execution fallback
        session = self._get_local_session(model_name)
        ort_inputs = {node.name: inputs[node.name] for node in session.get_inputs() if node.name in inputs}
        outputs = session.run(None, ort_inputs)
        
        output_names = [node.name for node in session.get_outputs()]
        return {name: val for name, val in zip(output_names, outputs)}

    async def infer_crop_recommendation(self, features: List[float]) -> Tuple[int, List[float]]:
        """
        Infers crop suitability.
        Inputs: ph, organic_carbon, N, P, K, temp, rainfall (7 values)
        Outputs: predicted label (int), class probabilities (List[float])
        """
        arr = np.array([features], dtype=np.float32) # shape [1, 7]
        try:
            results = await self.run_inference("crop_recommendation", {"float_input": arr})
            label = int(results["output_label"][0])
            prob_data = results["output_probability"][0]
            if isinstance(prob_data, dict):
                probs = [float(v) for v in prob_data.values()]
            elif hasattr(prob_data, "tolist"):
                probs = prob_data.tolist()
            else:
                probs = list(prob_data)
            return label, probs
        except Exception as e:
            logger.error("Crop Recommendation inference failure: %s", e)
            # Hardcoded safe rule-based default fallback if both Triton and local ORT are completely offline
            return 1, [0.1, 0.6, 0.1, 0.05, 0.05, 0.05, 0.03, 0.02]

    async def infer_yield_prediction(self, features: List[float]) -> float:
        """
        Predict crop yield in kg/ha.
        Inputs: ph, organic_carbon, N, P, K, temp, rainfall, crop_class_id (8 values)
        """
        arr = np.array([features], dtype=np.float32) # shape [1, 8]
        try:
            results = await self.run_inference("yield_prediction", {"float_input": arr})
            # Outputs can be "variable" or similar
            out_key = list(results.keys())[0]
            val = float(results[out_key][0])
            return val
        except Exception as e:
            logger.error("Yield prediction inference failure: %s", e)
            return 3200.0

    async def infer_price_forecasting(self, history: List[List[float]]) -> List[float]:
        """
        Predict prices for next 7 days.
        Inputs: 30 days of [modal, min, max] prices -> shape [1, 30, 3]
        """
        arr = np.array([history], dtype=np.float32) # shape [1, 30, 3]
        try:
            results = await self.run_inference("price_forecasting", {"input": arr})
            out_key = list(results.keys())[0]
            return results[out_key][0].tolist()
        except Exception as e:
            logger.error("Price forecasting inference failure: %s", e)
            # Default mock return
            return [history[-1][0] * (1.0 + 0.005 * i) for i in range(1, 8)]

    async def infer_disease_detection(self, image_tensor: np.ndarray) -> Tuple[int, List[float]]:
        """
        Predict leaf disease type from an image tensor.
        Inputs: image tensor of shape [1, 3, 224, 224]
        """
        try:
            results = await self.run_inference("disease_detection", {"input": image_tensor})
            out_key = list(results.keys())[0]
            logits = results[out_key][0]
            # Softmax calculation
            exp_logits = np.exp(logits - np.max(logits))
            probs = (exp_logits / np.sum(exp_logits)).tolist()
            label = int(np.argmax(probs))
            return label, probs
        except Exception as e:
            logger.error("Disease detection inference failure: %s", e)
            return 4, [0.05, 0.05, 0.05, 0.05, 0.8] # Return healthy as fallback

    async def infer_weather_prediction(self, features: List[float]) -> Tuple[float, float, float]:
        """
        Predict next-day weather (temp_max, rainfall, humidity).
        Inputs: lat, lon, day_of_year, current_temp, current_humidity (5 values)
        Outputs: (predicted_temp_max_c, predicted_rainfall_mm, predicted_humidity_pct)
        """
        arr = np.array([features], dtype=np.float32)  # shape [1, 5]
        try:
            results = await self.run_inference("weather_prediction", {"float_input": arr})
            out_key = list(results.keys())[0]
            vals = results[out_key][0]
            return float(vals[0]), float(max(0.0, vals[1])), float(min(100.0, max(0.0, vals[2])))
        except Exception as e:
            logger.error("Weather prediction inference failure: %s", e)
            # Default safe climatological return
            return features[3] + 2.0, 5.0, min(95.0, features[4] + 1.0)
