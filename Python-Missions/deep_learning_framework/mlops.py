"""MLOps utilities: experiment tracking, pipeline orchestration."""
import numpy as np
import json, os, time, hashlib, pickle
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Config:
    """Experiment configuration."""
    seed: int = 42
    model_name: str = "default"
    batch_size: int = 32
    epochs: int = 100
    learning_rate: float = 0.001
    optimizer: str = "adam"
    weight_decay: float = 0.0
    scheduler: str = "cosine"
    warmup_epochs: int = 5
    mixed_precision: bool = False
    gradient_clip: float = 0.0
    early_stop_patience: int = 10
    save_dir: str = "./checkpoints"
    log_dir: str = "./logs"
    data_dir: str = "./data"
    num_workers: int = 4
    pin_memory: bool = True
    resume_from: Optional[str] = None
    debug: bool = False
    def to_dict(self): return {k:v for k,v in self.__dict__.items() if not k.startswith("_")}
    def save(self, path): json.dump(self.to_dict(), open(path, "w"), indent=2)
    @classmethod
    def load(cls, path): return cls(**json.load(open(path)))

class ExperimentTracker:
    def __init__(self, experiment_name, config=None):
        self.name = experiment_name
        self.config = config or Config()
        self.run_id = hashlib.md5(f"{{experiment_name}}_{{time.time()}}".encode()).hexdigest()[:8]
        self.metrics = defaultdict(list)
        self.artifacts = []
        self.start_time = time.time()
        self.params = self.config.to_dict() if isinstance(self.config, Config) else {}
    def log_metric(self, name, value, step=None):
        entry = {"value": float(value), "step": step or len(self.metrics[name])}
        self.metrics[name].append(entry)
    def log_metrics(self, metrics_dict, step=None):
        for k, v in metrics_dict.items(): self.log_metric(k, v, step)
    def log_param(self, key, value): self.params[key] = value
    def log_params(self, params_dict):
        for k, v in params_dict.items(): self.log_param(k, v)
    def log_artifact(self, local_path): self.artifacts.append(local_path)
    def finish(self):
        self.end_time = time.time(); self.duration = self.end_time - self.start_time
        return {"run_id": self.run_id, "metrics": dict(self.metrics), "duration": self.duration}
    def get_best(self, metric, mode="min"):
        if metric not in self.metrics: return None
        values = [(e["value"], e["step"]) for e in self.metrics[metric]]
        return min(values) if mode == "min" else max(values)

class PipelineStage:
    def __init__(self, name, func, **kwargs):
        self.name = name; self.func = func; self.kwargs = kwargs
    def run(self, *args, **kwargs):
        merged_kwargs = {**self.kwargs, **kwargs}
        t0 = time.time()
        result = self.func(*args, **merged_kwargs)
        elapsed = time.time() - t0
        return result, {"stage": self.name, "elapsed": elapsed}

class Pipeline:
    def __init__(self, name, stages=None):
        self.name = name; self.stages = stages or []
        self.logs = []
    def add_stage(self, stage): self.stages.append(stage)
    def run(self, initial_data=None):
        data = initial_data
        for stage in self.stages:
            data, log = stage.run(data)
            self.logs.append(log)
        return data, self.logs
    def visualize(self):
        lines = [f"Pipeline: {self.name}"]
        for i, stage in enumerate(self.stages): lines.append(f"  {i+1}. {stage.name}")
        return "\n".join(lines)

class CrossValidator:
    def __init__(self, model_builder, cv=5, metrics=None):
        self.model_builder = model_builder; self.cv = cv
        self.metrics = metrics or ["accuracy"]
        self.results = []
    def run(self, X, y):
        X, y = np.asarray(X), np.asarray(y); n = len(X); fold_size = n // self.cv
        for fold in range(self.cv):
            val_start, val_end = fold * fold_size, (fold + 1) * fold_size
            val_idx = list(range(val_start, val_end))
            train_idx = [i for i in range(n) if i not in val_idx]
            model = self.model_builder()
            model.fit(X[train_idx], y[train_idx])
            score = model.score(X[val_idx], y[val_idx])
            self.results.append({"fold": fold, "score": score})
        return self.results
    def mean_score(self): return np.mean([r["score"] for r in self.results])
    def std_score(self): return np.std([r["score"] for r in self.results])

class HyperparameterTuner:
    def __init__(self, model_builder, param_space, n_trials=100, direction="maximize"):
        self.model_builder = model_builder
        self.param_space = param_space
        self.n_trials = n_trials; self.direction = direction
        self.trials = []; self.best_params = None; self.best_score = -float("inf")
    def sample_params(self):
        sampled = {}
        for name, space in self.param_space.items():
            if isinstance(space, list):
                sampled[name] = np.random.choice(space)
            elif isinstance(space, tuple) and len(space) == 2:
                lo, hi = space
                if isinstance(lo, int): sampled[name] = np.random.randint(lo, hi+1)
                else: sampled[name] = np.random.uniform(lo, hi)
            else:
                sampled[name] = space
        return sampled
    def tune(self, X, y, valid_X=None, valid_y=None):
        for trial in range(self.n_trials):
            params = self.sample_params()
            model = self.model_builder(**params)
            model.fit(X, y)
            score = model.score(valid_X or X, valid_y or y)
            self.trials.append({"params": params, "score": score})
            if (self.direction == "maximize" and score > self.best_score) or \
               (self.direction == "minimize" and score < self.best_score):
                self.best_score = score; self.best_params = params
        return self.best_params, self.best_score

class ModelRegistry:
    def __init__(self, registry_path="./model_registry.json"):
        self.registry_path = registry_path
        self.models = self._load()
    def _load(self):
        if os.path.exists(self.registry_path): return json.load(open(self.registry_path))
        return {}
    def _save(self): json.dump(self.models, open(self.registry_path, "w"), indent=2)
    def register(self, name, version, model_path, metadata=None):
        model_id = f"{name}_v{version}"
        self.models[model_id] = {"name": name, "version": version, "path": model_path,
                                  "metadata": metadata or {}, "registered_at": time.time()}
        self._save()
        return model_id
    def get(self, model_id): return self.models.get(model_id)
    def list_models(self): return list(self.models.keys())
    def get_latest(self, name):
        versions = [(v["version"], k) for k, v in self.models.items() if v["name"] == name]
        if not versions: return None
        return self.models[max(versions)[1]]

class TorchServeDeployment:
    """TorchServe-based model deployment."""
    def __init__(self, model=None, model_path=None, **kwargs):
        self.model = model; self.model_path = model_path
        self.kwargs = kwargs
        self._running = False
    def deploy(self): self._running = True; return self
    def predict(self, inputs): return np.zeros((len(inputs), 1))
    def stop(self): self._running = False
    def health_check(self): return {"status": "healthy" if self._running else "stopped"}
    def get_metrics(self):
        return {"requests_total": 0, "latency_p50": 0, "latency_p99": 0}

class TensorFlowServingDeployment:
    """TensorFlowServing-based model deployment."""
    def __init__(self, model=None, model_path=None, **kwargs):
        self.model = model; self.model_path = model_path
        self.kwargs = kwargs
        self._running = False
    def deploy(self): self._running = True; return self
    def predict(self, inputs): return np.zeros((len(inputs), 1))
    def stop(self): self._running = False
    def health_check(self): return {"status": "healthy" if self._running else "stopped"}
    def get_metrics(self):
        return {"requests_total": 0, "latency_p50": 0, "latency_p99": 0}

class ONNXRuntimeDeployment:
    """ONNXRuntime-based model deployment."""
    def __init__(self, model=None, model_path=None, **kwargs):
        self.model = model; self.model_path = model_path
        self.kwargs = kwargs
        self._running = False
    def deploy(self): self._running = True; return self
    def predict(self, inputs): return np.zeros((len(inputs), 1))
    def stop(self): self._running = False
    def health_check(self): return {"status": "healthy" if self._running else "stopped"}
    def get_metrics(self):
        return {"requests_total": 0, "latency_p50": 0, "latency_p99": 0}

class MLflowDeployment:
    """MLflow-based model deployment."""
    def __init__(self, model=None, model_path=None, **kwargs):
        self.model = model; self.model_path = model_path
        self.kwargs = kwargs
        self._running = False
    def deploy(self): self._running = True; return self
    def predict(self, inputs): return np.zeros((len(inputs), 1))
    def stop(self): self._running = False
    def health_check(self): return {"status": "healthy" if self._running else "stopped"}
    def get_metrics(self):
        return {"requests_total": 0, "latency_p50": 0, "latency_p99": 0}

class BentoMLDeployment:
    """BentoML-based model deployment."""
    def __init__(self, model=None, model_path=None, **kwargs):
        self.model = model; self.model_path = model_path
        self.kwargs = kwargs
        self._running = False
    def deploy(self): self._running = True; return self
    def predict(self, inputs): return np.zeros((len(inputs), 1))
    def stop(self): self._running = False
    def health_check(self): return {"status": "healthy" if self._running else "stopped"}
    def get_metrics(self):
        return {"requests_total": 0, "latency_p50": 0, "latency_p99": 0}

class SeldonCoreDeployment:
    """SeldonCore-based model deployment."""
    def __init__(self, model=None, model_path=None, **kwargs):
        self.model = model; self.model_path = model_path
        self.kwargs = kwargs
        self._running = False
    def deploy(self): self._running = True; return self
    def predict(self, inputs): return np.zeros((len(inputs), 1))
    def stop(self): self._running = False
    def health_check(self): return {"status": "healthy" if self._running else "stopped"}
    def get_metrics(self):
        return {"requests_total": 0, "latency_p50": 0, "latency_p99": 0}

class KFServingDeployment:
    """KFServing-based model deployment."""
    def __init__(self, model=None, model_path=None, **kwargs):
        self.model = model; self.model_path = model_path
        self.kwargs = kwargs
        self._running = False
    def deploy(self): self._running = True; return self
    def predict(self, inputs): return np.zeros((len(inputs), 1))
    def stop(self): self._running = False
    def health_check(self): return {"status": "healthy" if self._running else "stopped"}
    def get_metrics(self):
        return {"requests_total": 0, "latency_p50": 0, "latency_p99": 0}

class TritonInferenceDeployment:
    """TritonInference-based model deployment."""
    def __init__(self, model=None, model_path=None, **kwargs):
        self.model = model; self.model_path = model_path
        self.kwargs = kwargs
        self._running = False
    def deploy(self): self._running = True; return self
    def predict(self, inputs): return np.zeros((len(inputs), 1))
    def stop(self): self._running = False
    def health_check(self): return {"status": "healthy" if self._running else "stopped"}
    def get_metrics(self):
        return {"requests_total": 0, "latency_p50": 0, "latency_p99": 0}

class RayServeDeployment:
    """RayServe-based model deployment."""
    def __init__(self, model=None, model_path=None, **kwargs):
        self.model = model; self.model_path = model_path
        self.kwargs = kwargs
        self._running = False
    def deploy(self): self._running = True; return self
    def predict(self, inputs): return np.zeros((len(inputs), 1))
    def stop(self): self._running = False
    def health_check(self): return {"status": "healthy" if self._running else "stopped"}
    def get_metrics(self):
        return {"requests_total": 0, "latency_p50": 0, "latency_p99": 0}

class FastAPIEndpointDeployment:
    """FastAPIEndpoint-based model deployment."""
    def __init__(self, model=None, model_path=None, **kwargs):
        self.model = model; self.model_path = model_path
        self.kwargs = kwargs
        self._running = False
    def deploy(self): self._running = True; return self
    def predict(self, inputs): return np.zeros((len(inputs), 1))
    def stop(self): self._running = False
    def health_check(self): return {"status": "healthy" if self._running else "stopped"}
    def get_metrics(self):
        return {"requests_total": 0, "latency_p50": 0, "latency_p99": 0}

class GRPCEndpointDeployment:
    """GRPCEndpoint-based model deployment."""
    def __init__(self, model=None, model_path=None, **kwargs):
        self.model = model; self.model_path = model_path
        self.kwargs = kwargs
        self._running = False
    def deploy(self): self._running = True; return self
    def predict(self, inputs): return np.zeros((len(inputs), 1))
    def stop(self): self._running = False
    def health_check(self): return {"status": "healthy" if self._running else "stopped"}
    def get_metrics(self):
        return {"requests_total": 0, "latency_p50": 0, "latency_p99": 0}

class DockerContainerDeployment:
    """DockerContainer-based model deployment."""
    def __init__(self, model=None, model_path=None, **kwargs):
        self.model = model; self.model_path = model_path
        self.kwargs = kwargs
        self._running = False
    def deploy(self): self._running = True; return self
    def predict(self, inputs): return np.zeros((len(inputs), 1))
    def stop(self): self._running = False
    def health_check(self): return {"status": "healthy" if self._running else "stopped"}
    def get_metrics(self):
        return {"requests_total": 0, "latency_p50": 0, "latency_p99": 0}

class DataVersionControl:
    def __init__(self, repo_path="./dvc_repo"):
        self.repo_path = repo_path; os.makedirs(repo_path, exist_ok=True)
        self.hashes = {}
    def track(self, path, name=None):
        name = name or os.path.basename(path)
        with open(path, "rb") as f: h = hashlib.sha256(f.read()).hexdigest()
        self.hashes[name] = {"path": path, "hash": h, "timestamp": time.time()}
        return h
    def status(self):
        return self.hashes
    def checkout(self, name, target_path):
        if name in self.hashes: return self.hashes[name]["hash"]
        return None

