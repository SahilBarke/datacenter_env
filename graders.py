EPS = 1e-6

def _clamp(score: float) -> float:
    return max(EPS, min(1 - EPS, score))


# Easy Task: Fix Latency
def grade_fix_latency(env) -> float:
    score = max(0, 1 - env.latency / 500)
    return _clamp(score)


# Medium Task: Fix GPU Overload (balance CPU and error)
def grade_gpu_overload(env) -> float:
    score = 1 - (env.cpu / 100 + env.error_rate) / 2
    return _clamp(score)


# Hard Task: Fix Cascading Failure (balance latency, error, and CPU)
def grade_cascading_failure(env) -> float:
    score = 1 - (env.latency / 500 + env.error_rate + env.cpu / 100) / 3
    return _clamp(score)