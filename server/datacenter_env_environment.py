from typing import Tuple, Dict
import random

from models import DatacenterObservation, DatacenterAction

from graders import grade_fix_latency, grade_gpu_overload, grade_cascading_failure


class DatacenterEnvironment:
    def __init__(self):
        self.reset()

    def reset(self, seed: int = None, episode_id: str = None) -> DatacenterObservation:

        if seed is not None:
            random.seed(seed)

        # default task
        self.task = "fix_latency"
        # self.task = task

        # Initial state (unstable)
        self.cpu = random.randint(70, 95)
        self.latency = random.randint(300, 600)
        self.error_rate = random.uniform(0.05, 0.2)
        self.active_servers = 3
        self.steps = 0

        return self._get_obs()

    def step(self, action: DatacenterAction) -> DatacenterObservation:

        self.prev_latency = self.latency
        self.prev_error_rate = self.error_rate
        self.steps += 1

        act = action.action_type

        # Apply action effects
        if act == "scale_up":
            self.active_servers += 1
            self.cpu -= 10
            self.latency -= 40

        elif act == "restart_service":
            self.error_rate -= 0.05
            self.latency -= 20

        elif act == "reroute_traffic":
            self.cpu -= 5
            self.latency -= 30

        elif act == "do_nothing":
            self.latency += 20
            self.error_rate += 0.02

        # Task-specific dynamics
        if self.task == "fix_latency":
            self.latency += 5  # mild pressure — forces agent to keep acting
        elif self.task == "gpu_overload":
            self.cpu += 5  # simulate heavy load
        elif self.task == "cascading_failure":
            self.error_rate += 0.03
            self.latency += 15

        # Add randomness (real-world simulation)
        self.cpu += random.uniform(-2, 2)
        self.latency += random.uniform(-10, 10)

        # Clamp values
        self.cpu = max(0, min(100, self.cpu))
        self.error_rate = max(0, min(1, self.error_rate))

        reward = self._compute_reward(action.action_type)
        done = self._check_done()

        return self._get_obs(reward, done)

    @property
    def state(self) -> DatacenterObservation:
        return self._get_obs()

    def _get_obs(self, reward=0.0, done=False) -> DatacenterObservation:
        return DatacenterObservation(
            cpu_usage=self.cpu,
            latency=self.latency,
            error_rate=self.error_rate,
            active_servers=self.active_servers,
            reward=reward,  # will be computed in step()
            done=done,  # will be computed in step()
        )

    # 3. Task-aware reward in _compute_reward

    def _compute_reward(self, act: str) -> float:
        reward = 0

        if self.task == "fix_latency":
            reward -= 0.00008 * (self.latency**2)  # stronger latency penalty
            reward -= 3 * (self.error_rate**2)  # lighter error weight
            reward += 0.2 * (
                self.prev_latency - self.latency
            )  # improvement bonus
            reward += 5 * (self.prev_error_rate - self.error_rate)

            # Reduce scale_up penalty 
            if act == "scale_up":
                reward -= 0.5  
            elif act == "do_nothing":
                reward -= 2.0 

            # SLA thresholds
            if self.latency > 400:
                reward -= 5
            if self.latency > 250:
                reward -= 2  
            if self.error_rate > 0.15:
                reward -= 5

            # Success bonus
            if self.latency < 150 and self.error_rate < 0.05:
                reward += 50

            reward -= 0.3  # time penalty
            reward -= 0.1 * self.active_servers

        else:
            reward -= 0.00005 * (self.latency**2)
            reward -= 8 * (self.error_rate**2)
            reward -= 0.1 * self.active_servers
            reward += 0.1 * (self.prev_latency - self.latency)
            reward += 15 * (self.prev_error_rate - self.error_rate)
            reward -= 0.01 * abs(self.latency - self.prev_latency)
            if act == "scale_up":
                reward -= 1.5
            if self.latency > 400:
                reward -= 5
            if self.error_rate > 0.15:
                reward -= 10
            if self.latency < 150 and self.error_rate < 0.05:
                reward += 50
            reward -= 0.3

        return reward

    def _check_done(self) -> bool:
        if self.latency < 150 and self.error_rate < 0.05:
            return True
        if self.steps >= 20:
            return True
        return False

    def get_score(self) -> float:
        EPS = 1e-6
        
        def clamp(score):
            return max(EPS, min(1 - EPS, score))
        
        if self.task == "fix_latency":
            if self.latency < 150 and self.error_rate < 0.05:
                return 1 - EPS  

            latency_score = max(0, min(1, (600 - self.latency) / (600 - 150)))
            error_score = max(0, min(1, 1 - self.error_rate / 0.2))
            return clamp(0.7 * latency_score + 0.3 * error_score)

        elif self.task == "gpu_overload":
            return clamp(max(0, min(1, 1 - (self.cpu / 150 + self.error_rate * 1.2))))

        elif self.task == "cascading_failure":
            penalty = (self.latency / 700) + (self.cpu / 150) + (self.error_rate * 1.5)
            return clamp(max(0, min(1, 1 - penalty / 2.5)))

        return EPS  # default minimal score

    async def reset_async(self, seed: int = None, episode_id: str = None):
        return self.reset(seed=seed, episode_id=episode_id)

    async def step_async(self, action):
        return self.step(action)

    def close(self):
        # cleanup if needed
        pass
