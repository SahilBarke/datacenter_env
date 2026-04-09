# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""Datacenter Env Environment Client."""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from models import DatacenterAction, DatacenterObservation


class DatacenterEnv(EnvClient[DatacenterAction, DatacenterObservation, State]):
    """
    Client for the Datacenter Env Environment.

    This client maintains a persistent WebSocket connection to the environment server,
    enabling efficient multi-step interactions with lower latency.
    Each client instance has its own dedicated environment session on the server.

    Example:
        >>> # Connect to a running server
        >>> with DatacenterEnv(base_url="http://localhost:8000") as client:
        ...     result = client.reset()
        ...     print(result.observation.echoed_message)
        ...
        ...     result = client.step(DatacenterAction(message="Hello!"))
        ...     print(result.observation.echoed_message)

    Example with Docker:
        >>> # Automatically start container and connect
        >>> client = DatacenterEnv.from_docker_image("datacenter_env-env:latest")
        >>> try:
        ...     result = client.reset()
        ...     result = client.step(DatacenterAction(message="Test"))
        ... finally:
        ...     client.close()
    """

    def _step_payload(self, action: DatacenterAction) -> Dict:
        """
        Convert DatacenterAction to JSON payload for step message.

        Args:
            action: DatacenterAction instance

        Returns:
            Dictionary representation suitable for JSON encoding
        """
        return {
            "action_type": action.action_type,
        }

    def _parse_result(self, payload: Dict) -> StepResult[DatacenterObservation]:
        """
        Parse server response into StepResult[DatacenterObservation].

        Args:
            payload: JSON response data from server

        Returns:
            StepResult with DatacenterObservation
        """
        obs_data = payload.get("observation", {})
        observation = DatacenterObservation(
            cpu_usage=obs_data.get("cpu_usage"),
            latency=obs_data.get("latency"),
            error_rate=obs_data.get("error_rate"),
            active_servers=obs_data.get("active_servers"),
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        """
        Parse server response into State object.

        Args:
            payload: JSON response from state request

        Returns:
            State object with episode_id and step_count
        """
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 1),
        )
