from pydantic import BaseModel
from typing import Dict


class DatacenterObservation(BaseModel):
    cpu_usage: float
    latency: float
    error_rate: float
    active_servers: int
    
    # REQUIRED by OpenEnv
    reward: float = 0.0
    done: bool = False


class DatacenterAction(BaseModel):
    action_type: str  # "scale_up", "restart_service", "reroute_traffic", "do_nothing"
    target: str = "cluster_1"  # default 


class Reward(BaseModel):
    value: float
