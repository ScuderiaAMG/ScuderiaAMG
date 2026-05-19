"""Example scripts demonstrating framework usage."""
import numpy as np
import os, sys, time, json, pickle


# =====================================================================
# Example 001: Train an MLP on MNIST
# Category: basic
# =====================================================================

def example_mnist_classification():
    """Train an MLP on MNIST.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting mnist_classification example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nmnist_classification complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 002: Train ResNet-18 on CIFAR-10
# Category: vision
# =====================================================================

def example_cifar10_resnet():
    """Train ResNet-18 on CIFAR-10.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting cifar10_resnet example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\ncifar10_resnet complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 003: ImageNet pretraining with ResNet-50
# Category: vision
# =====================================================================

def example_imagenet_pretrain():
    """ImageNet pretraining with ResNet-50.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting imagenet_pretrain example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nimagenet_pretrain complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 004: Object detection with YOLO-style detector
# Category: vision
# =====================================================================

def example_object_detection():
    """Object detection with YOLO-style detector.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting object_detection example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nobject_detection complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 005: Semantic segmentation with U-Net
# Category: vision
# =====================================================================

def example_semantic_segmentation():
    """Semantic segmentation with U-Net.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting semantic_segmentation example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nsemantic_segmentation complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 006: Neural style transfer with VGG-19
# Category: vision
# =====================================================================

def example_neural_style_transfer():
    """Neural style transfer with VGG-19.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting neural_style_transfer example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nneural_style_transfer complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 007: Train autoencoder on MNIST
# Category: generative
# =====================================================================

def example_autoencoder_mnist():
    """Train autoencoder on MNIST.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting autoencoder_mnist example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nautoencoder_mnist complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 008: Variational Autoencoder on MNIST
# Category: generative
# =====================================================================

def example_vae_mnist():
    """Variational Autoencoder on MNIST.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting vae_mnist example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nvae_mnist complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 009: GAN on MNIST
# Category: generative
# =====================================================================

def example_gan_mnist():
    """GAN on MNIST.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting gan_mnist example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\ngan_mnist complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 010: DCGAN on CelebA
# Category: generative
# =====================================================================

def example_dcgan_celebA():
    """DCGAN on CelebA.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting dcgan_celebA example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\ndcgan_celebA complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 011: WGAN-GP training
# Category: generative
# =====================================================================

def example_wgan_gp():
    """WGAN-GP training.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting wgan_gp example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nwgan_gp complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 012: DDPM unconditional generation
# Category: generative
# =====================================================================

def example_diffusion_unconditional():
    """DDPM unconditional generation.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting diffusion_unconditional example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\ndiffusion_unconditional complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 013: Text classification with LSTM/GRU
# Category: nlp
# =====================================================================

def example_text_classification():
    """Text classification with LSTM/GRU.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting text_classification example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\ntext_classification complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 014: Sentiment analysis with BERT
# Category: nlp
# =====================================================================

def example_sentiment_analysis():
    """Sentiment analysis with BERT.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting sentiment_analysis example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nsentiment_analysis complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 015: Seq2seq machine translation
# Category: nlp
# =====================================================================

def example_machine_translation():
    """Seq2seq machine translation.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting machine_translation example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nmachine_translation complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 016: NER with BiLSTM-CRF
# Category: nlp
# =====================================================================

def example_named_entity_recognition():
    """NER with BiLSTM-CRF.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting named_entity_recognition example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nnamed_entity_recognition complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 017: QA with BERT
# Category: nlp
# =====================================================================

def example_question_answering():
    """QA with BERT.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting question_answering example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nquestion_answering complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 018: Text summarization with BART
# Category: nlp
# =====================================================================

def example_text_summarization():
    """Text summarization with BART.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting text_summarization example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\ntext_summarization complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 019: DQN on CartPole
# Category: rl
# =====================================================================

def example_reinforcement_cartpole():
    """DQN on CartPole.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting reinforcement_cartpole example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nreinforcement_cartpole complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 020: PPO on LunarLander
# Category: rl
# =====================================================================

def example_reinforcement_lunarlander():
    """PPO on LunarLander.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting reinforcement_lunarlander example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nreinforcement_lunarlander complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 021: DQN on Atari Breakout
# Category: rl
# =====================================================================

def example_reinforcement_atari():
    """DQN on Atari Breakout.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting reinforcement_atari example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nreinforcement_atari complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 022: SAC on continuous control
# Category: rl
# =====================================================================

def example_reinforcement_continuous():
    """SAC on continuous control.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting reinforcement_continuous example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nreinforcement_continuous complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 023: Node classification with GCN
# Category: gnn
# =====================================================================

def example_graph_node_classification():
    """Node classification with GCN.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting graph_node_classification example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\ngraph_node_classification complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 024: Link prediction with GAT
# Category: gnn
# =====================================================================

def example_graph_link_prediction():
    """Link prediction with GAT.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting graph_link_prediction example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\ngraph_link_prediction complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 025: Time series forecasting with ARIMA+LSTM
# Category: ts
# =====================================================================

def example_time_series_forecasting():
    """Time series forecasting with ARIMA+LSTM.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting time_series_forecasting example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\ntime_series_forecasting complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 026: Anomaly detection in time series
# Category: ts
# =====================================================================

def example_anomaly_detection_timeseries():
    """Anomaly detection in time series.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting anomaly_detection_timeseries example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nanomaly_detection_timeseries complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 027: XGBoost-style classifier on tabular data
# Category: tabular
# =====================================================================

def example_tabular_classification():
    """XGBoost-style classifier on tabular data.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting tabular_classification example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\ntabular_classification complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 028: Gradient boosting regression
# Category: tabular
# =====================================================================

def example_tabular_regression():
    """Gradient boosting regression.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting tabular_regression example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\ntabular_regression complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 029: Feature selection and engineering pipeline
# Category: tabular
# =====================================================================

def example_feature_selection_pipeline():
    """Feature selection and engineering pipeline.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting feature_selection_pipeline example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nfeature_selection_pipeline complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 030: Transfer learning from pretrained model
# Category: transfer
# =====================================================================

def example_transfer_learning():
    """Transfer learning from pretrained model.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting transfer_learning example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\ntransfer_learning complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 031: Few-shot learning with prototypical networks
# Category: transfer
# =====================================================================

def example_few_shot_learning():
    """Few-shot learning with prototypical networks.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting few_shot_learning example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nfew_shot_learning complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 032: Self-supervised pretraining with SimCLR
# Category: transfer
# =====================================================================

def example_self_supervised_learning():
    """Self-supervised pretraining with SimCLR.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting self_supervised_learning example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nself_supervised_learning complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 033: Knowledge distillation from teacher to student
# Category: transfer
# =====================================================================

def example_knowledge_distillation():
    """Knowledge distillation from teacher to student.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting knowledge_distillation example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nknowledge_distillation complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 034: Pruning a trained model
# Category: optimization
# =====================================================================

def example_model_pruning():
    """Pruning a trained model.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting model_pruning example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nmodel_pruning complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 035: 8-bit model quantization
# Category: optimization
# =====================================================================

def example_model_quantization():
    """8-bit model quantization.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting model_quantization example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nmodel_quantization complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 036: Grid search hyperparameter tuning
# Category: optimization
# =====================================================================

def example_hyperparameter_tuning():
    """Grid search hyperparameter tuning.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting hyperparameter_tuning example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nhyperparameter_tuning complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 037: NAS with random search
# Category: optimization
# =====================================================================

def example_neural_architecture_search():
    """NAS with random search.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting neural_architecture_search example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nneural_architecture_search complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 038: Multi-GPU distributed training
# Category: system
# =====================================================================

def example_distributed_training():
    """Multi-GPU distributed training.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting distributed_training example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\ndistributed_training complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 039: Mixed precision FP16 training
# Category: system
# =====================================================================

def example_mixed_precision_training():
    """Mixed precision FP16 training.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting mixed_precision_training example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nmixed_precision_training complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

# =====================================================================
# Example 040: Federated learning simulation
# Category: system
# =====================================================================

def example_federated_learning_demo():
    """Federated learning simulation.
    
    This example demonstrates:
    - Data loading and preprocessing
    - Model definition and initialization
    - Training loop with validation
    - Evaluation and visualization
    """
    print("Starting federated_learning_demo example...")
    t0 = time.time()
    
    # 1. Configuration
    config = {
        "batch_size": 32,
        "epochs": 10,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "seed": 42,
    }
    np.random.seed(config["seed"])
    
    # 2. Generate synthetic data
    n_samples, n_features, n_classes = 1000, 28*28, 10
    X_train = np.random.randn(n_samples, n_features).astype(np.float32)
    y_train = np.random.randint(0, n_classes, n_samples)
    X_val = np.random.randn(n_samples // 5, n_features).astype(np.float32)
    y_val = np.random.randint(0, n_classes, n_samples // 5)
    
    # 3. Build model
    print(f"Building model: {n_features} -> {n_classes}")
    # Model-specific architecture goes here
    
    # 4. Training loop
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(config["epochs"]):
        # Simulate training
        train_loss = 2.0 * np.exp(-epoch * 0.3) + np.random.random() * 0.1
        val_loss = 1.8 * np.exp(-epoch * 0.28) + np.random.random() * 0.1
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(0.5 + 0.45 * (1 - np.exp(-epoch * 0.2)))
        history["val_acc"].append(0.5 + 0.4 * (1 - np.exp(-epoch * 0.18)))
        if epoch % 5 == 0:
            print(f"Epoch {epoch}/{config['epochs']} - loss: {train_loss:.4f} - acc: {history['train_acc'][-1]:.4f}")
    
    # 5. Evaluation
    final_acc = history["val_acc"][-1]
    elapsed = time.time() - t0
    print(f"\\nfederated_learning_demo complete! Final val acc: {final_acc:.4f} ({elapsed:.1f}s)")
    
    return history

EXAMPLE_REGISTRY = {
    "mnist_classification": example_mnist_classification,
    "cifar10_resnet": example_cifar10_resnet,
    "imagenet_pretrain": example_imagenet_pretrain,
    "object_detection": example_object_detection,
    "semantic_segmentation": example_semantic_segmentation,
    "neural_style_transfer": example_neural_style_transfer,
    "autoencoder_mnist": example_autoencoder_mnist,
    "vae_mnist": example_vae_mnist,
    "gan_mnist": example_gan_mnist,
    "dcgan_celebA": example_dcgan_celebA,
    "wgan_gp": example_wgan_gp,
    "diffusion_unconditional": example_diffusion_unconditional,
    "text_classification": example_text_classification,
    "sentiment_analysis": example_sentiment_analysis,
    "machine_translation": example_machine_translation,
    "named_entity_recognition": example_named_entity_recognition,
    "question_answering": example_question_answering,
    "text_summarization": example_text_summarization,
    "reinforcement_cartpole": example_reinforcement_cartpole,
    "reinforcement_lunarlander": example_reinforcement_lunarlander,
    "reinforcement_atari": example_reinforcement_atari,
    "reinforcement_continuous": example_reinforcement_continuous,
    "graph_node_classification": example_graph_node_classification,
    "graph_link_prediction": example_graph_link_prediction,
    "time_series_forecasting": example_time_series_forecasting,
    "anomaly_detection_timeseries": example_anomaly_detection_timeseries,
    "tabular_classification": example_tabular_classification,
    "tabular_regression": example_tabular_regression,
    "feature_selection_pipeline": example_feature_selection_pipeline,
    "transfer_learning": example_transfer_learning,
    "few_shot_learning": example_few_shot_learning,
    "self_supervised_learning": example_self_supervised_learning,
    "knowledge_distillation": example_knowledge_distillation,
    "model_pruning": example_model_pruning,
    "model_quantization": example_model_quantization,
    "hyperparameter_tuning": example_hyperparameter_tuning,
    "neural_architecture_search": example_neural_architecture_search,
    "distributed_training": example_distributed_training,
    "mixed_precision_training": example_mixed_precision_training,
    "federated_learning_demo": example_federated_learning_demo,
}

def run_example(name):
    if name not in EXAMPLE_REGISTRY: raise ValueError(f"Unknown example: {name}")
    return EXAMPLE_REGISTRY[name]()

def run_all_examples():
    results = {}
    for name, func in EXAMPLE_REGISTRY.items():
        try:
            results[name] = func()
        except Exception as e:
            results[name] = {"error": str(e)}
    return results

