"""
FastAPI application for the Datacenter Env Environment.

This module creates an HTTP server that exposes the DatacenterEnvironment
over HTTP and WebSocket endpoints, compatible with EnvClient.

Endpoints:
    - POST /reset: Reset the environment
    - POST /step: Execute an action
    - GET /state: Get current environment state
    - GET /schema: Get action/observation schemas

Usage:
    # Development (with auto-reload):
    uvicorn server.app:app --reload --host 0.0.0.0 --port 8000

    # Production:
    uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 4

    # Or run directly:
    python -m server.app
"""

import uvicorn
from fastapi.responses import RedirectResponse

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:  # pragma: no cover
    raise ImportError(
        "openenv is required for the web interface. "
        "Install dependencies with:\n    uv sync\n"
    ) from e

from models import DatacenterAction, DatacenterObservation
from server.datacenter_env_environment import DatacenterEnvironment

# Create the app with web interface and README integration
app = create_app(
    DatacenterEnvironment,
    DatacenterAction,
    DatacenterObservation,
    env_name="datacenter_env",
    max_concurrent_envs=1,  # Increase to allow more concurrent WebSocket sessions
)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Redirect root URL to the interactive API docs."""
    return RedirectResponse(url="/docs")


def main(host: str = "0.0.0.0", port: int = 8000) -> None:
    """
    Entry point for direct execution via uv run or python -m.

    This function enables running the server without Docker:
        uv run --project . server
        uv run --project . server --port 8001
        python -m datacenter_env.server.app

    Args:
        host: Host address to bind to (default: "0.0.0.0")
        port: Port number to listen on (default: 8000)

    For production deployments, consider using uvicorn directly with
    multiple workers:
        uvicorn datacenter_env.server.app:app --workers 4
    """
    uvicorn.run(app, host=host, port=port)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    main()