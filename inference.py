import asyncio
import os
import json
from typing import List, Optional
from unittest import result

from openai import OpenAI

# Import your env + action
from server.datacenter_env_environment import DatacenterEnvironment, DatacenterAction

# ================= CONFIG =================

API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
# API_KEY = os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL")
# API_BASE_URL = "https://api.groq.com/openai/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or ""

TASKS = ["fix_latency", "gpu_overload", "cascading_failure"]
BENCHMARK = "datacenter_env"
MAX_STEPS = 20
SUCCESS_SCORE_THRESHOLD = 0.6

VALID_ACTIONS = ["scale_up", "restart_service", "reroute_traffic", "do_nothing"]


# ================= LOGGING =================
def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    error_val = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


# ================= MAIN LOOP =================
def get_action(
    client: OpenAI, observation: dict, task: str, step: int, recent_actions: list
) -> str:
    if task == "fix_latency":
        goal = (
            "Reduce latency below 150 and error_rate below 0.05. "
            "scale_up is your BEST action — it reduces latency by 40 per step. "
            "Follow with reroute_traffic for additional -30 latency. "
            "Use restart_service only if error_rate exceeds 0.1. "
            "NEVER use do_nothing — latency will increase."
        )
    elif task == "gpu_overload":
        goal = (
            "Reduce CPU usage below 70% and keep error_rate low. "
            "scale_up is the PRIMARY action here — use it consistently. "
            "Only switch to restart_service if error_rate spikes above 0.1."
        )
    elif task == "cascading_failure":
        goal = (
            "System has cascading failure — ALL three metrics are critical simultaneously. "
            "You MUST use scale_up in early steps to handle the overload first. "
            "Rotate in this pattern: scale_up → reroute_traffic → restart_service → repeat. "
            "Do NOT skip scale_up — without it, the system cannot recover from cascading load."
        )
    else:
        goal = "Stabilize system"

    # Build action history string
    history_str = ""
    if recent_actions:
        history_str = f"\nLast {len(recent_actions)} actions taken: {recent_actions}"
        if len(set(recent_actions)) == 1:
            history_str += f"\n ⚠️ You have repeated '{recent_actions[0]}' {len(recent_actions)} times. Try a DIFFERENT action now."

    prompt = f"""
You are an expert datacenter SRE at step {step}/20.

Current system state:
{json.dumps(observation, indent=2)}

Goal: {goal}
{history_str}

Action effects:
- scale_up: best when CPU > 80%. Reduces CPU load and latency.
- restart_service: best when error_rate > 0.05. Directly fixes errors.
- reroute_traffic: best when latency > 150. Redistributes load.
- do_nothing: ONLY if ALL metrics are already at target.

Rules:
- If you've repeated the same action 3+ times and rewards aren't improving, switch actions.
- For cascading_failure, you likely need to rotate between scale_up, restart_service, and reroute_traffic.
- Look at the observation carefully and pick the action that targets the WORST metric.

Reply with ONLY one of: scale_up, restart_service, reroute_traffic, do_nothing
No explanation. Just the action name.
"""

    try:
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        raw = res.choices[0].message.content.strip().lower()

        for action in VALID_ACTIONS:
            if action in raw:
                return action

        print(f"[WARN] Unexpected model response: {repr(raw)}", flush=True)
        return "reroute_traffic"

    except Exception as e:
        print(f"[ERROR] API call failed: {e}", flush=True)
        return rule_based_fallback(observation, task)


def rule_based_fallback(observation: dict, task: str) -> str:
    cpu = observation.get("cpu_usage", 0)
    latency = observation.get("latency", 0)
    error_rate = observation.get("error_rate", 0)

    if error_rate > 0.05:
        return "restart_service"
    elif cpu > 80 or latency > 150:
        return "reroute_traffic"
    elif cpu > 60:
        return "scale_up"
    return "do_nothing"


async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    for TASK_NAME in TASKS:
        env = DatacenterEnvironment()
        rewards = []
        steps_taken = 0
        score = 0.0
        info = {}
        success = False
        recent_actions = []

        log_start(TASK_NAME, BENCHMARK, MODEL_NAME)

        try:
            obs = env.reset()
            done = obs.done
            obs_dict = obs.model_dump()

            for step in range(1, MAX_STEPS + 1):
                action_str = get_action(
                    client, obs_dict, TASK_NAME, step, recent_actions[-5:]
                )

                recent_actions.append(action_str)

                obs = env.step(DatacenterAction(action_type=action_str))
                reward = obs.reward
                done = obs.done

                obs_dict = obs.model_dump()

                rewards.append(reward)
                steps_taken = step

                log_step(step, action_str, reward, done, None)

                if done:
                    score = env.get_score()
                    break

            if score == 0.0:
                score = env.get_score()

            success = score >= SUCCESS_SCORE_THRESHOLD

        finally:
            log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    asyncio.run(main())
