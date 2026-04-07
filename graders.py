"""A grader function is that  which takes the final state (or trajectory) and returns score between 0.0 to 1.0"""


# Easy Task: Fix Latency
def grade_fix_latency(env) -> float:
    # Target: low latency
    score = max(0, 1 - env.latency / 500)
    return min(score, 1)


# Medium Task: Fix GPU Overload (balance CPU and error)
def grade_gpu_overload(env) -> float:
    # Target: balanced CPU + low error
    score = 1 - (env.cpu / 100 + env.error_rate) / 2
    return max(0, min(score, 1))


# Hard Task: Fix Cascading Failure (balance latency, error, and CPU)
def grade_cascading_failure(env) -> float:
    # Hard: balance everything
    score = 1 - (env.latency / 500 + env.error_rate + env.cpu / 100) / 3
    return max(0, min(score, 1))
