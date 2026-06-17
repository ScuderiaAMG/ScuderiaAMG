# Hi there mate

A student at **Huazhong University of Science and Technology (HUST)**, School of Artificial Intelligence and Automation, majoring in Automation. Interests lie in **ROS robotics**, **reinforcement learning**, and **computer vision**.

*Escherichia30636* is personal codebase — a mix of coursework, competition projects, experiments, and the occasional surprise. The repo goes private during **January, June, July, and December** each year.

Fan of **Mercedes-AMG Petronas F1 Team** · Fan of **Lewis Hamilton**

> *Still we rise.*

escherichia30636@qq.com / taiyanchi157@gmail.com

---

## DQN-NATURE — Deep Reinforcement Learning for Atari

>`基于DQN的atari智能体的设计与实现原文件夹/`

Course design project. A from-scratch implementation of the DQN algorithm from the Nature 2015 paper *"Human-level control through deep reinforcement learning"* (Mnih et al.), trained on **Atari Breakout** for 50 million frames. Built with PyTorch and Gymnasium. Extended with prioritized experience replay on top of the paper's core mechanisms.

Training hardware: NVIDIA GeForce RTX 4090 D (24GB), Ubuntu 20.04, ~18GB VRAM usage, ~2 days for full 50M-frame run.

### Architecture

| File | Role | Paper Section |
|---|---|---|
| `model.py` | CNN: Conv(8x8, stride 4, 32) -> Conv(4x4, stride 2, 64) -> Conv(3x3, stride 1, 64) -> FC(512) -> Q-values (one per valid action). Matches the Nature architecture exactly. | Network architecture |
| `agent.py` | DQN agent: RMSprop (lr=2.5e-4, alpha=0.95, eps=0.01), epsilon-greedy (1.0 -> 0.1 over 1M frames, then fixed), gamma=0.99 | Behavior policy, optimizer |
| `atari_wrappers.py` | Atari env preprocessing pipeline — NoopReset (0-30 random no-ops), MaxAndSkip (frameskip=4, max over last 2 frames for flicker handling), WarpFrame (grayscale + 84x84 resize), FrameStack (stack 4 frames for temporal info). Entry: `make_atari(env_id)` | Input preprocessing |
| `replay_buffer.py` | Uniform experience replay — deque, 1M capacity, uniform random minibatch sampling (size 32) | Experience replay |
| `prioritized_replay_buffer.py` | Prioritized experience replay extension — TD-error-based sampling priority with importance-sampling weights to correct bias | Experience replay optimization (extension) |
| `train.py` | Core training loop — experience collection, minibatch sampling, gradient descent step on MSE loss, target network sync every 10K frames | Training algorithm |
| `main.py` / `main2.py` | Entry points — `main2.py` adds best-model checkpointing by episode reward | Experiment orchestration |
| `validate.py` / `validate2.py` | 30-episode rollout evaluation with `gym.wrappers.RecordVideo`, reports mean/std/max/min reward | Experimental validation |

### Training

```
# On Ubuntu 20.04
conda env create -f environment.yaml
conda activate dqn_nature
python main.py
```

Training loop: episode begins with random no-ops -> agent selects action (epsilon-greedy) -> 4-frame skip with max pooling -> grayscale + 84x84 + 4-frame stack -> transition stored in replay buffer -> once buffer > 50K, randomly sample batch of 32 -> compute target Q via target network -> MSE loss -> gradient clip at 10 -> RMSprop update -> sync target net every 10K frames. Epsilon decays linearly from 1.0 to 0.1 over the first 1M frames.

All paths are relative; training logs and model weights auto-save to `./dqn_nature/models/`.

### Experimental Results

Training on Breakout for 50M frames. Evaluation: 30 episodes, epsilon=0.05, 5-minute cap per episode.

| Game | Random | Linear Learner | DQN (this impl) | Human |
|---|---|---|---|---|
| Pong | -20.7 | -19.0 | 8.9 | 14.6 |
| Breakout | 3.2 | 3.0 | 255.0 | 31.7 |
| Space Invaders | 148.0 | 50.1 | 976 | 1652 |
| Seaquest | 68.4 | 664.8 | 3286 | 20182 |
| Enduro | 0.0 | 159.4 | 51.8 | 309.6 |

Paper's reported Breakout score: 316.8. This implementation reaches 255.0 (80% of paper), surpassing human level (31.7) by ~8x.

**Ablation study** (10M frames on Breakout):

| Configuration | Avg Score |
|---|---|
| Full DQN (replay + target net) | 255.0 |
| No target network (replay only) | 240.7 |
| No experience replay (target net only) | 10.2 |
| No replay + no target net | 3.2 |

Experience replay and target network separation are both critical; removing replay alone causes near-complete collapse, confirming both are essential for stable training.

### Outputs

- `models/dqn_breakout_best.pth` / `dqn_breakout_final.pth` / `dqn_breakout_final1.pth`
- `video/` — 30 rollout MP4s with JSON metadata
- `figures/validation_rewards_final10.png` — reward curve

---

## Python-Missions — Course Assignments & Side Projects

>`Python-Missions/`

Collection of projects for the "Python Programming" elective and beyond. Spans web scraping, image processing, GANs, super-resolution, and a full Pygame application.
Coursework and extended projects for the "Python Programming" course at the HUST School of Automation. The collection encompasses a comprehensive self-study Python curriculum, a deep learning framework implemented from scratch, image processing, GANs, YOLO object detection, Pygame applications, and physics experiments, totaling over 80,000 lines of code. ---

### Systematic Python Self-Study Course · `01_basics/` ~ `12_math_and_optimization/`

A comprehensive self-study roadmap for Python, covering everything from basic syntax to mathematics and optimization; includes 12 modules and 32 core scripts:

| # | Module | Content | Scripts |
|---|---|---|---|
| 01 | **Basics** | Basic syntax, data structures, object-oriented programming | `01_fundamentals.py`, `02_data_structures.py`, `03_oop.py` |
| 02 | **Intermediate** | Advanced functions, iterators, exception handling | `01_advanced_functions.py`, `02_iterators_and_errors.py` |
| 03 | **Advanced** | Concurrent programming, design patterns | `01_concurrency.py`, `02_design_patterns.py` |
| 04 | **Data Science** | NumPy basics, Pandas basics | `01_numpy_fundamentals.py`, `02_pandas_fundamentals.py` |
| 05 | **Machine Learning** | MLP/CNN from scratch, PyTorch networks, Transformer, unsupervised learning | `01_mlp_from_scratch.py`, `02_cnn_from_scratch.py`, `03_pytorch_networks.py`, `04_transformer.py`, `05_unsupervised_learning.py` |
| 06 | **Reinforcement Learning** | Q-Learning, DQN, Policy Gradient, PPO, MCTS, environment utilities | `01_q_learning.py` ~ `06_envs_and_utils.py` |
| 07 | **Algorithms** | Sorting & searching, graph algorithms, dynamic programming, advanced data structures | `01_sorting_searching.py` ~ `04_advanced_data_structures.py` |
| 08 | **Computer Vision** | Image processing basics | `01_image_processing.py` |
| 09 | **NLP** | Text processing, word embeddings | `01_text_processing.py`, `02_word_embeddings.py` |
| 10 | **Databases** | SQL and ORMs | `01_sql_and_orms.py` |
| 11 | **Software Engineering** | Design patterns and testing, Web and APIs, cryptography and security | `01_patterns_and_testing.py`, `02_web_and_api.py`, `03_cryptography_and_security.py` |
| 12 | **Math & Optimization** | Numerical methods, probability and statistics | `01_numerical_methods.py`, `02_probability_and_statistics.py` |

---

### Deep Learning Framework · `deep_learning_framework/`

A **complete deep learning framework implemented entirely from scratch** (~53,000 lines of pure Python/NumPy), covering the full stack of modern deep learning. 27 modules covering the entire workflow from low-level operators to MLOps:

| Module | Scope | Key Components |
|---|---|---|
| `layers.py` | Neural Network Layers | `Linear`, `Conv2d`, `BatchNorm`, `LayerNorm`, `RNN`, `LSTM`, `GRU`, `Transformer`, `Attention`, `Embedding`, `Dropout` |
| `models.py` | Model Collection | `MLP`, `CNN`, `ResNet`, `DenseNet`, `UNet`, `GAN`, `VAE`, `Diffusion`, `ViT`, `CLIP`, `LLaMA-style` |
| `activations.py` | Activation Functions | `ReLU`, `GELU`, `Swish`, `Mish`, `Softmax` |
| `losses.py` | Loss Functions | `MSE`, `CrossEntropy`, `Focal`, `Contrastive`, `Triplet`, `Dice` |
| `optimizers.py` | Optimizers | `SGD`, `Adam`, `AdamW`, `LAMB`, `Lion`, `RMSprop` |
| `regularization.py` | Regularization | `Dropout`, `DropPath`, `StochasticDepth`, `LabelSmoothing`, `Mixup`, `CutMix` |
| `cv.py` | Computer Vision | Filters (Gaussian/Median/Bilateral), Edge Detection, Data Augmentation, IoU/NMS |
| `nlp.py` | Natural Language Processing | `Tokenizer` family (Whitespace/Character/BPE), TF-IDF, Sequence Labeling, Text Data Augmentation |
| `rl.py` | Reinforcement Learning | `ReplayBuffer`, `PrioritizedReplayBuffer`, N-Step, PER, NoisyNet support |
| `gnn.py` | Graph Neural Networks | `GraphConv`, `GAT`, `GIN`, `GraphSAGE`, Message Passing Framework |
| `multimodal.py` | Multimodal | Image-Text Fusion, Cross-modal Attention, Audio-Visual Alignment |
| `timeseries.py` | Time Series | LSTM/Transformer Forecasting, Sequence Decomposition, Anomaly Detection |
| | `tables.py` | Tabular data | TabNet-style attention, feature embeddings, mixture density networks (~27K lines) |
| `signal.py` | Signal processing | Wavelet transform, FFT, filtering, time-frequency analysis |
| `bioinformatics.py` | Bioinformatics | Sequence encoding, contact map prediction |
| `classic_ml.py` | Classic ML | KMeans, GMM, decision trees, HMM, CRF, t-SNE, UMAP |
| `features.py` | Feature engineering | Binning, Target Encoding, CatBoost Encoding, mutual information, PCA/kPCA |
| `data_utils.py` | Data processing | Dataset/DataLoader, data cleaning pipelines, augmentation pipelines |
| `metrics.py` | Evaluation metrics | Classification/regression/ranking/generation metrics, statistical tests |
| `automl.py` | AutoML | Hyperparameter search (Random/Grid/Bayesian/HyperBand), NAS, model selection, feature selection |
| `distributed.py` | Distributed training | DataParallel, DistributedDataParallel, parameter server, Ring AllReduce |
| `mlops.py` | MLOps | Experiment tracking, model registry, A/B testing, feature store, drift detection, deployment pipelines |
| `security.py` | Security | Adversarial examples (FGSM/PGD/C&W), membership inference, differential privacy, model watermarking |
| `examples.py` | Examples | MNIST/CIFAR/IMDB classification examples, object detection, image segmentation |
| `utils.py` | Utilities | `save`/`load`, progress bars, learning rate schedulers, weight initialization |
| `weights_db.py` | Model repository | Pre-trained weights database, version management, automatic download (~6,565 lines) |

**Design Philosophy**: NumPy-only backend; `Module` → `Parameter` → automatic differentiation; API style closely resembles PyTorch. All modules can be used independently without installing any deep learning frameworks. ---

### Agricultural Drone Pesticide Spraying Simulation System · `Test3/`

An interactive simulator for agricultural drone pesticide spraying, powered by Pygame:

| File | Role |
|---|---|
| `main.py` | Program entry point |
| `app.py` | `FarmDroneApp` — Main control loop, 60 FPS, state machine (welcome → login/register → main → exit) |
| `drone.py` | `Drone` class — Drone movement model and rendering |
| `field.py` | `Field` class — Grid-based modeling and visualization of the farmland |
| `pesticide.py` | `PesticideManager` — Pesticide spray coverage and dissipation model |
| `path_planning.py` | `PathPlanner` — Drone path planning algorithm |
| `auth.py` | `AuthSystem` — User login/registration (JSON persistence) |
| `animation.py` | `AnimationSystem` — Opening/closing animation system |
| `utils.py` | Utility functions |

### Pygame Full-Stack Application Framework · `Test3demo/`

A complete Pygame application template featuring a multi-screen architecture (MVC + Screen state machine) that includes a welcome animation, login/registration screens, the main simulation interface, and a closing animation. Each screen is modularized under `ui/screens/`, and logging is centralized via `utils/logger.py`. ---

### Pure NumPy GAN · `GAN/1.py`

Building a **pure NumPy** Generative Adversarial Network from scratch—no PyTorch or TensorFlow:

- `Linear`, `ReLU`, and `Sigmoid` layers + manual forward/backward passes
- Binary Cross Entropy analytical gradients + `Sequential` chain-rule backpropagation
- Generator: latent (4D) → hidden (16, ReLU) → 2D output
- Discriminator: 2D → hidden (16, ReLU) → 1D probability (Sigmoid)
- Alternating G/D training for 2000 epochs

Objective: To understand the internal mechanisms of GANs and their connection to GAIL (Generative Adversarial Imitation Learning). The real data distribution is set as a Gaussian distribution with a mean of [5, 5], simulating expert state-action demonstrations.


### Image Processing and Super-Resolution · `pic.py/`

| Script | Function |
|---|---|
| `pic.py` | Selective color inversion — reverses only grayscale pixels (R, G, and B values ​​within a tolerance range), leaving others unchanged.


---

## horizon_haarcascade — FH5 Auction Sniper & Face Detection

>`horizon_haarcascade/`

A dual-project folder combining Forza Horizon 5 auction automation with OpenCV Haar cascade face detection experiments. The name is a portmanteau: Forza **Horizon** + **Haar Cascade**.

### Forza Horizon 5 Auction Buyout Sniper · `main.py`

The source code for the compiled EXE in `极限竞速：地平线5刷车脚本/`. A sophisticated game automation script that uses OpenCV template matching to navigate Forza Horizon 5's auction house and snipe car listings.

| Aspect | Detail |
|---|---|
| **Image recognition** | `cv2.matchTemplate` with `TM_CCOEFF_NORMED`, threshold 0.8. Template images in `images/` (SA, CF, AT, BF, PB, BS, NB, VS, AO — each representing a UI element) |
| **Input simulation** | `pydirectinput` for key presses (DirectInput bypasses game anti-cheat), `pyautogui` for mouse movement and screenshot capture |
| **Window management** | `pygetwindow` for game window detection, resize to 1616x939, focus/activate |
| **Car database** | Reads `FH5_all_cars_info_v3.xlsx`, filters cars with `BUYOUT NUM > 0`, iterates through sniping targets. Updates Excel in real-time after each successful buyout |
| **UI navigation** | Full state machine: Search Auction -> Confirm Car -> check Auction page -> Place Bid -> confirm Buyout Success/Fail -> loop. Navigates car brand/model grid via `go_to_MAKE()` using coordinate offsets |
| **Timeout/error handling** | 30-minute per-car timeout, auto-switch to next target. ESC-based stuck recovery with 10-retry cap. Colored terminal output (`colorama`) for status visibility |

**Requirements**: Windows, 1920x1080 screen + game resolution, 60Hz+, English game locale. Dependencies (`sourcelist.txt`): opencv-python, numpy, pandas, openpyxl, pyautogui, pydirectinput, pygetwindow, colorama.

```
pip install opencv-python numpy pandas openpyxl pyautogui pydirectinput pygetwindow colorama
python main.py
```

### Real-time Face Detection with Haar Cascades

Four OpenCV scripts exploring webcam-based face detection using `haarcascade_frontalface_default.xml`:

| Script | Function |
|---|---|
| `camera_video_box.py` | Basic real-time face detection — draws red bounding boxes around detected faces |
| `camera_face_posi.py` | Face detection with coordinate logging — prints (x, y, w, h) for each detected face |
| `camera_face_posi0.py` | Mirror-mode detection — horizontally flips the frame (`cv2.flip(frame, 1)`), prints both normal and mirror coordinates. Useful for mirror-based UI interactions |
| `camera_face_pict.py` | Face replacement — overlays an image (`deepseek.jpg`) onto detected face regions. Resizes overlay to match each face bounding box |

All four use `scaleFactor=1.1, minNeighbors=5, minSize=(30,30)` and exit on 'q' key press.

---

## CSIG-VI — Low-Light Image Enhancement

>`CSIG-VI/`

2025 "Camera Academic Star" Imaging Algorithm Technology Competition entry. Three model variants targeting low-light image enhancement, from unsupervised to fully supervised approaches. Target hardware: RTX 4060 (8GB VRAM), PyTorch 2.0.1 with CUDA 11.7/11.8.

### DarkVisionNet (`DarkvisionNet.py`)

Unsupervised dual-branch architecture with physics-guided attention:

| Component | Architecture |
|---|---|
| `PhysicalGuidedAttention` | Fuses luminance distribution (Conv -> Sigmoid) with noise level estimation (variance pooling) to generate content-aware attention weights |
| `MultiScaleResidualBlock` | Three parallel convolutions (3x3, 5x5, 7x7) -> fusion -> PhysicalGuidedAttention gating -> residual connection. 8 blocks stacked. |
| `EnhancementBranch` | Encoder-decoder: Conv 64 -> Conv 128 (stride 2) -> Conv 256 (stride 2) -> 8x MultiScaleResidualBlock -> ConvTranspose 128 -> ConvTranspose 64 -> Conv 3 (Sigmoid) |
| `DenoisingBranch` | 5-layer Conv-BN-ReLU stack (64 channels, 3x3 kernels), no downsampling — preserves fine detail |
| `DarkVisionNet` | Runs both branches in parallel, concatenates outputs (6 channels), fuses via Conv 32 -> Conv 3 (Tanh), adds residual to input, clamps to [0,1] |

**Training**: Self-supervised (input = target), patch-based (256x256), synthetic darkening augmentation (gamma 1.5-3.0, additive Gaussian noise). Loss = MSE + 0.5*SSIM + 0.1*ColorConsistencyLoss. Adam optimizer with CosineAnnealingLR. 4-day time limit built into training loop.

```
python DarkvisionNet.py --input_dir <path> --epochs 100 --batch_size 8
```

### RD-DualNet (`RD-DualNet.py` / `RD-DualNet2.py`)

Supervised approach — directly learns the mapping from low-light to Ground Truth. Key innovation: **Retinex-DCP Guided Attention** that fuses physical priors with learned features.

| Component | Architecture |
|---|---|
| `DepthwiseSeparableConv` | Depthwise conv (groups=in_channels) + pointwise conv (1x1) + BN + ReLU — mobile-friendly |
| `SEBlock` | Squeeze-and-Excitation channel attention with reduction=16 |
| `RetinexDCPGuidedAttention` | Estimates Retinex reflectance R (detail) via 2-layer Conv and DCP prior (illumination/noise) via 2-layer Conv, fuses with backbone features to produce attention weights |
| `LightweightMultiScaleBlock` | 3 parallel DepthwiseSeparableConv (3x3, 5x5, 7x7) -> SEBlock -> 1x1 fusion -> RetinexDCPGuidedAttention gating -> residual |
| `RD_DualNet` | Shared shallow feature extractor (Conv 64) -> Enhancement branch (4x LightweightMultiScaleBlock, detail/brightness focus) + Denoising branch (3x DepthwiseSeparableConv + SEBlock, smoothness/noise suppression) -> feature concatenation -> Conv 1x1 -> Conv 3x3 (Tanh) -> residual output |

**v2 fixes** (`RD-DualNet2.py`): Replaced `nn.Sequential` with `nn.ModuleList` for proper forward iteration through enhance blocks; added VGG denormalization `[-1,1] -> [0,1]` before perceptual loss computation; added post-training color calibration via least-squares linear regression (`evaluate_and_tune`: learns a 3x3 gain matrix + 3x1 bias from evaluation pairs).

**Training**: Supervised paired dataset (`PairedDataset` — low_dir + high_dir), patch-based (256x256, paired random crops). **HybridLoss** = L1 (pixel fidelity) + 0.1*Perceptual (VGG16 features up to relu4_3) + 0.05*GT-Mean (global brightness alignment). AdamW (lr=2e-4, weight_decay=1e-4), CosineAnnealingLR (T_max=100, eta_min=1e-6), gradient clipping at 1.0. Modes: `--mode train` or `--mode enhance` (post-training inference with learned color correction).

```
python RD-DualNet2.py --mode train --low_dir <path> --high_dir <path> --epochs 100 --batch_size 16
python RD-DualNet2.py --mode enhance --eval_dir <path> --input_dir <path>
```

### Infrastructure

| File | Purpose |
|---|---|
| `config.py` | CUDA optimization (TF32, cuDNN benchmark, mixed precision hint), training config (gradient accumulation, num_workers), memory config (max_split_size_mb, GC threshold) |
| `install_darkvision.sh` | One-click env setup: detects Ubuntu version, CUDA version, creates venv, installs PyTorch with correct CUDA index, runs `test_environment.py` |
| `test_environment.py` | Environment validation: Python/PyTorch/CUDA/OpenCV/NumPy/Skimage versions, GPU tensor op test |
| `monitor_resources.py` | Real-time CPU/GPU monitoring daemon thread — psutil for CPU/RAM, gpustat for GPU utilization/memory/temperature |
| `image_enhance1.py` | Standalone inference script for DarkVisionNet — batch processes a folder, preserves original resolution |

---

## PINN_CNN — Dual AI Battery SOH Estimation for RA8+RZ/G2L

>`PINN_CNN/`

A dual-model battery state-of-health (SOH) estimation system built for the Renesas RA8 (Cortex-M85) + RZ/G2L (Cortex-A55) dual-chip architecture. Part of an industrial-grade lithium battery aging test and high-reliability data black-box system. Two complementary AI models: a physics-informed neural network for fast screening and a residual 1D-CNN for precise assessment.

| Model | Chip | Task | Input | Output | Params | A55 Latency |
|---|---|---|---|---|---|---|
| PINN | RZ/G2L | SOH regression | 132-d features | SOH ∈ [0,1] | ~53K | < 15 ms |
| CNN | RZ/G2L | 3-stage + RUL | (2, 128) IC dual-channel | healthy/degrading/EOL + RUL | ~44K | < 15 ms |

**Pipeline**: production-line fast screening (8-minute charge data → PINN → SOH) → cascaded sorting (full charge → CNN → health grade + remaining useful life).

### PINN — Physics-Informed Neural Network (`pinn/`)

A compact MLP with residual skip connections, trained with physics-based regularization on top of standard MSE. Input is a 132-d vector: IC curve (128 points on 2.8–3.6V grid) + temperature + log cycle count + dV proxy + measured capacity.

| Component | Detail |
|---|---|
| Architecture | Linear(132→128) → Linear(128→128) → Linear(128→64) → ResidualBlock(64) → dual head: SOH (Sigmoid) + aux resistance proxy |
| Physics loss | **ECM consistency** (MSE between predicted R and dV measurement) + **degradation smoothness** (2nd-order SOH penalty across cycles) + **monotonicity** (ReLU penalty on SOH rise). Weights: 0.15 / 0.05 / 0.02 |
| Training | AdamW (lr=5e-4, wd=1e-5), ReduceLROnPlateau, AMP mixed precision, gradient clip 1.0, 600 epochs, batch 256, early stop 80 |
| Data | NASA PCoE (.mat, cells B0005/6/7/18) + CALCE Arbin (.xlsx, CS2_35/36/37/38). Falls back to LFP 18650 2-RC ECM synthetic data (`battery_sim.py`) if real data unavailable |
| Performance | Test MAE < 1% SOH, R² > 0.99 |
| Export | PyTorch → ONNX opset 14 → INT8 dynamic quantization (83 KB) |

### CNN — Residual 1D-CNN for Precise Assessment (`cnn/`)

A slim residual conv net performing joint 3-stage classification and RUL regression. Dual-channel input: IC curve + IC gradient (d(IC)/dV), each (128,) — stacked as (2, 128).

| Component | Detail |
|---|---|
| Architecture | Stem Conv1d(2→16, k=7, s=2) → 3× ResidualBlock (16→32→48, k=7/7/5) with MaxPool → AdaptiveAvgPool1d → dual heads: classification (48→48→24→3) + RUL regression (48→48→24→1) |
| Stages | healthy (SOH ≥ 0.82), degrading (0.82 > SOH ≥ 0.70), EOL (SOH < 0.70) |
| Training | AdamW (lr=8e-4, wd=1e-4), CrossEntropyLoss (inverse-frequency class weights, label smoothing 0.08) + MSELoss(RUL), weights 0.55/0.45, AMP, 600 epochs, batch 128, early stop 100 |
| Augmentation | Gaussian noise (σ=0.03), random scale (0.85–1.15), voltage-axis shift (±6 points) — training only |
| Data split | Cell-based split (no cross-contamination), quality filtering (rejects flat/degenerate IC curves), ~70/15/15 train/val/test |
| Performance | Test accuracy ~70%, RUL MAE 0.21 |
| Export | PyTorch → ONNX opset 14 → INT8 dynamic quantization (84 KB) |

### RZ/G2L Deployment (`deploy/`)

ONNX Runtime CPU execution on dual Cortex-A55 @ 1.2 GHz:

```
python3 inference.py pinn  sample_132d.npy    # → SOH: 0.9234 (92.3%)
python3 inference.py cnn   ic_curve_128.npy   # → Stage: healthy (0), RUL: 0.8764
python3 inference.py benchmark                 # → PINN: 8.2 ms, CNN: 7.5 ms
```

Python API via `PINNInference` and `CNNInference` classes. RA8 ↔ RZ/G2L communication over QSPI/USB HS with shared memory. Full data loop: RA8 collects voltage/current/temperature → Kalman filter + IC/DV feature extraction → RZ/G2L runs inference → results stored to Octa-NAND + displayed on UI.

### Deployment Documentation

| File | Content |
|---|---|
| `RZG2L_CPP_DEPLOY.md` | 完整 C++ 推理引擎部署教程 — Ubuntu 20.04 ARM64 系统初始化 → ONNX Runtime 1.18+ 源码编译 (ARM NEON) → C++17 `libbattery_inference.so` 双模型推理接口 → CMake 构建部署 |
| `RZG2L_GUI_DEPLOY.md` | Qt 6.5 LTS 图形化交互界面部署 — Mali-G31 GPU DRM/KMS 显示 → eglfs QPA → QML 仪表盘 → 电池推理引擎集成 |
| `export_scalers.py` | StandardScaler 参数导出脚本 → 供 C++ 推理端标准化输入特征 |

### Data Sources

- **NASA PCoE**: 4 cells (B0005/6/7/18), `.mat` format, nested cell-array structure, charge/discharge curves at multiple temperatures
- **CALCE**: 4 cells (CS2_35/36/37/38), `.xlsx` Arbin format, multi-sheet per file, first-load caching to `.npz`
- **Synthetic**: `pinn/battery_sim.py` — LFP 18650 2-RC ECM simulator with power-law capacity fade, resistance growth, CC charging with noise

```
data/
├── nasa_pcoe/      B0005.mat, B0006.mat, B0007.mat, B0018.mat
└── calce/          CS2_35/, CS2_36/, CS2_37/, CS2_38/  (Arbin .xlsx)
```

Detailed documentation, training instructions, and hyperparameter tuning guide: `PINN_CNN/README.md`.

Accompanying documents:
- `基于瑞萨RA8+RZ_G2L双芯架构的工业级锂电池老化测试与高可靠数据黑匣子系统项目建议书.pdf` — full project proposal
- `RA8 Octa-NAND file system support2026.docx` — NAND flash storage design notes

---

## MCM — Mathematical Contest in Modeling

>`MCM/`

COMAP's Mathematical Contest in Modeling (MCM) and Interdisciplinary Contest in Modeling (ICM) — 2025 and 2026 competition materials, including problem sets, solution approaches, and complete project submissions.

### 2026 MCM-ICM Project · Problem C (DWTS Analytics)

`2026_MCM-ICM_Project/PRJ/` and `PJT/`

Full analysis of **Dancing with the Stars (DWTS)** competition data across Seasons 1-34. The project is structured around three sub-problems:

**PJT/1 — Vote Share Prediction** (`q1.py`):

Machine learning pipeline to estimate celebrity vote shares from judge scores and metadata:

- **Data**: `2026_MCM_Problem_C_Data.csv` -> `2026_MCM_Problem_C_Processed_Data.xlsx` (34 seasons, 2218 training samples after long-format transformation)
- **Feature engineering**: Judge score totals per week, score deltas, 2-week rolling averages, elimination status, industry one-hot encoding, age, season/week indices — 34 features total
- **Models**: XGBoost and LightGBM regressors trained head-to-head (300 estimators, max_depth=6, lr=0.05). Best model selected by RMSE comparison
- **Post-processing**: Vote shares normalized per season-week group (sum to 1.0), uncertainty estimates (0.05 base, 0.08 for eliminated contestants)
- **Outputs**: `predicted_vote_shares.csv`, `predicted_vote_shares_sorted.csv`, `EP_FROM_Model_Final_Results.xlsx`, model_summary.txt (Test RMSE: 0.0130)
- **Visualizations** (`pic.py`, `pic2.py`): Season trajectory plots, bump charts, feature importance, score density distributions, competition overview dashboards

**PJT/2 — Elimination Rule Analysis** (`rule_comparison.py`, `controversy_analysis.py`, `producer_recommendations.py`):

- Compares alternative elimination rules (rank-based vs. percentage-based) across 34 seasons
- Identifies 106 weeks where different rules would produce different elimination outcomes
- Bias analysis: rank method correlation with fan popularity = 0.8108 vs. percentage method = 0.6794
- Producer recommendation system outputs to `producer_recommendation.txt`

**PJT/3 — Method Comparison** (`q3-1.py`, `q3-1-1.py`):

- Systematic comparison of voting methods and their impact on competition fairness
- `Method_Comparison_Summary.txt` documents findings

### 2025 MCM-ICM Reference Materials

| Resource | Content |
|---|---|
| `2025_MCM_Problem_A/B/C.pdf` | Original problem statements |
| `2025_ICM_Problem_D/E/F.pdf` | Original ICM problem statements |
| `MCM2025A/B/C/D-O奖经验谈.pdf` | Outstanding-prize winner experience sharing |
| `MCM2025A/B/C/D-赛题解析.pdf` | Problem analysis and solution approaches |
| `建模基础.pdf` | Modeling fundamentals textbook |
| `综合评价及预测.pdf` | Comprehensive evaluation and forecasting methods |

### 2025 Python Workshop (`2025美赛Python使用心得分享/`)

A curated collection of Python scripts demonstrating common MCM modeling techniques:

| Script | Technique |
|---|---|
| `线性回归.py` | Linear regression with scikit-learn |
| `支持向量机_二元分类.py` / `支持向量机_回归.py` | SVM for classification and regression |
| `Kmeans.py` | K-means clustering |
| `time_series_demo.py` | Time series analysis (AirPassengers, financial data) |
| `salary_regression.py` | Regression on Salary_Data with statistical diagnostics |
| `数据预处理-缺失值.py` | Missing value imputation strategies |
| `最优化.py` | Numerical optimization |
| `一维插值.py` | 1D interpolation methods |
| `合并.py` | Data merging/joining |
| `2023C_handling_data.py` | Practical data cleaning on 2023 Problem C dataset |
| `画线图.py` / `画曲面图.py` / `画等值线图.py` / `画灰度图.py` | matplotlib visualization gallery |
| `my_module.py` / `my_own_file.py` | Custom module packaging examples |

---

## Robotics

### ROS Workspace · 

>`一个不知道哪来的工作空间/`

ROS Noetic workspace for drone autonomy. 9 packages under `src/`, built with Catkin/CMake.

| Package | Function |
|---|---|
| `bringup` | Launch files, PX4 config, costmap/planner parameters (global, local, DWA), move_base configuration |
| `drone_manager` | Cruise control state machine |
| `fly_ctl` | Low-level flight control |
| `mission` | Mission patterns — cross and endurance flight plans |
| `cloud_recognition` | Cloud and projector screen detection (`obs.yaml`, `plane_config.yaml`) |
| `ring_detector` | Visual ring detection with map accumulation and plane area filtering |
| `yolov8_ros` | YOLOv8 object detection + ByteTrack/Bot-SORT tracking, integrated as ROS node |
| `web_video_server` | Web-based video streaming from ROS topics |
| `usb_cam` | USB camera ROS driver |
| `template` | Package template for new nodes |

### WheelRobots · `WheelRobots/`

Webots wheeled robot controllers and simulation worlds.

---
## Running — HUST Sports GPS Running Simulator

>`Running/`

An automation tool for campus running check-ins. It generates simulated GPS running tracks along HUST campus routes to complete the "HUST Sports" app's extracurricular running requirements. Constraints: Distance ≥3.5 km per run; pace 4:00–10:00 min/km.

| File | Role |
|---|---|
| `run.py` | Rich TUI interactive version — track preview, GPX export, real-time ADB simulation, device diagnostics |
| `run_cli.py` | Pure CLI version — zero third-party dependencies; suitable for SSH, remote, or background execution |
| `routes/` | Campus route JSON definitions (GPS coordinate sequences); supports custom routes |
| `mumu_gps.py` | GPS injection solution for MuMu Emulator |
| `analyze_app.py` | App behavior analysis tool |
| `core/` | Core track generation and GPS simulation engine |

**Two usage methods**:
- **GPX Export (Recommended)**: Pre-generate GPX tracks on PC → Import and play back via a "Mock GPS" app on the phone; compatible with all devices.
- **Real-time ADB Simulation**: PC injects GPS coordinates into the phone via USB every second; supported only by specific ROMs.

Automatically meets pace requirements (4:00–10:00 min/km) and distance requirements (≥3.5 km). ### Remote Deployment

| Solution | Description |
|---|---|
| Local Server | Old laptop or Raspberry Pi running Linux + ADB; phone connected via USB and kept on 24/7; remote control via SSH |
| Windows SSH | Install OpenSSH Server via PowerShell (Administrator); remote control over the same Wi-Fi network |

```
# GPX Export
python run_cli.py -p 5.5 --gpx route.gpx

# Unattended Background Execution
nohup python3 run_cli.py -p 5.5 -l 2 -y > run.log 2>&1 &
```

---

## CSIEC — Collaborative Perception and Planning for Multi-Unmanned Systems

>`CSIEC/`

A project entry for the China International College Students' "Internet+" Innovation Competition (CSIEC)—focusing on collaborative perception, planning, and path planning for multi-unmanned systems (UGV + UAV). Includes the complete project proposal, presentation slides, and a guide for secondary development on the Unitree Go2 robot dog. | File | Content |
|---|---|
| `多无人系统协同感知与规划-项目申请书.pdf` | Formal project proposal |
| `多无人系统协同感知、规划（有图片）-项目.docx` | Detailed project document with illustrations |
| `duowurenxitong_defense_20260522_212848.pptx` | Project defense presentation (PPT) |
| `连接宇树Go2 开发版（EDU版）的扩展坞进行二次开发.md/pdf` | Unitree Go2 (EDU version) development guide — physical connection, network configuration (192.168.123.18), SSH login, SDK installation and testing |

### AirHust · `AirHust/`

C++ algorithm suite for UAV/robot collision avoidance — implementations and variants of various collision avoidance strategies:

| Script | Variant |
|---|---|
| `collision_avoidance.cpp` | Standard collision avoidance |
| `collision_avoidance_alpha.cpp` / `_alpha2.cpp` | Alpha variant |
| `collision_avoidance_beta.cpp` | Beta variant |
| `collision_avoidance_plus.cpp` | Enhanced version |
| `collision_avoidance_basic.cpp` | Basic/streamlined version |
| `collision_avoidance_mod.cpp` | Modified version |
| `crossing_door_darknet.cpp` | Darknet-based doorway detection |
| `integrated_test.cpp` / `integrated_work.cpp` | Integrated testing and comprehensive solution |
| `aia_collision_avoidance.cpp` | AIA (Aerial Intelligent Agent) competition version |

---

## Coursework

`人工智能导论/` · `信号与系统/` · `数据结构/` · `自动控制原理/` · `运筹学/` · `计算方法/` · `大学物理/` · `模拟电路/` · `数字电路/` · `微机原理/` · `离散数学/` · `复变函数与积分变换/` · `单片机/` · `文献检索与科技论文写作/` · `大学生社会实践/` · `数电实验/` · `模电实验/` · `电路实验/` · `物理实验复习/` · `自动控制原理实验/` · `电子技术课程设计实验/` · `马克思主义基本原理/` · `CET6/Reading Materials for the Independent Assessment of SARS-CoV-2 Origins`


---

## Other Projects

| Project | Description |
|---|---|
| `极限竞速：地平线5刷车脚本/` | Forza Horizon 5 auction house automation — compiled EXE + Excel car database. Source code at `horizon_haarcascade/main.py`. Requirements: 1920x1080, 60Hz+, English locale. |
| `爬呀爬/` | Python web video crawler — `test_download.py` / `test_download2.py` / `test_download3.py` with duration filtering, custom download directory, max_pages limiting |
| `设计一个小玩意/` | PCB / schematic design |
| `C/` | C programming (`test.c`, HLCM algorithms in `hlcm.md`), 机器学习西瓜书 PDF |
| `java/` | Java OOP — `Main.java` with Student class |
| `Claude~Claude!/` | PyQt5 桌面 AI 宠物 — 文件拖拽 + 自然语言问答，调用 DeepSeek API (deepseek-v4-pro)，带思维链 (Reasoning) 解析，可拖动悬浮窗 |
| `仙人指路/` | 网络配置规则列表 (`kr.list`, `list.list`) |
| `BorlandCpp3.1_DOSBOX纯净版/` | Borland C++ 3.1 for DOSBOX — HUST 自动化学院 C 语言课程设计专用编程环境（VBS 虚拟机纯净版） |
| `build/` · `tmp_pdf/` | Build artifacts and temporary PDF processing |
| `人工智能与自动化学院官网首页/` | 学院新闻中心工作 — 成员名单、HTML 页面设计 (`aia.html`)、高考/国庆推文策划、竞选稿、明信片设计 |
| `华科ppt模板/` | HUST 官方 PPT/简历模板（含 2022 校庆配色版） |
| `一些论文/` | 学术论文收集 — 多机器人协同、SLAM、图像去噪、圆检测算法等 |
| `DatasetForEliterace/` | EliteRace 竞赛数据集 — 图像采集样本 |
| `atari智能体_被淘汰模型表现/` | Atari DQN 训练中被淘汰的中间模型 (dqn_401, dqn_preview) |
| `一些不知道如何归类的东东/` | 党支部材料 — 积极分子材料填写指南、工作方案等 |

---

## Tech Stack

**Languages:** Python · C/C++ · Java

**ML/DL:** PyTorch 2.x · XGBoost · LightGBM · scikit-learn · NumPy · OpenCV · Gymnasium · Real-ESRGAN · Ultralytics YOLOv12 · ONNX / ONNX Runtime · TensorBoard

**Robotics:** ROS Noetic · Webots · Catkin/CMake · Renesas RA8 (Cortex-M85) · RZ/G2L (Cortex-A55) · Unitree Go2

**Domain:** Battery SOH Estimation · PINNs · ECM (2-RC) · IC/DV Analysis · Embedded AI (INT8 Deployment) · Multi-Robot Collaboration

**GUI/Embedded:** Qt 6.5 LTS (eglfs/QML) · PyQt5 · ARM NEON · Mali-G31 GPU

**Tools:** VS Code · MSYS2/MinGW64 · Anaconda · ChromeDriver/Selenium · Pygame · pandas · matplotlib · Git
