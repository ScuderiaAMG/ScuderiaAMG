import os
import gymnasium as gym
import torch
import numpy as np
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
        print(f"成功加载模型: {model_path}")
    else:
        print(f"模型文件不存在: {model_path}")
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
                print(f"验证回合 {episode+1}/{episodes}, 步数: {step}, 奖励: {episode_reward:.2f}")
                total_rewards.append(episode_reward)
                break
    
    env.close()
    
    print("\n验证结果:")
    print(f"平均奖励: {np.mean(total_rewards):.2f} ± {np.std(total_rewards):.2f}")
    print(f"最大奖励: {np.max(total_rewards):.2f}")
    print(f"最小奖励: {np.min(total_rewards):.2f}")

if __name__ == "__main__":
    model_path = "models/dqn_breakout_best.pth"
    validate_model(model_path, episodes=30)
