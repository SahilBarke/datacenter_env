import requests
import time

BASE_URL = "https://sahil-barke01-datacenter-env.hf.space"

def run_demo():
    print(f"Connecting to: {BASE_URL}")

    # RESET
    print("\nResetting Environment...")
    res = requests.post(f"{BASE_URL}/reset", json={})
    data = res.json()

    obs = data["observation"]

    print(f"CPU: {obs['cpu_usage']}, Latency: {obs['latency']}")

    total_reward = 0

    for step in range(10):
        time.sleep(0.5)

        action = {
            "action": {
                "action_type": "scale_up",
                "target_servers": 1
            }
        }

        res = requests.post(f"{BASE_URL}/step", json=action)
        data = res.json()

        obs = data["observation"]
        reward = data.get("reward", 0)

        print(f"Step {step} → Latency: {obs['latency']:.2f}, Reward: {reward:.2f}")

        total_reward += reward

    print(f"\n Total Reward: {total_reward:.2f}")


if __name__ == "__main__":
    run_demo()