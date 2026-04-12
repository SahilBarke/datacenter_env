---
title: Datacenter Optimization Environment
emoji: ⚡
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
  - reinforcement-learning
  - infrastructure
  - ai-systems
---
 
# ⚡ Datacenter Optimization Environment
 
A realistic **OpenEnv simulation environment** for datacenter operations. It models real-world infrastructure challenges like latency spikes, GPU overload, and cascading failures — designed for training AI agents to make **real-time operational decisions** such as scaling servers, rerouting traffic, and stabilizing distributed systems.
 
🌐 **Live Demo:** [sahil-barke01-datacenter-env.hf.space](https://sahil-barke01-datacenter-env.hf.space)
 
---
 
## 🧩 The Challenge
 
Modern datacenters must constantly balance:
 
| Dimension | Goal |
|---|---|
| ⚡ Performance | Keep latency low |
| 🛡️ Reliability | Minimize error rate |
| 💰 Cost | Reduce active server count |
 
Agents must learn to handle scenarios including **latency spikes**, **GPU overload**, and **cascading failures** — sometimes simultaneously.
 
---
 
## ⚙️ Action Space
 
```json
{
  "action_type": "scale_up | restart_service | reroute_traffic | do_nothing",
  "target_servers": 1
}
```
 
| Action | Effect |
|---|---|
| 📈 `scale_up` | Adds servers → reduces load, increases cost |
| 🔄 `restart_service` | Clears error state, reduces error rate |
| 🔀 `reroute_traffic` | Balances load across active servers |
| 🟢 `do_nothing` | No change (passivity has consequences) |
 
---
 
## 📊 Observation Space
 
Each `/step` call returns:
 
```json
{
  "cpu_usage": 85.2,
  "latency": 420.5,
  "error_rate": 0.12,
  "active_servers": 4,
  "reward": -3.2,
  "done": false
}
```
 
---
 
## 🧠 Reward Function
 
| Signal | Condition |
|---|---|
| ✅ Positive | Low latency, low error rate, efficient server usage |
| ❌ Negative | High latency, high error rate, excess servers, unnecessary actions |
 
---
 
## 🔁 Episode Termination
 
| Outcome | Condition |
|---|---|
| ✅ Success | `latency < 150` AND `error_rate < 0.05` |
| ❌ Timeout | Steps ≥ 20 |
 
---
 
## 🔌 API Endpoints
 
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/reset` | Reset the environment to initial state |
| `POST` | `/step` | Execute an action, get next observation |
| `GET` | `/schema` | Retrieve environment schema |
 
Interactive docs available at `/docs` once running.
 
---
 
## 🚀 Running Locally
 
**Start server**
 
```bash
uvicorn server.app:app --host 0.0.0.0 --port 8000
```
 
Then open: `http://localhost:8000/docs`
 
---
 
## 🐳 Docker Setup
 
```bash
# Build
docker build -t datacenter_env .
 
# Run
docker run -p 8000:8000 datacenter_env
```
 
---
 
## 🧱 Project Structure
 
```
datacenter_env/
├── server/
│   ├── app.py
│   └── datacenter_env_environment.py
├── models.py
├── client.py
├── demo.py
├── Dockerfile
├── openenv.yaml
└── README.md
```
 
---
 
## 🎯 Use Cases
 
- Reinforcement Learning research
- Infrastructure automation & optimization
- AI-driven DevOps / SRE training
- Autonomous system control
 
---
 
## 🔮 Future Improvements
 
- Multi-cluster simulation
- Advanced failure scenario composition
- Cost-aware reward shaping
- Pretrained baseline agents
 
---
 
## ⚙️ Tech Stack
 
Built with [OpenEnv](https://github.com/openenv) · [FastAPI](https://fastapi.tiangolo.com/) · [Docker](https://www.docker.com/) · [Hugging Face Spaces](https://huggingface.co/spaces)
