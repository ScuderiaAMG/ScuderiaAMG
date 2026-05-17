# Hi there mate

Currently working on ROS system, Deep learning, Computer vision，learning in Huazhong University of Science and Technology, School of Artificial Intelligence and Automation, Automation.

*ScuderiaAMG* is a repository for private use, for courses, playing, challenge myself, and some surprises for someone. Every year it will be closed during *January June July December*.

escherichia30636@qq.com / taiyanchi157@gmail.com

Fan of MercedesAMG Petronas Formula One Team / Fan of Lewis Hamilton

**Still we rise.**

## Overview

Personal academic monorepo for a HUST AI & Automation student. Contains many independent projects across coursework, research, and personal experiments. There is no single build system or package manager for the whole repo — each subdirectory is self-contained.

## Environment

- **OS**: Windows 11, with MSYS2/MinGW64 providing Unix tools (`/mingw64/bin/`, `/usr/bin/`)
- **Python**: Anaconda at `D:/Applications/Anaconda3/python.exe`; Python 3 via `python3` on MSYS2
- **C/C++ compiler**: GCC via MinGW64 (`/mingw64/bin/gcc`, `/usr/bin/gcc`)
- **Node.js**: Available via `node`, package manager is `npm`
- **Editor**: VS Code (settings in `.vscode/settings.json`)

## Project categories

### Coursework (active)

Directories named after university subjects contain notes, assignments, and exam prep. Most are PDFs and markdown — code, when present, is in Python or C:

- `人工智能导论/` — AI course: lecture PDFs, exam prep (LaTeX), review notes (`ai.md`, `ai2.md`, `ai3.md`). Uses `pdftotext` for PDF extraction. The `复习/` subdirectory has structured review materials.
- `数据结构/` — Data structures: C programming assignments (`Q1.c`, `Q2.c`), review notes, lecture slides
- `信号与系统/`, `自动控制原理/`, `运筹学/`, `计算方法/` — engineering/math courses
- `Python-Missions/` — Python Programming elective assignments and GAN experiments

### Deep Learning / Computer Vision

- **`CSIG-VI/`** — Low-light image enhancement competition entry. Three models: `DarkvisionNet.py` (unsupervised), `RD-DualNet.py` / `RD-DualNet2.py` (supervised Retinex-DCP dual-branch). Requirements in `requirements.txt` (PyTorch 2.0.1, CUDA 11.7/11.8). Setup via `install_darkvision.sh` (creates venv, installs PyTorch with CUDA). Config in `config.py` targets RTX 4060.
- **`基于DQN的atari智能体的设计与实现原文件夹/`** — DQN Atari agent (Breakout). Uses Gymnasium, PyTorch. Entry: `main.py` (training), `validate.py` / `validate2.py` (evaluation). Model checkpoints in `models/`, videos in `video/`.
- **`horizon_haarcascade/`** — Computer vision with Haar cascades (appears to be a game-related CV project).

### Robotics (ROS + Webots)

- **`一个不知道哪来的工作空间/`** — ROS Noetic workspace. Top-level CMake at `src/CMakeLists.txt`. Packages: `bringup` (launch/config), `drone_manager` (cruise control), `fly_ctl`, `mission` (cross/endurance patterns), `cloud_recognition` (cloud/plane detection), `ring_detector`, `yolov8_ros` (YOLOv8 object detection + tracking), `web_video_server`, `usb_cam`. VS Code CMake config points here.
- **`AirHust/`** — Webots-based UAV collision avoidance (C++). Multiple iterations (`collision_avoidance*.cpp`, `integrated_work.cpp`, `slam_test.cpp`).
- **`WheelRobots/`** — Webots wheeled robot controllers and worlds.

### Competitions / Research

- **`MCM/`** — Mathematical Contest in Modeling (2025, 2026). Contains problem PDFs, solution approaches, and Python code in `2026_MCM-ICM_Project/`.
- **`CSIEC/`** — Multi-UAV collaborative perception and planning research proposal (project application documents).

### Other

- `C/` — Individual C programs (`test.c`)
- `java/` — Individual Java programs (`Main.java`, `Main.class`)
- `极限竞速：地平线5/` — Forza Horizon 5 auction house automation (compiled `.exe` + Excel car database)
- `爬呀爬/` — Video downloader scripts (`test_download*.py`)
- `build/` — Build artifacts directory
- `tmp_pdf/` — Temporary PDF processing workspace

## Build & run conventions

- **Python projects**: No unified build. Each project has its own dependencies. The CSIG-VI project uses a venv (`darkvision_env/`). Run scripts directly: `python main.py` or `python3 main.py`.
- **C programs**: Compile with GCC: `gcc -o program source.c` then `./program`
- **Java programs**: Compile with `javac Main.java` then `java Main`
- **ROS workspace**: Catkin build (`catkin_make`) from the workspace root. Targets ROS Noetic on Ubuntu.
- **Webots**: Open `.wbt` world files in Webots; controllers are compiled C++.

## Git notes

- Repository closes (likely made private) during January, June, July, December each year.
- Git user: LEGION-83DG / LENOVO-83BF
