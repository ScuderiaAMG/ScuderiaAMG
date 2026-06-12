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

<<<<<<< HEAD
Collection of projects for the "Python Programming" elective and beyond. Spans web scraping, image processing, GANs, super-resolution, and a full Pygame application.
=======
HUST 自动化学院《Python程序设计》课程作业及扩展项目。涵盖 Python 系统性自学课程体系、从零实现的深度学习框架、图像处理、GAN、YOLO 目标检测、Pygame 应用和物理实验等。总代码量超 80,000 行。
>>>>>>> 1c640f4676aa1864c3f405ddbcaa550e4d7a03a6

---

### Python 系统性自学课程 · `01_basics/` ~ `12_math_and_optimization/`

一套完整的 Python 自学路线，从基础语法到数学与优化，共 12 个模块、32 个核心脚本：

| # | 模块 | 内容 | 脚本 |
|---|---|---|---|
| 01 | **Basics** | 基础语法、数据结构、面向对象 | `01_fundamentals.py`, `02_data_structures.py`, `03_oop.py` |
| 02 | **Intermediate** | 高级函数、迭代器、异常处理 | `01_advanced_functions.py`, `02_iterators_and_errors.py` |
| 03 | **Advanced** | 并发编程、设计模式 | `01_concurrency.py`, `02_design_patterns.py` |
| 04 | **Data Science** | NumPy 基础、Pandas 基础 | `01_numpy_fundamentals.py`, `02_pandas_fundamentals.py` |
| 05 | **Machine Learning** | MLP/CNN 从零实现、PyTorch 网络、Transformer、无监督学习 | `01_mlp_from_scratch.py`, `02_cnn_from_scratch.py`, `03_pytorch_networks.py`, `04_transformer.py`, `05_unsupervised_learning.py` |
| 06 | **Reinforcement Learning** | Q-Learning、DQN、Policy Gradient、PPO、MCTS、环境工具 | `01_q_learning.py` ~ `06_envs_and_utils.py` |
| 07 | **Algorithms** | 排序搜索、图算法、动态规划、高级数据结构 | `01_sorting_searching.py` ~ `04_advanced_data_structures.py` |
| 08 | **Computer Vision** | 图像处理基础 | `01_image_processing.py` |
| 09 | **NLP** | 文本处理、词嵌入 | `01_text_processing.py`, `02_word_embeddings.py` |
| 10 | **Databases** | SQL 与 ORM | `01_sql_and_orms.py` |
| 11 | **Software Engineering** | 设计模式与测试、Web 与 API、密码学与安全 | `01_patterns_and_testing.py`, `02_web_and_api.py`, `03_cryptography_and_security.py` |
| 12 | **Math & Optimization** | 数值方法、概率与统计 | `01_numerical_methods.py`, `02_probability_and_statistics.py` |

---

### 深度学习框架 · `deep_learning_framework/`

一个**全部从零实现的完整深度学习框架**（~53,000 行纯 Python/NumPy），涵盖现代深度学习全栈。27 个模块覆盖从底层算子到 MLOps 的全流程：

| Module | Scope | Key Components |
|---|---|---|
| `layers.py` | 神经网络层 | `Linear`, `Conv2d`, `BatchNorm`, `LayerNorm`, `RNN`, `LSTM`, `GRU`, `Transformer`, `Attention`, `Embedding`, `Dropout` |
| `models.py` | 模型集合 | `MLP`, `CNN`, `ResNet`, `DenseNet`, `UNet`, `GAN`, `VAE`, `Diffusion`, `ViT`, `CLIP`, `LLaMA-style` |
| `activations.py` | 激活函数 | `ReLU`, `GELU`, `Swish`, `Mish`, `Softmax` |
| `losses.py` | 损失函数 | `MSE`, `CrossEntropy`, `Focal`, `Contrastive`, `Triplet`, `Dice` |
| `optimizers.py` | 优化器 | `SGD`, `Adam`, `AdamW`, `LAMB`, `Lion`, `RMSprop` |
| `regularization.py` | 正则化 | `Dropout`, `DropPath`, `StochasticDepth`, `LabelSmoothing`, `Mixup`, `CutMix` |
| `cv.py` | 计算机视觉 | 滤波器 (Gaussian/Median/Bilateral)、边缘检测、数据增强、IoU/NMS |
| `nlp.py` | 自然语言处理 | `Tokenizer` 族 (Whitespace/Character/BPE)、TF-IDF、序列标注、文本数据增强 |
| `rl.py` | 强化学习 | `ReplayBuffer`, `PrioritizedReplayBuffer`, N-Step、PER、NoisyNet 支持 |
| `gnn.py` | 图神经网络 | `GraphConv`, `GAT`, `GIN`, `GraphSAGE`, 消息传递框架 |
| `multimodal.py` | 多模态 | 图像-文本融合、跨模态注意力、视听对齐 |
| `timeseries.py` | 时间序列 | LSTM/Transformer 时序预测、序列分解、异常检测 |
| `tables.py` | 表格数据 | TabNet-style 注意力、特征嵌入、混合密度网络 (~27K 行) |
| `signal.py` | 信号处理 | 小波变换、FFT、滤波、时频分析 |
| `bioinformatics.py` | 生物信息 | 序列编码、接触图预测 |
| `classic_ml.py` | 经典 ML | KMeans、GMM、决策树、HMM、CRF、t-SNE、UMAP |
| `features.py` | 特征工程 | 分箱、Target Encoding、CatBoost Encoding、互信息、PCA/kPCA |
| `data_utils.py` | 数据处理 | Dataset/DataLoader、数据清洗管线、增强流水线 |
| `metrics.py` | 评估指标 | 分类/回归/排序/生成指标、统计检验 |
| `automl.py` | AutoML | 超参搜索 (Random/Grid/Bayesian/HyperBand)、NAS、模型选择、特征选择 |
| `distributed.py` | 分布式训练 | DataParallel、DistributedDataParallel、参数服务器、Ring AllReduce |
| `mlops.py` | MLOps | 实验追踪、模型注册、A/B 测试、特征存储、漂移检测、部署管线 |
| `security.py` | 安全 | 对抗样本 (FGSM/PGD/C&W)、成员推理、差分隐私、模型水印 |
| `examples.py` | 示例 | MNIST/CIFAR/IMDB 分类示例、目标检测、图像分割 |
| `utils.py` | 工具 | `save`/`load`、进度条、学习率调度器、权重初始化 |
| `weights_db.py` | 模型仓库 | 预训练权重数据库、版本管理、自动下载 (~6,565 行) |

**设计理念**：NumPy-only 后端，`Module` → `Parameter` → 自动求导，API 风格贴近 PyTorch。所有模块可独立使用，无需安装任何深度学习框架。

---

### 农田无人机喷洒农药模拟系统 · `Test3/`

Pygame 驱动的农田无人机喷洒农药交互式模拟器：

| File | Role |
|---|---|
| `main.py` | 程序入口 |
| `app.py` | `FarmDroneApp` — 主控循环，60 FPS，状态机 (welcome → login/register → main → exit) |
| `drone.py` | `Drone` 类 — 无人机运动模型与渲染 |
| `field.py` | `Field` 类 — 农田网格化建模与可视化 |
| `pesticide.py` | `PesticideManager` — 农药喷洒覆盖与消散模型 |
| `path_planning.py` | `PathPlanner` — 无人机路径规划算法 |
| `auth.py` | `AuthSystem` — 用户登录/注册（JSON 持久化） |
| `animation.py` | `AnimationSystem` — 开场/结束动画系统 |
| `utils.py` | 工具函数 |

### Pygame 全栈应用框架 · `Test3demo/`

一个完整的 Pygame 应用模板——含欢迎动画、登录/注册界面、模拟主界面和结束动画的多屏应用架构 (MVC + Screen 状态机)。`ui/screens/` 下每个屏幕独立模块化，`utils/logger.py` 统一日志。

---

### 纯 NumPy GAN · `GAN/1.py`

从零构建 **纯 NumPy** 生成对抗网络——无 PyTorch/TensorFlow：

- `Linear`, `ReLU`, `Sigmoid` 层 + 手动前向/反向传播
- Binary Cross Entropy 解析梯度 + `Sequential` 链式反向传播
- Generator: latent (4D) → hidden (16, ReLU) → 2D 输出
- Discriminator: 2D → hidden (16, ReLU) → 1D 概率 (Sigmoid)
- 2000 epoch 交替训练 G/D

目标：理解 GAN 内部机制及其与 GAIL (Generative Adversarial Imitation Learning) 的联系。真实数据分布设为均值 [5, 5] 的高斯分布，模拟专家状态-动作演示。

---

### 图像处理与超分辨率 · `pic.py/`

| Script | Function |
|---|---|
<<<<<<< HEAD
| `pic.py` | Selective color inversion — reverses only grayscale pixels (R~G~B within tolerance), leaves colored regions untouched. Uses NumPy boolean masking. |
| `res.py` | Real-ESRGAN super-resolution pipeline — RRDBNet (23 RRDB blocks, 64 features), FP16 inference, tile-based processing (256px tiles for 8GB VRAM), auto model download from GitHub releases. `enhance_image()` function with configurable outscale and tile_size. |
| `ai_upscale.py` | Alternative AI upscaling approach |
| `pro_upscale.py` / `upscale2.py` / `upscale3.py` | Upscaling variants with different model configurations |
| `realesrgan-ncnn-vulkan-20220424-windows/` | Real-ESRGAN ncnn Vulkan executable — native Windows GPU inference without Python overhead. Includes x2/x3/x4 anime and general models. |
| `check.py` | Image quality check utility |
| `tree.py` | File tree visualization |
| Physics experiment scripts | `phototube_vi_characteristic.py`, `franck_hertz_experiment.py`, `planck_constant_zero_current.py`, `saturation_photocurrent_vs_intensity.py` — experimental data plotting with matplotlib |

### Web Scraping · `demo.py`

Selenium + BeautifulSoup crawler for scraping the **ShanghaiRanking 2025 Chinese University Rankings**. Features:
=======
| `pic.py` / `pic2.py` | 选择性颜色反转——仅反转灰度像素 (R~G~B 在容差内)，NumPy 布尔掩码实现 |
| `res.py` | Real-ESRGAN 超分辨率——RRDBNet (23 RRDB blocks, 64 features)、FP16 推理、分块处理 (256px tiles, 适配 8GB VRAM)、自动下载模型。`enhance_image()` 函数支持自定义 outscale 和 tile_size |
| `pro_upscale.py` | Pro 上采样变体——多模型配置 |
| `pro_upscale2.py` | **`pro_ai_upscale_any_ratio()`** — 支持任意纵横比的 AI 上采样，批量处理 + 可选输出分辨率与模型 |
| `upscale2.py` / `upscale3.py` / `ai_upscale.py` | 不同模型配置的上采样变体 |
| `realesrgan-ncnn-vulkan-20220424-windows/` | Real-ESRGAN ncnn Vulkan 可执行文件——原生 Windows GPU 推理，零 Python 开销，含 x2/x3/x4 anime/general 模型 |
| `check.py` | 图像质量检测 |
| `tree.py` | 文件树可视化 |
| 物理实验脚本 | `光电管伏安特性曲线.py`, `弗兰克-赫兹实验.py`, `零电流法测定普朗克常数h和红限频率.py`, `饱和光电流与入射光强的关系.py` — matplotlib 实验数据可视化 |

---

### YOLOv12 目标检测 · `vision/`

YOLOv12 竞赛数据集目标检测训练：

| Project | Dataset | Model | Epochs | Hardware |
|---|---|---|---|---|
| `Elite_race_train/` | 自定义 EliteRace 检测 | yolo12n.pt | 300 | RTX 4090 D, batch 108 |
| `raicom2026_train_down/` | RaiCom 2026 俯视视角 | yolo12n.pt | 300 | RTX 4090 D |
| `raicom2026_train_up/` | RaiCom 2026 仰视视角 | yolo12n.pt | 300 | RTX 4090 D |

每轮训练包含：混淆矩阵、F1/PR 曲线、验证批次预测、训练批次样本、best/last/epoch 检查点。

### YOLO 推理 · `predict.py`

YOLOv12 批量推理脚本——配置输入文件夹 + 模型路径 → 自动创建 result 目录 → 输出带标注的图片 + 检测日志 txt。`weights/best.pt` 为训练好的模型权重。

---

### Web Scraping · `demo.py`

Selenium + BeautifulSoup 爬取**软科 2025 中国大学排行榜**：
>>>>>>> 1c640f4676aa1864c3f405ddbcaa550e4d7a03a6

- 反检测: `--disable-blink-features`, `excludeSwitches`, `navigator.webdriver` 伪造
- 自动滚动触发懒加载，最大尝试次数 + 高度变化检测
- "加载更多"按钮检测，JS 点击回退
- 中文大学名提取 (处理 img+text 混合单元格，CJK 字符正则)
- pandas DataFrame 输出含 rank/name/location/type/score 列

### PDF 图像提取 · `pdf_img.py`

从 PDF 文件中提取嵌入图像以供后续处理。

### 其他文件

| File | Description |
|---|---|
| `practice1_1.py` ~ `practice1_4.py` | Python 入门练习——数据结构、算法、文件 I/O、控制流 |
| `TEST1.py` / `TEST1-1.py` / `TEST2.py` / `test.py` / `test0.py` / `test_snippet.py` / `zz.py` | 基础编程练习与代码片段 |
| `block_diagram_step_1` | 框图步骤描述 |
| `predict.py` | YOLOv12 推理 |
| `weights/` | 模型权重 (`RealESRGAN_x4plus.pth`) |
| `IEEE-Transactions-LaTeX2e-templates-and-instructions/` | IEEE 论文 LaTeX 模板 |
| 根目录图片/PDF | 超分辨率前后对比图、物理实验数据图、椭圆偏振光雷达图、课程设计 PDF 题目 |

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

## Running — 华中大体育 GPS 跑步模拟器

>`Running/`

Campus跑步打卡自动化工具。沿华科校园路线生成模拟跑步 GPS 轨迹，完成"华中大体育"App 的课外跑步打卡。约束规则：每次 ≥3.5 km，配速 4:00-10:00 min/km。

| File | Role |
|---|---|
| `run.py` | Rich TUI 交互版 — 轨迹预览、GPX 导出、ADB 实时模拟、设备诊断 |
| `run_cli.py` | 纯命令行版 — 零第三方依赖，适合 SSH/远程/后台运行 |
| `routes/` | 校园路线 JSON 定义（GPS 坐标序列），支持自定义路线 |
| `mumu_gps.py` | MuMu 模拟器 GPS 注入方案 |
| `analyze_app.py` | App 行为分析工具 |
| `core/` | 核心轨迹生成与 GPS 模拟引擎 |

**两种使用方式**：
- **GPX 导出（推荐）**：PC 端预先生成 GPX 轨迹 → 手机 Mock GPS App 导入播放，全设备通用
- **ADB 实时模拟**：PC 通过 USB 每秒向手机注入 GPS 坐标，仅部分 ROM 支持

配速自动满足 4:00-10:00 min/km，里程自动满足 ≥3.5 km。

### Remote Deployment

| 方案 | 说明 |
|---|---|
| 本地服务器 | 旧笔记本/树莓派装 Linux + ADB，手机 USB 插上 24h 开机，SSH 远程控制 |
| Windows SSH | 管理员 PowerShell 安装 OpenSSH Server，同 WiFi 下远程操控 |

```
# GPX 导出
python run_cli.py -p 5.5 --gpx route.gpx

# 后台无人值守
nohup python3 run_cli.py -p 5.5 -l 2 -y > run.log 2>&1 &
```

---

## CSIEC — 多无人系统协同感知与规划

>`CSIEC/`

中国国际大学生创新大赛 (CSIEC) 参赛项目——多无人系统（UGV + UAV）协同感知、规划与路径规划。包含完整的项目申报书、答辩 PPT 和宇树 Go2 机器人狗二次开发指南。

| File | Content |
|---|---|
| `多无人系统协同感知与规划-项目申请书.pdf` | 正式项目申报书 |
| `多无人系统协同感知、规划（有图片）-项目.docx` | 带插图的详细项目文档 |
| `duowurenxitong_defense_20260522_212848.pptx` | 项目答辩 PPT |
| `连接宇树Go2 开发版（EDU版）的扩展坞进行二次开发.md/pdf` | Unitree Go2 robot dog SDK development guide — 物理连接、网络配置 (192.168.123.18)、SSH 登录、SDK 安装与测试 |

### AirHust · `AirHust/`

无人机/机器人碰撞避免 C++ 算法集——多种碰撞避免策略的 C/C++ 实现与变体：

| Script | Variant |
|---|---|
| `collision_avoidance.cpp` | 标准碰撞避免 |
| `collision_avoidance_alpha.cpp` / `_alpha2.cpp` | Alpha 变体 |
| `collision_avoidance_beta.cpp` | Beta 变体 |
| `collision_avoidance_plus.cpp` | 增强版 |
| `collision_avoidance_basic.cpp` | 基础精简版 |
| `collision_avoidance_mod.cpp` | 修改版 |
| `crossing_door_darknet.cpp` | 暗网穿越门检测 |
| `integrated_test.cpp` / `integrated_work.cpp` | 集成测试与综合方案 |
| `aia_collision_avoidance.cpp` | AIA (Aerial Intelligent Agent) 竞赛版 |

---

## Coursework

`人工智能导论/` · `信号与系统/` · `数据结构/` · `自动控制原理/` · `运筹学/` · `计算方法/` · `大学物理/` · `模拟电路/` · `数字电路/` · `微机原理/` · `离散数学/` · `复变函数与积分变换/` · `单片机/` · `文献检索与科技论文写作/` · `大学生社会实践/` · `数电实验/` · `模电实验/` · `电路实验/` · `物理实验复习/` · `自动控制原理实验/` · `电子技术课程设计实验/` · `马克思主义基本原理/` · `CET6/`

### 电子技术课程设计实验 · `电子技术课程设计实验/`

电子技术课程设计实验资料 — 实验总览、课程设计报告评分要求、实验数据截图。

### 马克思主义基本原理 · `马克思主义基本原理/`

马原课程学习资料 — 期末考试题型与复习提纲（2021-2026各年度）、习题集、历年真题（A/B卷含答案）。

### CET-6 · `CET6/`

大学英语六级备考 — 核心词汇整理 (`words.md`)、SARS-CoV-2 溯源独立评估阅读材料 (SAGO 报告)。

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
