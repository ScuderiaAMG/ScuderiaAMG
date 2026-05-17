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

Collection of projects for the 《Python程序设计》 elective and beyond. Spans web scraping, image processing, GANs, super-resolution, and a full Pygame application.

### Pure NumPy GAN · `GAN/1.py`

A minimalist Generative Adversarial Network built **entirely in NumPy** — no PyTorch/TensorFlow. Implements from scratch:

- `Linear`, `ReLU`, `Sigmoid` layers with manual forward/backward pass
- Binary Cross Entropy loss with analytical gradient computation
- `Sequential` container with chain-rule backpropagation through arbitrary layer stacks
- Generator: latent (4D) -> hidden (16, ReLU) -> 2D output (continuous action space analogue)
- Discriminator: 2D -> hidden (16, ReLU) -> 1D probability (Sigmoid)
- Full training loop alternating D and G updates for 2000 epochs

Aimed at understanding GAN internals and the connection to GAIL (Generative Adversarial Imitation Learning) in RL. The real data distribution is set to a Gaussian with mean [5, 5], simulating expert state-action demonstrations.

### Image Processing · `pic.py/`

| Script | Function |
|---|---|
| `pic.py` | Selective color inversion — reverses only grayscale pixels (R~G~B within tolerance), leaves colored regions untouched. Uses NumPy boolean masking. |
| `res.py` | Real-ESRGAN super-resolution pipeline — RRDBNet (23 RRDB blocks, 64 features), FP16 inference, tile-based processing (256px tiles for 8GB VRAM), auto model download from GitHub releases. `enhance_image()` function with configurable outscale and tile_size. |
| `ai_upscale.py` | Alternative AI upscaling approach |
| `pro_upscale.py` / `upscale2.py` / `upscale3.py` | Upscaling variants with different model configurations |
| `realesrgan-ncnn-vulkan-20220424-windows/` | Real-ESRGAN ncnn Vulkan executable — native Windows GPU inference without Python overhead. Includes x2/x3/x4 anime and general models. |
| `check.py` | Image quality check utility |
| `tree.py` | File tree visualization |
| Physics experiment scripts | `光电管伏安特性曲线.py`, `弗兰克-赫兹实验.py`, `零电流法测定普朗克常数h和红限频率.py`, `饱和光电流与入射光强的关系.py` — experimental data plotting with matplotlib |

### Web Scraping · `demo.py`

Selenium + BeautifulSoup crawler for scraping the **ShanghaiRanking 2025 Chinese University Rankings** (软科中国大学排行榜). Features:

- Anti-detection: `--disable-blink-features`, `excludeSwitches`, navigator.webdriver spoofing
- Auto-scroll to trigger lazy loading, with max-attempt cap and height-change detection
- "Load more" button detection with JS click fallback
- Chinese university name extraction (handles mixed img+text cells, regex for CJK characters)
- pandas DataFrame output with rank/name/location/type/score columns

### Basic Exercises

`TEST1.py`, `TEST1-1.py`, `TEST2.py`, `practice1_1.py` through `practice1_4.py`, `test.py`, `test0.py`, `test_snippet.py`, `zz.py`, `block_diagram_step_1` — fundamental Python programming exercises covering data structures, algorithms, file I/O, and control flow.

---

## horizon_haarcascade — FH5 Auction Sniper & Face Detection

`horizon_haarcascade/`

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

### AirHust · 

>`AirHust/`

Webots-based UAV collision avoidance in C++. 15+ controller iterations showing algorithm evolution:

- `collision_avoidance_basic.cpp` -> `collision_avoidance_alpha.cpp` / `_beta.cpp` / `_alpha2.cpp` -> `collision_avoidance_plus.cpp` -> `integrated_work.cpp`
- `crossing_door_darknet.cpp` — door crossing with Darknet-based detection
- `slam_test.cpp` — SLAM integration testing
- `distance_test_mod1.cpp` — distance sensor calibration

### WheelRobots · `WheelRobots/`

Webots wheeled robot controllers and simulation worlds.

---

## Coursework

`人工智能导论/` · `信号与系统/` · `数据结构/` · `自动控制原理/` · `运筹学/` · `计算方法/` · `大学物理/` · `模拟电路/` · `数字电路/` · `微机原理/` · `离散数学/` · `复变函数与积分变换/` · `单片机/` · `文献检索与科技论文写作/` · `大学生社会实践/` · `数电实验/` · `模电实验/` · `电路实验/` · `物理实验复习/` · `自动控制原理实验/`

---

## Other Projects

| Project | Description |
|---|---|
| `CSIEC/` | Multi-UAV collaborative perception & planning — research proposal documents, Unitree Go2 EDU SDK development guide |
| `极限竞速：地平线5刷车脚本/` | Forza Horizon 5 auction house automation — compiled EXE + Excel car database. Source code at `horizon_haarcascade/main.py`. Requirements: 1920x1080, 60Hz+, English locale. |
| `爬呀爬/` | Python web video crawler — `test_download.py` / `test_download2.py` / `test_download3.py` with duration filtering, custom download directory, max_pages limiting |
| `设计一个小玩意/` | PCB / schematic design |
| `C/` | C programming (`test.c`, HLCM algorithms in `hlcm.md`), 机器学习西瓜书 PDF |
| `java/` | Java OOP — `Main.java` with Student class |
| `build/` · `tmp_pdf/` | Build artifacts and temporary PDF processing |

---

## Tech Stack

**Languages:** Python · C/C++ · Java

**ML/DL:** PyTorch 2.x · XGBoost · LightGBM · scikit-learn · NumPy · OpenCV · Gymnasium · Real-ESRGAN · Ultralytics YOLO

**Robotics:** ROS Noetic · Webots · Catkin/CMake

**Tools:** VS Code · MSYS2/MinGW64 · Anaconda · ChromeDriver/Selenium · Pygame · pandas · matplotlib · Git
