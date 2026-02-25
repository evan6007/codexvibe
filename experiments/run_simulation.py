import sys
import os
import json
import random

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from market_env import MarketEnv
from agents import QLearningAgent

def run_experiment():
    num_agents = 2
    episodes = 500
    max_steps = 100
    env = MarketEnv(num_agents=num_agents, max_steps=max_steps)

    agents = [QLearningAgent(i) for i in range(num_agents)]

    results = {
        'episode_rewards': [],
        'avg_price': []
    }

    for episode in range(episodes):
        state = env.reset()
        episode_reward = 0

        while True:
            # Get actions from all agents
            actions_with_signals = []
            for agent in agents:
                action = agent.act(state)
                actions_with_signals.append(action)

            # Step environment
            next_state, rewards, done, info = env.step(actions_with_signals)

            # Learn
            for i, agent in enumerate(agents):
                agent.learn(state, actions_with_signals[i], rewards[i], next_state)

            state = next_state
            episode_reward += sum(rewards)

            if done:
                break

        # Log metrics
        results['episode_rewards'].append(episode_reward)
        results['avg_price'].append(state['price'])

        if (episode + 1) % 50 == 0:
            print(f"Episode {episode+1}/{episodes}, Total Reward: {episode_reward:.2f}, Price: {state['price']:.2f}")

    # Save results
    os.makedirs('analysis', exist_ok=True)
    with open('analysis/results.json', 'w') as f:
        json.dump(results, f)
    print("Results saved to analysis/results.json")

if __name__ == "__main__":
    run_experiment()
