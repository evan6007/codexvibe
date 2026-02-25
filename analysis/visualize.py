import json
import os

def visualize():
    with open('analysis/results.json', 'r') as f:
        data = json.load(f)

    rewards = data['episode_rewards']
    prices = data['avg_price']

    # Calculate moving average
    window_size = 50
    moving_avg_rewards = []
    for i in range(len(rewards) - window_size + 1):
        window = rewards[i:i+window_size]
        avg = sum(window) / window_size
        moving_avg_rewards.append(avg)

    print(f"Total Episodes: {len(rewards)}")
    print(f"Average Reward (Last 50): {moving_avg_rewards[-1]:.2f}")

    # ASCII Plot
    print("\nReward Trend (Moving Average 50):")
    max_val = max(moving_avg_rewards)
    min_val = min(moving_avg_rewards)
    range_val = max_val - min_val if max_val != min_val else 1

    height = 20
    normalized = [int((r - min_val) / range_val * height) for r in moving_avg_rewards]

    for y in range(height, -1, -1):
        line = ""
        for x in range(len(normalized)):
            if x % 10 == 0: # Downsample
                if normalized[x] >= y:
                    line += "*"
                else:
                    line += " "
        print(f"{min_val + (y/height)*range_val:8.1f} | {line}")

    with open('analysis/summary.txt', 'w') as f:
        f.write(f"Total Episodes: {len(rewards)}\n")
        f.write(f"Final Average Reward (Last 50): {moving_avg_rewards[-1]:.2f}\n")
        f.write(f"Max Reward: {max(rewards):.2f}\n")
        f.write(f"Min Reward: {min(rewards):.2f}\n")

if __name__ == "__main__":
    visualize()
