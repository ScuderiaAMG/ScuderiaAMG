import os
import gymnasium as gym
import torch
import numpy as np
from atari_wrappers import make_atari
from agent import DQNAgent
from replay_buffer import ReplayBuffer

def main():
    project_root = "dqn_nature"
    os.makedirs(project_root, exist_ok=True)
    os.chdir(project_root)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    env = make_atari("BreakoutNoFrameskip-v4")
    obs, _ = env.reset()
    print("Observation shape:", obs.shape)
    agent = DQNAgent(env, device)
    replay_buffer = ReplayBuffer(1_000_000)
    
    total_frames = 50_000_000
    frames = 0
    episode = 0

    try:
        while frames < total_frames:
            obs, _ = env.reset()
            episode_reward = 0
            while True:
                action = agent.act(obs)
                next_obs, reward, done, truncated, _ = env.step(action)
                replay_buffer.push(obs, action, reward, next_obs, done)
                obs = next_obs
                episode_reward += reward
                frames += 4

                if len(replay_buffer) > 50_000:
                    batch = replay_buffer.sample(32)
                    agent.train_step(batch)

                    if frames % 10_000 == 0:
                        agent.update_target_net()

                if done or truncated or frames >= total_frames:
                    break

            episode += 1
            if episode % 100 == 0:
                print(f"Episode {episode}, Frames {frames}, Reward: {episode_reward:.2f}, Epsilon: {agent.epsilon:.3f}")

    except KeyboardInterrupt:
        print("Training interrupted.")
    finally:
        env.close()
        os.makedirs("models", exist_ok=True)
        torch.save(agent.q_net.state_dict(), "models/dqn_breakout_final.pth")
        print(" Model saved to models/dqn_breakout_final.pth")

if __name__ == "__main__":
    main()
