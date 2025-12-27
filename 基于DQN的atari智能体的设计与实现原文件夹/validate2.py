import os
import gymnasium as gym
import torch
import numpy as np
import matplotlib.pyplot as plt 
from atari_wrappers import make_atari
from model import DQN

def validate_model(model_path, episodes=5):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    env = make_atari("BreakoutNoFrameskip-v4")
    env = gym.wrappers.RecordVideo(env, 'video', episode_trigger=lambda x: True)  
    obs_shape = env.observation_space.shape
    n_actions = env.action_space.n
    
    model = DQN(obs_shape, n_actions).to(device)
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=device))
        print(f"Successfully loaded model: {model_path}")
    else:
        print(f"Model file does not exist: {model_path}")
        return
    
    model.eval() 
    
    total_rewards = []
    
    for episode in range(episodes):
        obs, _ = env.reset()
        episode_reward = 0
        step = 0
        
        while True:
            obs_t = torch.tensor(obs, dtype=torch.uint8, device=device).unsqueeze(0)
            with torch.no_grad():  
                q_vals = model(obs_t)
            action = q_vals.max(1)[1].item()
            
            next_obs, reward, done, truncated, _ = env.step(action)
            episode_reward += reward
            obs = next_obs
            step += 1
            
            if done or truncated:
                print(f"Validation episode {episode+1}/{episodes}, Steps: {step}, Reward: {episode_reward:.2f}")
                total_rewards.append(episode_reward)
                break
    
    env.close()
    
    print("\nValidation Results:")
    mean_reward = np.mean(total_rewards)
    std_reward = np.std(total_rewards)
    max_reward = np.max(total_rewards)
    min_reward = np.min(total_rewards)
    print(f"Average Reward: {mean_reward:.2f} ± {std_reward:.2f}")
    print(f"Maximum Reward: {max_reward:.2f}")
    print(f"Minimum Reward: {min_reward:.2f}")

    plt.figure(figsize=(10, 6))
    plt.plot(range(1, episodes+1), total_rewards, marker='o', label='Episode Rewards')
    plt.axhline(y=mean_reward, color='r', linestyle='--', label=f'Average: {mean_reward:.2f}')
    plt.xlabel('Validation Episodes')
    plt.ylabel('Reward Value')
    plt.title('DQN Model Validation Reward Curve')
    plt.legend()
    plt.grid(alpha=0.3)
    
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/validation_rewards_final1.png', dpi=300, bbox_inches='tight')
    print("Reward plot saved to figures/validation_rewards_final1.png")
    plt.show()  

if __name__ == "__main__":
    model_path = "models/dqn_breakout_final1.pth"
    validate_model(model_path, episodes=30)
