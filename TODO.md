# Datacenter Env Fix Plan - Grader Score Validation (0,1 range)

## Status: [IN PROGRESS]

### 1. [PENDING] Create TODO.md
✅ Done - tracking progress here.

### 2. [PENDING] Edit graders.py
- Adjust formulas/clamp to ensure strictly (0,1).
- Test edge cases (perfect/fail states).

### 3. [PENDING] Edit server/datacenter_env_environment.py
- Add task param to reset() for multi-task.
- Use graders.get_grade(self.task)(self) in get_score().
- Fix hardcoded task='fix_latency'.

### 4. [PENDING] Edit inference.py
- Pass task to env.reset(task=TASK_NAME).
- Improve prompting if needed.

### 5. [PENDING] Test
- `uv sync`
- `uv run python inference.py`
- Verify [END] logs show scores in (0,1), no validation errors.

### 6. [PENDING] Deploy/Validate HF Space if needed

**Next: Confirm plan → Edit graders.py first (safest).**
